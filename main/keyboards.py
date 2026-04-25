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
        types.KeyboardButton(get_text('btn_about', lang)),
    )
    kb.add(
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


def product_detail_keyboard(product, lang='uz'):
    """Mahsulot kartasi tugmalari"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    kb.add(types.InlineKeyboardButton(
        get_text('btn_add_to_cart', lang),
        callback_data=f"addcart_{product.id}"
    ))
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang),
        callback_data=f"cat_{product.category_id}"
    ))
    return kb


def colors_keyboard(product, lang='uz'):
    """Rang tanlash InlineKeyboard"""
    kb = types.InlineKeyboardMarkup(row_width=2)
    colors = product.colors.all()
    for color in colors:
        kb.add(types.InlineKeyboardButton(
            f"{color.emoji} {color.get_name(lang)}",
            callback_data=f"color_{product.id}_{color.id}"
        ))
    if not colors.exists():
        kb.add(types.InlineKeyboardButton(
            "Davom etish" if lang == 'uz' else "Продолжить" if lang == 'ru' else "Continue",
            callback_data=f"color_{product.id}_0"
        ))
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang), callback_data=f"prod_{product.id}"))
    return kb


def sizes_keyboard(product, color_id, lang='uz'):
    """O'lcham tanlash InlineKeyboard"""
    kb = types.InlineKeyboardMarkup(row_width=3)
    sizes = product.sizes.all()
    for size in sizes:
        kb.add(types.InlineKeyboardButton(
            size.name,
            callback_data=f"size_{product.id}_{color_id}_{size.id}"
        ))
    if not sizes.exists():
        kb.add(types.InlineKeyboardButton(
            "Davom etish" if lang == 'uz' else "Продолжить" if lang == 'ru' else "Continue",
            callback_data=f"size_{product.id}_{color_id}_0"
        ))
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang), callback_data=f"addcart_{product.id}"))
    return kb


def purchase_type_keyboard(product, color_id, size_id, lang='uz'):
    """Dona yoki karobka tanlash"""
    kb = types.InlineKeyboardMarkup(row_width=1)
    from .utils import format_price
    kb.add(types.InlineKeyboardButton(
        get_text('purchase_dona', lang).format(price=format_price(product.price)),
        callback_data=f"ptype_{product.id}_{color_id}_{size_id}_dona"
    ))
    if product.box_price:
        kb.add(types.InlineKeyboardButton(
            get_text('purchase_karobka', lang).format(
                price=format_price(product.box_price), qty=product.box_quantity),
            callback_data=f"ptype_{product.id}_{color_id}_{size_id}_karobka"
        ))
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang),
        callback_data=f"size_{product.id}_{color_id}_{size_id}"
    ))
    return kb


def quantity_keyboard(product_id, color_id, size_id, ptype, lang='uz'):
    """Son tanlash"""
    kb = types.InlineKeyboardMarkup(row_width=5)
    btns = []
    for i in range(1, 11):
        btns.append(types.InlineKeyboardButton(
            str(i), callback_data=f"qty_{product_id}_{color_id}_{size_id}_{ptype}_{i}"
        ))
    kb.add(*btns[:5])
    kb.add(*btns[5:])
    kb.add(types.InlineKeyboardButton(
        get_text('btn_back', lang),
        callback_data=f"ptype_{product_id}_{color_id}_{size_id}_{ptype}"
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
