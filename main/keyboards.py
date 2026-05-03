"""Klaviaturalar — Reply va Inline"""
from telebot import types
from .translations import get_text


def language_keyboard():
    """Til tanlash klaviaturasi"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(
        types.InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz"),
        types.InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru"),
        types.InlineKeyboardButton("🇬🇧 English", callback_data="lang_en"),
    )
    return kb


def main_menu_keyboard(lang='uz'):
    """Asosiy menyu (ReplyKeyboard)"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        types.KeyboardButton(get_text('btn_men', lang)),
        types.KeyboardButton(get_text('btn_women', lang)),
    )
    kb.add(
        types.KeyboardButton(get_text('btn_kids', lang)),
        types.KeyboardButton(get_text('btn_cart', lang)),
    )
    kb.add(
        types.KeyboardButton(get_text('btn_my_orders', lang)),
        types.KeyboardButton(get_text('btn_ai', lang)),
    )
    kb.add(
        types.KeyboardButton(get_text('btn_about', lang)),
        types.KeyboardButton(get_text('btn_settings', lang)),
    )
    return kb


def categories_keyboard(categories, lang='uz'):
    """Kategoriyalar InlineKeyboard"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    for cat in categories:
        kb.add(types.InlineKeyboardButton(
            f"{cat.icon} {cat.get_name(lang)}",
            callback_data=f"cat_{cat.id}"
        ))
    return kb


def products_keyboard(products, page, total_pages, category_id, lang='uz'):
    """Mahsulotlar ro'yxati InlineKeyboard (paginated)"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    for p in products:
        kb.add(types.InlineKeyboardButton(
            f"{p.get_name(lang)} — {int(p.price):,} so'm",
            callback_data=f"prod_{p.id}"
        ))
    # Pagination
    nav = []
    if page > 1:
        nav.append(types.InlineKeyboardButton(
            get_text('btn_prev', lang), callback_data=f"ppage_{category_id}_{page-1}"))
    if page < total_pages:
        nav.append(types.InlineKeyboardButton(
            get_text('btn_next', lang), callback_data=f"ppage_{category_id}_{page+1}"))
    if nav:
        kb.row(*nav)
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang), callback_data=f"gender_{products[0].category.gender}" if products else "back_menu"))
    return kb


def product_selector_keyboard(product, color_id=0, size_id=0, ptype='d', qty=1, lang='uz'):
    """
    Mahsulot kartasi ichida to'liq tanlash klaviaturasi.
    Rang, o'lcham, dona/karobka, son — hammasi bitta postda.
    """
    from .utils import format_price
    kb = types.InlineKeyboardMarkup(row_width=4)
    pid = product.id

    colors = list(product.colors.all())
    sizes = list(product.sizes.all())

    # ── RANG TUGMALARI ──
    if colors:
        kb.add(types.InlineKeyboardButton(
            get_text('lbl_color', lang), callback_data="noop"))
        color_btns = []
        for c in colors:
            mark = " ✅" if c.id == color_id else ""
            color_btns.append(types.InlineKeyboardButton(
                f"{c.emoji}{mark}",
                callback_data=f"pc_{pid}_{c.id}_{size_id}_{ptype}_{qty}"
            ))
        for i in range(0, len(color_btns), 4):
            kb.row(*color_btns[i:i + 4])

    # ── O'LCHAM TUGMALARI ──
    if sizes:
        kb.add(types.InlineKeyboardButton(
            get_text('lbl_size', lang), callback_data="noop"))
        size_btns = []
        for s in sizes:
            mark = " ✅" if s.id == size_id else ""
            size_btns.append(types.InlineKeyboardButton(
                f"{s.name}{mark}",
                callback_data=f"pz_{pid}_{color_id}_{s.id}_{ptype}_{qty}"
            ))
        for i in range(0, len(size_btns), 5):
            kb.row(*size_btns[i:i + 5])

    # ── DONA / KAROBKA ──
    if product.box_price:
        dona_mark = " ✅" if ptype == 'd' else ""
        karobka_mark = " ✅" if ptype == 'k' else ""
        kb.row(
            types.InlineKeyboardButton(
                f"📦 {get_text('btn_dona', lang)}{dona_mark}",
                callback_data=f"pt_{pid}_{color_id}_{size_id}_d_{qty}"
            ),
            types.InlineKeyboardButton(
                f"📦 {get_text('btn_karobka_short', lang).format(qty=product.box_quantity)}{karobka_mark}",
                callback_data=f"pt_{pid}_{color_id}_{size_id}_k_{qty}"
            ),
        )

    # ── SON TANLASH: ➖ [son] ➕ ──
    kb.row(
        types.InlineKeyboardButton("➖", callback_data=f"pd_{pid}_{color_id}_{size_id}_{ptype}_{qty}"),
        types.InlineKeyboardButton(f"  {qty}  ", callback_data="noop"),
        types.InlineKeyboardButton("➕", callback_data=f"pi_{pid}_{color_id}_{size_id}_{ptype}_{qty}"),
    )

    # ── SAVATGA QO'SHISH (narx bilan) ──
    if ptype == 'k' and product.box_price:
        total = int(product.box_price) * qty
    else:
        total = int(product.price) * qty

    kb.add(types.InlineKeyboardButton(
        f"🛒 {get_text('btn_add_to_cart', lang)} — {format_price(total)}",
        callback_data=f"pa_{pid}_{color_id}_{size_id}_{ptype}_{qty}"
    ))

    # ── ORTGA ──
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang),
        callback_data=f"cat_{product.category_id}"
    ))

    return kb


