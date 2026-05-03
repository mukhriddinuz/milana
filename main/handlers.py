"""
Milana Textile Bot — Barcha handlerlar.
Faza 1-3: Start, Til, Menyu, Katalog, Savat, Buyurtma
"""
import math
from telebot import types
from .bot import bot
from .models import (
    BotUser, Category, Product, ProductColor, ProductSize,
    Cart, CartItem, Order, OrderItem
)
from .notifications import notify_admin_error
from .translations import get_text
from .utils import get_or_create_user, get_user_lang, get_cart, t, format_price
from . import keyboards as kb

PRODUCTS_PER_PAGE = 5

# Vaqtinchalik ma'lumotlar (order jarayoni)
user_states = {}

# AI chatbot rejimidagi foydalanuvchilar
ai_mode_users = set()


# =============================================
# /start KOMANDASI
# =============================================
@bot.message_handler(commands=['start'])
def handle_start(message):
    if message.chat.type != 'private':
        return
    bot_user = get_or_create_user(message)

    # Deep link tekshirish
    args = message.text.split()
    if len(args) > 1 and args[1].startswith('product_'):
        try:
            pid = int(args[1].replace('product_', ''))
            product = Product.objects.get(id=pid, in_stock=True)
            show_product_detail(message.chat.id, product, bot_user.language)
            return
        except (ValueError, Product.DoesNotExist):
            pass

    bot.send_message(
        message.chat.id,
        get_text('welcome', bot_user.language),
        parse_mode='HTML',
        reply_markup=kb.language_keyboard()
    )


# =============================================
# TIL TANLASH
# =============================================
@bot.callback_query_handler(func=lambda c: c.data.startswith('lang_'))
def handle_language(call):
    lang = call.data.split('_')[1]
    BotUser.objects.filter(telegram_id=call.from_user.id).update(language=lang)

    bot.answer_callback_query(call.id, get_text('language_selected', lang))
    bot.edit_message_text(
        get_text('language_selected', lang),
        call.message.chat.id, call.message.message_id, parse_mode='HTML'
    )
    bot.send_message(
        call.message.chat.id,
        get_text('main_menu', lang),
        parse_mode='HTML',
        reply_markup=kb.main_menu_keyboard(lang)
    )


@bot.callback_query_handler(func=lambda c: c.data == 'change_lang')
def handle_change_lang(call):
    bot.edit_message_text(
        get_text('select_language', get_user_lang(call.from_user.id)),
        call.message.chat.id, call.message.message_id,
        reply_markup=kb.language_keyboard()
    )


# =============================================
# ASOSIY MENYU — ReplyKeyboard handlerlar
# =============================================
@bot.message_handler(func=lambda m: m.chat.type == 'private' and m.content_type == 'text')
def handle_menu_text(message):
    lang = get_user_lang(message.from_user.id)
    text = message.text
    uid = message.from_user.id

    # Bo'limlar
    if text == get_text('btn_men', lang):
        ai_mode_users.discard(uid)
        show_gender_categories(message.chat.id, 'erkak', lang)
    elif text == get_text('btn_women', lang):
        ai_mode_users.discard(uid)
        show_gender_categories(message.chat.id, 'ayol', lang)
    elif text == get_text('btn_kids', lang):
        ai_mode_users.discard(uid)
        show_gender_categories(message.chat.id, 'bola', lang)
    elif text == get_text('btn_cart', lang):
        ai_mode_users.discard(uid)
        show_cart(message.chat.id, message.from_user.id, lang)
    elif text == get_text('btn_my_orders', lang):
        ai_mode_users.discard(uid)
        show_orders(message.chat.id, message.from_user.id, lang)
    elif text == get_text('btn_about', lang):
        ai_mode_users.discard(uid)
        bot.send_message(message.chat.id, get_text('about_text', lang), parse_mode='HTML')
    elif text == get_text('btn_settings', lang):
        ai_mode_users.discard(uid)
        bot.send_message(message.chat.id, get_text('settings_menu', lang),
                         parse_mode='HTML', reply_markup=kb.settings_keyboard(lang))
    elif text == get_text('btn_ai', lang):
        # AI chatbot rejimiga kirish
        ai_mode_users.add(uid)
        if uid in user_states:
            del user_states[uid]
        bot.send_message(message.chat.id, get_text('ai_welcome', lang),
                         parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))
    elif text == get_text('btn_back_to_menu', lang):
        # Order jarayonidan yoki AI rejimidan qaytish
        ai_mode_users.discard(uid)
        if uid in user_states:
            del user_states[uid]
        # AI sessiyasini tozalash
        try:
            from .chatbot import reset_chat_session
            reset_chat_session(uid, lang)
        except Exception:
            pass
        bot.send_message(message.chat.id, get_text('main_menu', lang),
                         parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))
    else:
        # AI rejimida bo'lsa — Gemini ga yuborish
        if uid in ai_mode_users:
            handle_ai_message(message, lang)
            return
        # Order jarayonidagi matn
        if uid in user_states:
            state = user_states[uid]
            if state.get('step') == 'phone':
                handle_order_phone_text(message, lang)
                return
            elif state.get('step') == 'address':
                handle_order_address(message, lang)
                return
        # Noma'lum matn
        bot.send_message(message.chat.id, get_text('main_menu', lang),
                         parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))


