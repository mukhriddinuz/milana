"""
Milana Textile — Gemini AI Chatbot (RAG arxitektura).
Mijozlarga kiyim tanlashda yordam beruvchi sun'iy intellekt yordamchi.

RAG = Retrieval-Augmented Generation:
1. Foydalanuvchi xabaridan jins/narx ajratiladi (sodda regex)
2. Bazadan mos mahsulotlar qidiriladi (max 20 ta)
3. Faqat topilganlar Gemini ga yuboriladi
4. Gemini o'zi aqlli — javobni u shakllantiradi

Token sarfi: ~2000 token / so'rov (5000+ mahsulotda ham)
"""
import json
import time
import re
import google.generativeai as genai
from django.conf import settings
from django.db.models import Q
from .models import Product, Category
from .notifications import notify_admin_error


# =============================================
# GEMINI KONFIGURATSIYASI
# =============================================

_gemini_configured = False
MAX_SEARCH_RESULTS = 20


def _ensure_configured():
    """Gemini API ni faqat bir marta configure qilish"""
    global _gemini_configured
    if not _gemini_configured:
        api_key = settings.GEMINI_API_KEY
        if not api_key:
            raise ValueError("GEMINI_API_KEY sozlamasi topilmadi!")
        genai.configure(api_key=api_key)
        _gemini_configured = True


def _get_model(system_instruction=None):
    """Gemini modelini yaratish"""
    _ensure_configured()
    return genai.GenerativeModel(
        model_name='gemini-2.5-flash',
        generation_config={
            'temperature': 0.7,
            'top_p': 0.9,
            'max_output_tokens': 1500,
        },
        system_instruction=system_instruction,
        safety_settings=[
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_MEDIUM_AND_ABOVE"},
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
        ]
    )


# =============================================
# SODDA VA ISHONCHLI QIDIRUV
# =============================================
# Stop words, stemmer kerak emas.
# Faqat 2 ta ishonchli filtr: JINS va NARX.
# Qolganini Gemini o'zi hal qiladi.

# Jinsni aniqlash uchun kalit so'zlar (3 tilda)
_GENDER_MAP = {
    'erkak':    ['erkak', 'erkaklar', 'мужской', 'мужская', 'мужские', 'мужчин',
                 'men', 'man', 'male', 'boy', 'yigit'],
    'ayol':     ['ayol', 'ayollar', 'женский', 'женская', 'женские', 'женщин',
                 'women', 'woman', 'female', 'girl', 'lady', 'qiz', 'xotin'],
    'bola':     ['bola', 'bolalar', 'детский', 'детская', 'детские', 'ребенок',
                 'дети', 'kids', 'kid', 'child', 'children', 'kichkina'],
}


def _detect_gender(text):
    """Xabardan jinsni aniqlash (sodda, ishonchli)"""
    text_lower = text.lower()
    for gender, keywords in _GENDER_MAP.items():
        for kw in keywords:
            if kw in text_lower:
                return gender
    return None


def _detect_price_range(text):
    """Xabardan narx oralig'ini aniqlash.

    Misol:
        '130 000 so'm atrofidagi'  → (104000, 156000)
        '100000 dan 200000 gacha'  → (100000, 200000)
        'arzon kiyim'              → (None, None, is_cheap=True)
    """
    text_lower = text.lower()
    min_price = None
    max_price = None
    is_cheap = False
    is_expensive = False

    # Arzon/qimmat
    cheap_words = ['arzon', 'дешев', 'cheap', 'бюджет', 'budget', 'hamyon']
    expensive_words = ['qimmat', 'дорог', 'expensive', 'premium', 'lux']
    for w in cheap_words:
        if w in text_lower:
            is_cheap = True
    for w in expensive_words:
        if w in text_lower:
            is_expensive = True

    # Raqamlarni topish
    price_numbers = re.findall(r'(\d[\d\s]*\d)', text)
    if not price_numbers:
        price_numbers = re.findall(r'(\d+)', text)

    prices = []
    for pn in price_numbers:
        try:
            p = int(pn.replace(' ', ''))
            if p >= 1000:
                prices.append(p)
        except ValueError:
            pass

    if len(prices) >= 2:
        min_price = min(prices)
        max_price = max(prices)
    elif len(prices) == 1:
        p = prices[0]
        if is_cheap:
            max_price = p
        elif is_expensive:
            min_price = p
        else:
            # Bitta narx berilganda ±20% oraliq
            margin = int(p * 0.20)
            min_price = p - margin
            max_price = p + margin

    return min_price, max_price, is_cheap, is_expensive