def cart_keyboard(cart, lang='uz'):
    """Savat tugmalari"""
    kb = types.InlineKeyboardMarkup(row_width=3)
    items = cart.items.select_related('product', 'color', 'size').all()
    for i, item in enumerate(items, 1):
        kb.row(
            types.InlineKeyboardButton("-", callback_data=f"cdec_{item.id}"),
            types.InlineKeyboardButton(f"{i}. {item.quantity} dona", callback_data=f"cinfo_{item.id}"),
            types.InlineKeyboardButton("+", callback_data=f"cinc_{item.id}"),
        )
        kb.add(types.InlineKeyboardButton(
            f"O'chirish: {item.product.get_name(lang)[:20]}", callback_data=f"cdel_{item.id}"))
    if items:
        kb.add(types.InlineKeyboardButton(
            get_text('btn_clear_cart', lang), callback_data="cart_clear"))
        kb.add(types.InlineKeyboardButton(
            get_text('btn_order', lang), callback_data="order_start"))
    return kb


def order_confirm_keyboard(lang='uz'):
    """Buyurtma tasdiqlash"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(get_text('btn_confirm_yes', lang), callback_data="order_yes"),
        types.InlineKeyboardButton(get_text('btn_confirm_no', lang), callback_data="order_no"),
    )
    return kb


def phone_keyboard(lang='uz'):
    """Telefon raqam yuborish"""
    kb = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    kb.add(types.KeyboardButton(get_text('btn_send_phone', lang), request_contact=True))
    kb.add(types.KeyboardButton(get_text('btn_back_to_menu', lang)))
    return kb


def settings_keyboard(lang='uz'):
    """Sozlamalar"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(
        get_text('btn_change_language', lang), callback_data="change_lang"))
    return kb


def ai_products_keyboard(products, page, total_pages, lang='uz'):
    """AI topgan mahsulotlar ro'yxati — pagination bilan.

    Args:
        products: Joriy sahifadagi mahsulotlar
        page: Hozirgi sahifa raqami
        total_pages: Jami sahifalar
        lang: Til kodi
    """
    kb = types.InlineKeyboardMarkup(row_width=1)

    for p in products:
        kb.add(types.InlineKeyboardButton(
            f"{p.get_name(lang)} — {int(p.price):,} so'm",
            callback_data=f"aiprod_{p.id}"
        ))

    # Pagination
    nav = []
    if page > 1:
        nav.append(types.InlineKeyboardButton(
            get_text('btn_prev', lang),
            callback_data=f"aipage_{page - 1}"
        ))
    nav.append(types.InlineKeyboardButton(
        f"{page}/{total_pages}", callback_data="noop"
    ))
    if page < total_pages:
        nav.append(types.InlineKeyboardButton(
            get_text('btn_next', lang),
            callback_data=f"aipage_{page + 1}"
        ))
    if nav:
        kb.row(*nav)

    return kb