# =============================================
# KONTAKT HANDLER
# =============================================
@bot.message_handler(content_types=['contact'])
def handle_contact(message):
    if message.chat.type != 'private':
        return
    lang = get_user_lang(message.from_user.id)
    uid = message.from_user.id
    if uid in user_states and user_states[uid].get('step') == 'phone':
        phone = message.contact.phone_number
        user_states[uid]['phone'] = phone
        user_states[uid]['step'] = 'address'
        bot.send_message(message.chat.id, get_text('order_address', lang),
                         parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))


# =============================================
# GENDER -> KATEGORIYALAR
# =============================================
def show_gender_categories(chat_id, gender, lang):
    cats = Category.objects.filter(gender=gender, is_active=True)
    if not cats.exists():
        bot.send_message(chat_id, get_text('no_categories', lang))
        return
    bot.send_message(chat_id, get_text('select_category', lang),
                     parse_mode='HTML', reply_markup=kb.categories_keyboard(cats, lang))


@bot.callback_query_handler(func=lambda c: c.data.startswith('gender_'))
def handle_gender_back(call):
    gender = call.data.split('_')[1]
    lang = get_user_lang(call.from_user.id)
    cats = Category.objects.filter(gender=gender, is_active=True)
    if not cats.exists():
        bot.answer_callback_query(call.id, get_text('no_categories', lang))
        return
    bot.edit_message_text(
        get_text('select_category', lang),
        call.message.chat.id, call.message.message_id,
        parse_mode='HTML', reply_markup=kb.categories_keyboard(cats, lang)
    )


# =============================================
# KATEGORIYA -> MAHSULOTLAR
# =============================================
@bot.callback_query_handler(func=lambda c: c.data.startswith('cat_'))
def handle_category(call):
    cat_id = int(call.data.split('_')[1])
    lang = get_user_lang(call.from_user.id)
    show_products_page(call.message.chat.id, call.message.message_id, cat_id, 1, lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('ppage_'))
def handle_products_page(call):
    parts = call.data.split('_')
    cat_id = int(parts[1])
    page = int(parts[2])
    lang = get_user_lang(call.from_user.id)
    show_products_page(call.message.chat.id, call.message.message_id, cat_id, page, lang)