def _search_products(message_text, lang='uz'):
    """Bazadan mahsulotlarni qidirish.

    Strategiya:
    1. Jins va narx bo'yicha filtr (ishonchli)
    2. Xabardagi so'zlar bilan mahsulot nomlaridan qidirish
    3. Topilmasa → filtr bilan fallback
    4. Filtr ham bo'sh bo'lsa → eng yangi mahsulotlar
    """
    # 1. Asosiy filtrlarni aniqlash
    gender = _detect_gender(message_text)
    min_price, max_price, is_cheap, is_expensive = _detect_price_range(message_text)

    # 2. Bazadan query
    qs = Product.objects.filter(
        in_stock=True
    ).select_related('category').prefetch_related('colors', 'sizes')

    if gender:
        qs = qs.filter(category__gender=gender)
    if min_price:
        qs = qs.filter(price__gte=min_price)
    if max_price:
        qs = qs.filter(price__lte=max_price)

    # Tartiblash
    if is_cheap:
        qs = qs.order_by('price')
    elif is_expensive:
        qs = qs.order_by('-price')
    elif min_price or max_price:
        qs = qs.order_by('price')

    # 3. So'zlar bilan qidirish (har qanday tilda)
    # Faqat 3+ belgili so'zlarni olamiz (qisqalari ortiqcha shovqin)
    words = re.findall(r'[a-zA-Zа-яА-ЯёЁ\u0027\u2018\u2019]+', message_text.lower())
    search_words = [w for w in words if len(w) >= 3]

    if search_words:
        word_q = Q()
        for w in search_words:
            word_q |= (
                Q(name_uz__icontains=w) |
                Q(name_ru__icontains=w) |
                Q(name_en__icontains=w) |
                Q(model_name__icontains=w) |
                Q(variant__icontains=w) |
                Q(category__name_uz__icontains=w) |
                Q(category__name_ru__icontains=w) |
                Q(category__name_en__icontains=w) |
                Q(colors__name_uz__icontains=w) |
                Q(colors__name_ru__icontains=w)
            )
        keyword_results = qs.filter(word_q).distinct()
        if keyword_results.exists():
            return keyword_results[:MAX_SEARCH_RESULTS]

    # 4. Fallback: so'zlar bilan topilmadi → filtr natijalari
    if qs.exists():
        return qs[:MAX_SEARCH_RESULTS]

    # 5. Hech narsa topilmadi → eng yangi mahsulotlardan ko'rsatish
    return Product.objects.filter(
        in_stock=True
    ).select_related('category').prefetch_related(
        'colors', 'sizes'
    ).order_by('-created_at')[:MAX_SEARCH_RESULTS]


def _format_products_for_ai(products, lang='uz'):
    """Topilgan mahsulotlarni AI uchun ixcham JSON ga aylantirish"""
    result = []
    for p in products:
        colors = [c.get_name(lang) for c in p.colors.all()]
        sizes = [s.name for s in p.sizes.all()]
        item = {
            'id': p.id,
            'name': p.get_name(lang),
            'cat': p.category.get_name(lang),
            'gender': p.category.get_gender_display(),
            'price': int(p.price),
        }
        if colors:
            item['colors'] = colors
        if sizes:
            item['sizes'] = sizes
        if p.model_name:
            item['model'] = p.model_name
        if p.variant:
            item['variant'] = p.variant
        if p.box_price:
            item['box_price'] = int(p.box_price)
            item['box_qty'] = p.box_quantity
        desc = p.get_description(lang)
        if desc:
            item['desc'] = desc[:80]
        result.append(item)
    return result