def show_products_page(chat_id, message_id, cat_id, page, lang):
    products = Product.objects.filter(category_id=cat_id, in_stock=True)
    total = products.count()
    if total == 0:
        try:
            bot.edit_message_text(get_text('no_products', lang),
                                 chat_id, message_id, parse_mode='HTML')
        except Exception:
            bot.send_message(chat_id, get_text('no_products', lang))
        return
    total_pages = math.ceil(total / PRODUCTS_PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * PRODUCTS_PER_PAGE
    page_products = products[start:start + PRODUCTS_PER_PAGE]
    text = get_text('select_category', lang) + "\n" + get_text('page_info', lang).format(
        current=page, total=total_pages)
    try:
        bot.edit_message_text(text, chat_id, message_id, parse_mode='HTML',
                              reply_markup=kb.products_keyboard(page_products, page, total_pages, cat_id, lang))
    except Exception:
        bot.send_message(chat_id, text, parse_mode='HTML',
                         reply_markup=kb.products_keyboard(page_products, page, total_pages, cat_id, lang))


# =============================================
# MAHSULOT KARTASI
# =============================================
@bot.callback_query_handler(func=lambda c: c.data.startswith('prod_'))
def handle_product(call):
    pid = int(call.data.split('_')[1])
    lang = get_user_lang(call.from_user.id)
    try:
        product = Product.objects.get(id=pid)
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    # Avvalgi xabarni o'chirish
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    show_product_detail(call.message.chat.id, product, lang)


def show_product_detail(chat_id, product, lang):
    """Mahsulot kartasini ko'rsatish — rang/o'lcham/son tanlash bilan"""
    colors = product.colors.all()
    sizes = product.sizes.all()
    color_names = ", ".join([f"{c.emoji} {c.get_name(lang)}" for c in colors]) or "—"
    size_names = ", ".join([s.name for s in sizes]) or "—"

    model_text = get_text('model_label', lang).format(model=product.model_name) if product.model_name else ""
    variant_text = get_text('variant_label', lang).format(variant=product.variant) if product.variant else ""
    box_text = ""
    if product.box_price:
        box_text = get_text('box_price_label', lang).format(
            box_price=format_price(product.box_price), box_qty=product.box_quantity)

    text = get_text('product_card', lang).format(
        name=product.get_name(lang),
        model=model_text,
        variant=variant_text,
        price=format_price(product.price),
        box_price=box_text,
        sizes=size_names,
        colors=color_names,
        description=product.get_description(lang) or "—"
    )

    # Boshlang'ich tanlash holati
    initial_color = colors[0].id if colors else 0
    initial_size = sizes[0].id if sizes else 0
    selector_kb = kb.product_selector_keyboard(
        product, color_id=initial_color, size_id=initial_size,
        ptype='d', qty=1, lang=lang
    )

    media_group = []
    
    if product.main_image:
        try:
            media_group.append(types.InputMediaPhoto(open(product.main_image.path, 'rb'), caption=text, parse_mode='HTML'))
        except Exception:
            pass
            
    for img in product.images.all():
        try:
            if not media_group:
                media_group.append(types.InputMediaPhoto(open(img.image.path, 'rb'), caption=text, parse_mode='HTML'))
            else:
                media_group.append(types.InputMediaPhoto(open(img.image.path, 'rb')))
        except Exception:
            pass

    if len(media_group) > 1:
        try:
            bot.send_media_group(chat_id, media_group)
            bot.send_message(chat_id, get_text('product_actions', lang),
                             reply_markup=selector_kb)
            return
        except Exception as e:
            print(f"Error sending media group: {e}")
    elif len(media_group) == 1:
        try:
            bot.send_photo(chat_id, media_group[0].media, caption=text, parse_mode='HTML',
                           reply_markup=selector_kb)
            return
        except Exception:
            pass

    bot.send_message(chat_id, text, parse_mode='HTML',
                     reply_markup=selector_kb)


# =============================================
# MAHSULOT SELECTOR HANDLERLARI
# (rang, o'lcham, turi, son — hammasi bitta postda)
# =============================================

def _parse_selector_data(data):
    """Selector callback_data ni parse qilish.
    Format: prefix_pid_colorid_sizeid_ptype_qty
    """
    parts = data.split('_')
    return {
        'pid': int(parts[1]),
        'color_id': int(parts[2]),
        'size_id': int(parts[3]),
        'ptype': parts[4],
        'qty': int(parts[5]),
    }


def _refresh_selector(call, product, color_id, size_id, ptype, qty, lang):
    """Selector klaviaturasini yangilash (faqat tugmalar)"""
    new_kb = kb.product_selector_keyboard(
        product, color_id=color_id, size_id=size_id,
        ptype=ptype, qty=qty, lang=lang
    )
    try:
        bot.edit_message_reply_markup(
            call.message.chat.id, call.message.message_id,
            reply_markup=new_kb
        )
    except Exception:
        pass


@bot.callback_query_handler(func=lambda c: c.data == 'noop')
def handle_noop(call):
    """Noop — label tugmalar uchun"""
    bot.answer_callback_query(call.id)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pc_'))
def handle_select_color(call):
    """Rang tanlash"""
    s = _parse_selector_data(call.data)
    lang = get_user_lang(call.from_user.id)
    try:
        product = Product.objects.get(id=s['pid'])
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    bot.answer_callback_query(call.id)
    _refresh_selector(call, product, s['color_id'], s['size_id'], s['ptype'], s['qty'], lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pz_'))
def handle_select_size(call):
    """O'lcham tanlash"""
    s = _parse_selector_data(call.data)
    lang = get_user_lang(call.from_user.id)
    try:
        product = Product.objects.get(id=s['pid'])
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    bot.answer_callback_query(call.id)
    _refresh_selector(call, product, s['color_id'], s['size_id'], s['ptype'], s['qty'], lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pt_'))
def handle_toggle_type(call):
    """Dona/Karobka tanlash"""
    s = _parse_selector_data(call.data)
    lang = get_user_lang(call.from_user.id)
    try:
        product = Product.objects.get(id=s['pid'])
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    bot.answer_callback_query(call.id)
    _refresh_selector(call, product, s['color_id'], s['size_id'], s['ptype'], s['qty'], lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pi_'))
def handle_inc_qty(call):
    """Son oshirish (+)"""
    s = _parse_selector_data(call.data)
    lang = get_user_lang(call.from_user.id)
    if s['qty'] >= 99:
        bot.answer_callback_query(call.id, get_text('max_qty_toast', lang))
        return
    try:
        product = Product.objects.get(id=s['pid'])
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    bot.answer_callback_query(call.id)
    _refresh_selector(call, product, s['color_id'], s['size_id'], s['ptype'], s['qty'] + 1, lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pd_'))
def handle_dec_qty(call):
    """Son kamaytirish (-)"""
    s = _parse_selector_data(call.data)
    lang = get_user_lang(call.from_user.id)
    if s['qty'] <= 1:
        bot.answer_callback_query(call.id, get_text('min_qty_toast', lang))
        return
    try:
        product = Product.objects.get(id=s['pid'])
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    bot.answer_callback_query(call.id)
    _refresh_selector(call, product, s['color_id'], s['size_id'], s['ptype'], s['qty'] - 1, lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('pa_'))
def handle_add_to_cart_final(call):
    """Savatga qo'shish — barcha tanlovlar tayyor"""
    s = _parse_selector_data(call.data)
    lang = get_user_lang(call.from_user.id)

    try:
        product = Product.objects.get(id=s['pid'])
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return

    bot_user = get_or_create_user(call)
    cart = get_cart(bot_user)

    # Rang va o'lcham
    color = None
    if s['color_id'] > 0:
        try:
            color = ProductColor.objects.get(id=s['color_id'])
        except ProductColor.DoesNotExist:
            pass

    size = None
    if s['size_id'] > 0:
        try:
            size = ProductSize.objects.get(id=s['size_id'])
        except ProductSize.DoesNotExist:
            pass

    # Savatga qo'shish
    ptype = 'dona' if s['ptype'] == 'd' else 'karobka'
    CartItem.objects.create(
        cart=cart,
        product=product,
        color=color,
        size=size,
        quantity=s['qty'],
        purchase_type=ptype
    )

    # Toast xabar
    bot.answer_callback_query(call.id, get_text('added_toast', lang), show_alert=True)


# =============================================
# SAVAT
# =============================================
def show_cart(chat_id, telegram_id, lang):
    try:
        bot_user = BotUser.objects.get(telegram_id=telegram_id)
        cart = get_cart(bot_user)
    except BotUser.DoesNotExist:
        bot.send_message(chat_id, get_text('cart_empty', lang))
        return

    items = cart.items.select_related('product', 'color', 'size').all()
    if not items.exists():
        bot.send_message(chat_id, get_text('cart_empty', lang))
        return

    text = get_text('cart_header', lang)
    for i, item in enumerate(items, 1):
        color_name = f"{item.color.emoji} {item.color.get_name(lang)}" if item.color else "—"
        size_name = item.size.name if item.size else "—"
        ptype = "dona" if item.purchase_type == 'dona' else "karobka"
        unit_price = item.product.price if item.purchase_type == 'dona' else (item.product.box_price or item.product.price)
        text += get_text('cart_item', lang).format(
            num=i,
            name=item.product.get_name(lang),
            color=color_name,
            size=size_name,
            type=ptype,
            qty=item.quantity,
            price=format_price(unit_price),
            subtotal=format_price(item.get_subtotal())
        )
    text += get_text('cart_total', lang).format(total=format_price(cart.get_total()))

    bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=kb.cart_keyboard(cart, lang))


# Savat: +/- / o'chirish
@bot.callback_query_handler(func=lambda c: c.data.startswith('cinc_'))
def handle_cart_increase(call):
    item_id = int(call.data.split('_')[1])
    lang = get_user_lang(call.from_user.id)
    try:
        item = CartItem.objects.get(id=item_id)
        item.quantity += 1
        item.save()
    except CartItem.DoesNotExist:
        pass
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    show_cart(call.message.chat.id, call.from_user.id, lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('cdec_'))
def handle_cart_decrease(call):
    item_id = int(call.data.split('_')[1])
    lang = get_user_lang(call.from_user.id)
    try:
        item = CartItem.objects.get(id=item_id)
        if item.quantity > 1:
            item.quantity -= 1
            item.save()
        else:
            item.delete()
    except CartItem.DoesNotExist:
        pass
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    show_cart(call.message.chat.id, call.from_user.id, lang)


@bot.callback_query_handler(func=lambda c: c.data.startswith('cdel_'))
def handle_cart_delete(call):
    item_id = int(call.data.split('_')[1])
    lang = get_user_lang(call.from_user.id)
    try:
        CartItem.objects.get(id=item_id).delete()
    except CartItem.DoesNotExist:
        pass
    bot.answer_callback_query(call.id, get_text('cart_item_removed', lang))
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    show_cart(call.message.chat.id, call.from_user.id, lang)


@bot.callback_query_handler(func=lambda c: c.data == 'cart_clear')
def handle_cart_clear(call):
    lang = get_user_lang(call.from_user.id)
    try:
        bot_user = BotUser.objects.get(telegram_id=call.from_user.id)
        cart = get_cart(bot_user)
        cart.items.all().delete()
    except Exception:
        pass
    bot.answer_callback_query(call.id, get_text('cart_cleared', lang))
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(call.message.chat.id, get_text('cart_empty', lang))


# =============================================
# BUYURTMA BERISH
# =============================================
@bot.callback_query_handler(func=lambda c: c.data == 'order_start')
def handle_order_start(call):
    lang = get_user_lang(call.from_user.id)
    user_states[call.from_user.id] = {'step': 'phone'}
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(call.message.chat.id, get_text('order_phone', lang),
                     parse_mode='HTML', reply_markup=kb.phone_keyboard(lang))


def handle_order_phone_text(message, lang):
    """Telefon raqam matn sifatida kiritilganda"""
    phone = message.text.strip()
    user_states[message.from_user.id]['phone'] = phone
    user_states[message.from_user.id]['step'] = 'address'
    bot.send_message(message.chat.id, get_text('order_address', lang),
                     parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))


def handle_order_address(message, lang):
    """Manzil kiritilganda"""
    address = message.text.strip()
    uid = message.from_user.id
    user_states[uid]['address'] = address
    user_states[uid]['step'] = 'confirm'

    try:
        bot_user = BotUser.objects.get(telegram_id=uid)
        cart = get_cart(bot_user)
    except Exception:
        bot.send_message(message.chat.id, get_text('error_general', lang))
        return

    items = cart.items.select_related('product', 'color', 'size').all()
    if not items.exists():
        bot.send_message(message.chat.id, get_text('cart_empty', lang))
        if uid in user_states:
            del user_states[uid]
        return

    items_text = ""
    for i, item in enumerate(items, 1):
        items_text += f"{i}. {item.product.get_name(lang)} x{item.quantity}\n"

    text = get_text('order_confirm', lang).format(
        phone=user_states[uid]['phone'],
        address=address,
        items=items_text,
        total=format_price(cart.get_total())
    )
    bot.send_message(message.chat.id, text, parse_mode='HTML',
                     reply_markup=kb.order_confirm_keyboard(lang))


@bot.callback_query_handler(func=lambda c: c.data == 'order_yes')
def handle_order_confirm(call):
    lang = get_user_lang(call.from_user.id)
    uid = call.from_user.id

    if uid not in user_states:
        bot.answer_callback_query(call.id, get_text('error_general', lang))
        return

    try:
        bot_user = BotUser.objects.get(telegram_id=uid)
        cart = get_cart(bot_user)
        items = cart.items.select_related('product', 'color', 'size').all()

        if not items.exists():
            bot.answer_callback_query(call.id, get_text('cart_empty', lang))
            return

        # Buyurtma yaratish
        order = Order.objects.create(
            user=bot_user,
            phone=user_states[uid].get('phone', ''),
            address=user_states[uid].get('address', ''),
            total_price=cart.get_total()
        )

        for item in items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                product_name=item.product.get_name(lang),
                color_name=f"{item.color.get_name(lang)}" if item.color else '',
                size_name=item.size.name if item.size else '',
                quantity=item.quantity,
                price=item.product.price if item.purchase_type == 'dona' else (item.product.box_price or item.product.price),
                purchase_type=item.purchase_type
            )

        # Telefon saqlash
        bot_user.phone = user_states[uid].get('phone', '')
        bot_user.save(update_fields=['phone'])

        # Savatni tozalash
        cart.items.all().delete()

        # State tozalash
        del user_states[uid]

        bot.edit_message_text(
            get_text('order_success', lang).format(order_id=order.id),
            call.message.chat.id, call.message.message_id,
            parse_mode='HTML'
        )
        bot.send_message(call.message.chat.id, get_text('main_menu', lang),
                         parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))

    except Exception as e:
        print(f"[ORDER ERROR] {e}")
        bot.answer_callback_query(call.id, get_text('error_general', lang))


@bot.callback_query_handler(func=lambda c: c.data == 'order_no')
def handle_order_cancel(call):
    lang = get_user_lang(call.from_user.id)
    if call.from_user.id in user_states:
        del user_states[call.from_user.id]
    bot.edit_message_text(
        get_text('order_cancelled', lang),
        call.message.chat.id, call.message.message_id,
        parse_mode='HTML'
    )
    bot.send_message(call.message.chat.id, get_text('main_menu', lang),
                     parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))