# =============================================
# KATEGORIYALAR KESHI
# =============================================

_categories_cache = {'data': None, 'time': 0}
CATEGORIES_TTL = 600


def _get_cached_categories():
    """Kategoriyalar ro'yxatini kesh bilan olish"""
    now = time.time()
    if _categories_cache['data'] is None or (now - _categories_cache['time']) > CATEGORIES_TTL:
        cats = Category.objects.filter(is_active=True)
        info = []
        for c in cats:
            count = c.products.filter(in_stock=True).count()
            info.append({
                'name': c.name_uz,
                'gender': c.get_gender_display(),
                'count': count,
            })
        _categories_cache['data'] = info
        _categories_cache['time'] = now
    return _categories_cache['data']


# =============================================
# SYSTEM PROMPT (yengil)
# =============================================

def _build_system_prompt(lang='uz'):
    """AI chatbot uchun system prompt.

    Mahsulotlar bu yerda YO'Q — har so'rovda alohida yuboriladi.
    """
    categories = _get_cached_categories()

    lang_instruction = {
        'uz': "Foydalanuvchi bilan O'ZBEK TILIDA muloqot qil.",
        'ru': "Общайся с пользователем на РУССКОМ ЯЗЫКЕ.",
        'en': "Communicate with the user in ENGLISH.",
    }

    return f"""Sen "Milana Textile" onlayn kiyim do'konining AI yordamchisisan.

VAZIFALARYING:
1. Mijozlarga kiyim tanlashda yordam berish
2. Berilgan mahsulotlar ro'yxatidan mos variantlarni tavsiya qilish
3. Narxlar, o'lchamlar, ranglar haqida javob berish

{lang_instruction.get(lang, lang_instruction['uz'])}

QOIDALAR:
- Faqat KIYIM sohasida javob ber.
- Kiyim bilan bog'liq bo'lmagan savolga "Men faqat kiyim sohasida yordam bera olaman" de.
- FAQAT senga berilgan mahsulotlar ro'yxatidan foydalaning. O'zingdan to'qib chiqarma.
- Agar ro'yxatda mijozga mos narsa bo'lmasa, buni ayt va boshqa turdagi mahsulotlarni so'rashni taklif qil.
- Narxlarni so'mda ko'rsat (masalan: 150 000 so'm).
- Mahsulot ID raqamini ko'rsat (#ID).
- Javobni qisqa va aniq ber.
- Telegram HTML formatda javob ber (<b>, <i>, <code>).

KATEGORIYALAR:
{json.dumps(categories, ensure_ascii=False, separators=(',', ':'))}

JAVOB FORMATI:
Siz qisqa va chiroyli javob yozing. Mahsulotlarning narxi va qisqacha xarakteristikasini ayting.
Muhim: Har bir tavsiya qilgan mahsulotingiz yonida ID raqamini ko'rsating (masalan: #123).

Oxirida shunga o'xshash xabar qoldiring: "Batafsil ko'rish va buyurtma berish uchun quyidagi tugmalardan birini tanlang 👇"
"""


# =============================================
# SESSIYALAR VA RETRY
# =============================================

_chat_sessions = {}
SESSION_TTL = 1800
MAX_RETRIES = 3
BASE_DELAY = 2


def _cleanup_old_sessions():
    """Eskirgan sessiyalarni tozalash"""
    now = time.time()
    expired = [k for k, v in _chat_sessions.items() if (now - v['time']) > SESSION_TTL]
    for k in expired:
        del _chat_sessions[k]


def _send_with_retry(chat, message_text):
    """429 xatolik bo'lsa qayta urinish"""
    last_error = None
    for attempt in range(MAX_RETRIES):
        try:
            return chat.send_message(message_text)
        except Exception as e:
            last_error = e
            error_str = str(e).lower()
            if '429' in error_str or ('resource' in error_str and 'exhausted' in error_str):
                delay = BASE_DELAY * (2 ** attempt)
                print(f"[CHATBOT] 429 rate limit, {delay}s kutilmoqda... ({attempt + 1}/{MAX_RETRIES})")
                time.sleep(delay)
                continue
            raise
    raise last_error