# =============================================
# BUYURTMALAR TARIXI
# =============================================
def show_orders(chat_id, telegram_id, lang):
    try:
        bot_user = BotUser.objects.get(telegram_id=telegram_id)
        orders = Order.objects.filter(user=bot_user).order_by('-created_at')[:20]
    except BotUser.DoesNotExist:
        bot.send_message(chat_id, get_text('no_orders', lang))
        return

    if not orders.exists():
        bot.send_message(chat_id, get_text('no_orders', lang))
        return

    text = get_text('orders_list', lang)
    for order in orders:
        text += get_text('order_item_line', lang).format(
            id=order.id,
            status=order.get_status_display(),
            total=format_price(order.total_price),
            date=order.created_at.strftime('%d.%m.%Y')
        )
    bot.send_message(chat_id, text, parse_mode='HTML')


# =============================================
# BACK TO MENU (Inline)
# =============================================
@bot.callback_query_handler(func=lambda c: c.data == 'back_menu')
def handle_back_menu(call):
    lang = get_user_lang(call.from_user.id)
    ai_mode_users.discard(call.from_user.id)
    try:
        bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception:
        pass
    bot.send_message(call.message.chat.id, get_text('main_menu', lang),
                     parse_mode='HTML', reply_markup=kb.main_menu_keyboard(lang))


# =============================================
# AI CHATBOT HANDLER
# =============================================

AI_PRODUCTS_PER_PAGE = 5

# AI qidiruv natijalari keshi (callback_data 64 bayt limiti tufayli)
# {chat_id: product_ids_list}
_ai_search_results = {}


def handle_ai_message(message, lang):
    """
    AI rejimidagi foydalanuvchi xabarini Gemini ga yuborish.
    Javobni matn + mahsulot tugmalari bilan ko'rsatish.
    """
    uid = message.from_user.id
    chat_id = message.chat.id

    # "Javob tayyorlanmoqda..." xabarini yuborish
    thinking_msg = bot.send_message(
        chat_id,
        get_text('ai_thinking', lang),
        parse_mode='HTML'
    )

    try:
        from .chatbot import get_ai_response
        result = get_ai_response(
            user_id=uid,
            message_text=message.text,
            lang=lang
        )

        # "Javob tayyorlanmoqda" xabarini o'chirish
        try:
            bot.delete_message(chat_id, thinking_msg.message_id)
        except Exception:
            pass

        ai_text = result['text']
        product_ids = result['product_ids']

        # 1. AI javob matnini yuborish
        if len(ai_text) <= 4096:
            bot.send_message(chat_id, ai_text, parse_mode='HTML')
        else:
            for i in range(0, len(ai_text), 4096):
                bot.send_message(chat_id, ai_text[i:i + 4096], parse_mode='HTML')

        # 2. Mahsulot tugmalarini ko'rsatish (agar mavjud bo'lsa)
        if product_ids:
            _ai_search_results[chat_id] = product_ids
            _show_ai_products_page(chat_id, product_ids, 1, lang)

    except Exception as e:
        print(f"[AI HANDLER ERROR] {e}")
        notify_admin_error(
            title='AI handler xatoligi',
            error=e,
            extra=f"chat_id={chat_id}\nuser_id={uid}\nlang={lang}\nmessage={message.text}"
        )
        try:
            bot.delete_message(chat_id, thinking_msg.message_id)
        except Exception:
            pass
        bot.send_message(
            chat_id,
            get_text('ai_error', lang),
            parse_mode='HTML',
            reply_markup=kb.main_menu_keyboard(lang)
        )