# =============================================
# ASOSIY FUNKSIYALAR
# =============================================

def get_ai_response(user_id, message_text, lang='uz'):
    """Foydalanuvchi xabariga Gemini orqali javob qaytarish (RAG).

    Returns:
        dict: {
            'text': str,           # AI javobi (HTML)
            'product_ids': list,   # Topilgan mahsulot ID lari
        }
    """
    try:
        _cleanup_old_sessions()
        session_key = f"{user_id}_{lang}"

        if session_key not in _chat_sessions:
            system_prompt = _build_system_prompt(lang)
            model = _get_model(system_instruction=system_prompt)
            chat = model.start_chat(history=[])
            _chat_sessions[session_key] = {'chat': chat, 'time': time.time()}
        else:
            _chat_sessions[session_key]['time'] = time.time()

        chat = _chat_sessions[session_key]['chat']

        # RAG: Bazadan qidirish
        products = _search_products(message_text, lang)
        products_data = _format_products_for_ai(products, lang)

        print(f"[CHATBOT] user={user_id} | lang={lang} | context_products={len(products_data)}")

        # Kontekst bilan xabarni yuborish
        if products_data:
            context = (
                f"Mijoz: {message_text}\n\n"
                f"Bazadan topilgan mahsulotlar ({len(products_data)} ta):\n"
                f"{json.dumps(products_data, ensure_ascii=False, separators=(',', ':'))}"
            )
        else:
            context = (
                f"Mijoz: {message_text}\n\n"
                f"Bazada hech qanday mahsulot topilmadi."
            )

        response = _send_with_retry(chat, context)

        # AI tavsiya qilgan mahsulotlarning ID larini ajratib olish
        mentioned_ids = []
        for pid_str in re.findall(r'#(\d+)', response.text):
            try:
                pid = int(pid_str)
                # Faqat kontekstda bor bo'lgan ID larni olamiz (AI to'qib chiqarmasligi uchun)
                if any(p['id'] == pid for p in products_data):
                    if pid not in mentioned_ids:
                        mentioned_ids.append(pid)
            except ValueError:
                pass

        return {'text': response.text, 'product_ids': mentioned_ids}

    except Exception as e:
        print(f"[CHATBOT ERROR] {e}")
        session_key = f"{user_id}_{lang}"
        if session_key in _chat_sessions:
            del _chat_sessions[session_key]

        notify_admin_error(
            title='AI Chatbot xatoligi',
            error=e,
            extra=f"user_id={user_id}\nlang={lang}\nmessage={message_text}"
        )

        error_str = str(e).lower()
        if '429' in error_str or 'resource' in error_str:
            msg = {
                'uz': "Hozirda so'rovlar ko'p. 1 daqiqadan keyin qayta urinib ko'ring.",
                'ru': "Слишком много запросов. Подождите 1 минуту.",
                'en': "Too many requests. Please wait 1 minute.",
            }.get(lang, "Hozirda so'rovlar ko'p. 1 daqiqadan keyin qayta urinib ko'ring.")
            return {'text': msg, 'product_ids': []}

        msg = {
            'uz': "Kechirasiz, xatolik yuz berdi. Qaytadan yozing.",
            'ru': "Извините, произошла ошибка. Напишите снова.",
            'en': "Sorry, an error occurred. Please try again.",
        }.get(lang, "Kechirasiz, xatolik yuz berdi. Qaytadan yozing.")
        return {'text': msg, 'product_ids': []}


def reset_chat_session(user_id, lang='uz'):
    """Sessiyani tozalash"""
    session_key = f"{user_id}_{lang}"
    if session_key in _chat_sessions:
        del _chat_sessions[session_key]


# =============================================
# REST API
# =============================================

def get_ai_response_api(message_text, lang='uz', session_id=None):
    """REST API orqali chatbot javobini olish"""
    if not session_id:
        session_id = 'api_default'

    result = get_ai_response(
        user_id=f"api_{session_id}",
        message_text=message_text,
        lang=lang
    )

    return {
        'response': result['text'],
        'products': result['product_ids'],
        'session_id': session_id,
    }