def _show_ai_products_page(chat_id, product_ids, page, lang, message_id=None):
    """AI topgan mahsulotlarni sahifalab ko'rsatish"""
    products = Product.objects.filter(
        id__in=product_ids, in_stock=True
    ).select_related('category')

    # ID lar tartibini saqlash
    id_order = {pid: i for i, pid in enumerate(product_ids)}
    products = sorted(products, key=lambda p: id_order.get(p.id, 999))

    total = len(products)
    if total == 0:
        return

    total_pages = math.ceil(total / AI_PRODUCTS_PER_PAGE)
    page = max(1, min(page, total_pages))
    start = (page - 1) * AI_PRODUCTS_PER_PAGE
    page_products = products[start:start + AI_PRODUCTS_PER_PAGE]

    text = get_text('ai_products_title', lang).format(
        total=total, page=page, total_pages=total_pages
    )

    markup = kb.ai_products_keyboard(page_products, page, total_pages, lang)

    if message_id:
        try:
            bot.edit_message_text(
                text, chat_id, message_id,
                parse_mode='HTML', reply_markup=markup
            )
            return
        except Exception:
            pass

    bot.send_message(chat_id, text, parse_mode='HTML', reply_markup=markup)


# AI mahsulot pagination
@bot.callback_query_handler(func=lambda c: c.data.startswith('aipage_'))
def handle_ai_page(call):
    """AI mahsulotlar sahifasini almashtirish"""
    page = int(call.data.split('_')[1])
    chat_id = call.message.chat.id
    lang = get_user_lang(call.from_user.id)
    product_ids = _ai_search_results.get(chat_id, [])
    if product_ids:
        _show_ai_products_page(chat_id, product_ids, page, lang, call.message.message_id)
    bot.answer_callback_query(call.id)


# AI mahsulot detail
@bot.callback_query_handler(func=lambda c: c.data.startswith('aiprod_'))
def handle_ai_product(call):
    """AI topgan mahsulotni ko'rsatish — savatga qo'shish imkoniyati bilan"""
    pid = int(call.data.split('_')[1])
    lang = get_user_lang(call.from_user.id)
    try:
        product = Product.objects.get(id=pid)
    except Product.DoesNotExist:
        bot.answer_callback_query(call.id, get_text('product_not_found', lang))
        return
    bot.answer_callback_query(call.id)
    show_product_detail(call.message.chat.id, product, lang)
