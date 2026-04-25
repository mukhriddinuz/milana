"""
Milana Textile Bot — Ko'p tilli matnlar tizimi.
Barcha statik matnlar 3 tilda: O'zbek, Rus, Ingliz
"""

TEXTS = {
    # =============================================
    # UMUMIY
    # =============================================
    'welcome': {
        'uz': "<b>Milana Textile</b>\nOnlayn do'kon\n\nTilni tanlang:",
        'ru': "<b>Milana Textile</b>\nОнлайн магазин\n\nВыберите язык:",
        'en': "<b>Milana Textile</b>\nOnline store\n\nSelect language:",
    },
    'language_selected': {
        'uz': "Til tanlandi: O'zbekcha",
        'ru': "Язык выбран: Русский",
        'en': "Language selected: English",
    },
    'main_menu': {
        'uz': "<b>Milana Textile</b>\n\nBo'limni tanlang:",
        'ru': "<b>Milana Textile</b>\n\nВыберите раздел:",
        'en': "<b>Milana Textile</b>\n\nSelect section:",
    },

    # =============================================
    # MENYU TUGMALARI
    # =============================================
    'btn_men': {
        'uz': "Erkaklar kiyimlari",
        'ru': "Мужская одежда",
        'en': "Men's clothing",
    },
    'btn_women': {
        'uz': "Ayollar kiyimlari",
        'ru': "Женская одежда",
        'en': "Women's clothing",
    },
    'btn_kids': {
        'uz': "Bolalar kiyimlari",
        'ru': "Детская одежда",
        'en': "Kids' clothing",
    },
    'btn_cart': {
        'uz': "Savat",
        'ru': "Корзина",
        'en': "Cart",
    },
    'btn_my_orders': {
        'uz': "Buyurtmalarim",
        'ru': "Мои заказы",
        'en': "My orders",
    },
    'btn_about': {
        'uz': "Biz haqimizda",
        'ru': "О нас",
        'en': "About us",
    },
    'btn_ai': {
        'uz': "AI Yordamchi",
        'ru': "AI Помощник",
        'en': "AI Assistant",
    },
    'btn_settings': {
        'uz': "Sozlamalar",
        'ru': "Настройки",
        'en': "Settings",
    },
    'btn_back': {
        'uz': "Ortga",
        'ru': "Назад",
        'en': "Back",
    },
    'btn_back_to_menu': {
        'uz': "Asosiy menyu",
        'ru': "Главное меню",
        'en': "Main menu",
    },
    'btn_change_language': {
        'uz': "Tilni o'zgartirish",
        'ru': "Сменить язык",
        'en': "Change language",
    },

    # =============================================
    # KATEGORIYA VA MAHSULOT
    # =============================================
    'select_category': {
        'uz': "Kategoriyani tanlang:",
        'ru': "Выберите категорию:",
        'en': "Select category:",
    },
    'no_categories': {
        'uz': "Hozircha kategoriyalar mavjud emas",
        'ru': "Категорий пока нет",
        'en': "No categories available",
    },
    'no_products': {
        'uz': "Bu kategoriyada mahsulotlar mavjud emas",
        'ru': "В этой категории нет товаров",
        'en': "No products in this category",
    },
    'product_actions': {
        'uz': "Mahsulot bo'yicha amallar:",
        'ru': "Действия по товару:",
        'en': "Product actions:",
    },
    'product_card': {
        'uz': (
            "<b>{name}</b>\n"
            "{model}"
            "{variant}"
            "\nNarxi: <b>{price} so'm</b>"
            "{box_price}"
            "\n\nO'lchamlar: {sizes}"
            "\nRanglar: {colors}"
            "\n\n{description}"
        ),
        'ru': (
            "<b>{name}</b>\n"
            "{model}"
            "{variant}"
            "\nЦена: <b>{price} сум</b>"
            "{box_price}"
            "\n\nРазмеры: {sizes}"
            "\nЦвета: {colors}"
            "\n\n{description}"
        ),
        'en': (
            "<b>{name}</b>\n"
            "{model}"
            "{variant}"
            "\nPrice: <b>{price} sum</b>"
            "{box_price}"
            "\n\nSizes: {sizes}"
            "\nColors: {colors}"
            "\n\n{description}"
        ),
    },
    'model_label': {
        'uz': "Model: {model}\n",
        'ru': "Модель: {model}\n",
        'en': "Model: {model}\n",
    },
    'variant_label': {
        'uz': "Variant: {variant}\n",
        'ru': "Вариант: {variant}\n",
        'en': "Variant: {variant}\n",
    },
    'box_price_label': {
        'uz': "\nKarobka: <b>{box_price} so'm</b> ({box_qty} dona)",
        'ru': "\nКоробка: <b>{box_price} сум</b> ({box_qty} шт)",
        'en': "\nBox: <b>{box_price} sum</b> ({box_qty} pcs)",
    },

    # =============================================
    # RANG VA O'LCHAM TANLASH
    # =============================================
    'select_color': {
        'uz': "Rangni tanlang:",
        'ru': "Выберите цвет:",
        'en': "Select color:",
    },
    'select_size': {
        'uz': "O'lchamni tanlang:",
        'ru': "Выберите размер:",
        'en': "Select size:",
    },
    'select_purchase_type': {
        'uz': "Sotib olish turini tanlang:",
        'ru': "Выберите тип покупки:",
        'en': "Select purchase type:",
    },
    'purchase_dona': {
        'uz': "Donalik — {price} so'm",
        'ru': "Поштучно — {price} сум",
        'en': "Per unit — {price} sum",
    },
    'purchase_karobka': {
        'uz': "Karobkalik — {price} so'm ({qty} dona)",
        'ru': "Коробками — {price} сум ({qty} шт)",
        'en': "Per box — {price} sum ({qty} pcs)",
    },
    'select_quantity': {
        'uz': "Sonini tanlang:",
        'ru': "Выберите количество:",
        'en': "Select quantity:",
    },
    'added_to_cart': {
        'uz': "Savatga qo'shildi\n\n"
              "{product}\n"
              "Rang: {color}\n"
              "O'lcham: {size}\n"
              "Turi: {type}\n"
              "Soni: {qty}\n"
              "Narxi: {price} so'm",
        'ru': "Добавлено в корзину\n\n"
              "{product}\n"
              "Цвет: {color}\n"
              "Размер: {size}\n"
              "Тип: {type}\n"
              "Кол-во: {qty}\n"
              "Цена: {price} сум",
        'en': "Added to cart\n\n"
              "{product}\n"
              "Color: {color}\n"
              "Size: {size}\n"
              "Type: {type}\n"
              "Qty: {qty}\n"
              "Price: {price} sum",
    },

    # =============================================
    # SAVAT
    # =============================================
    'cart_empty': {
        'uz': "Savatingiz bo'sh",
        'ru': "Ваша корзина пуста",
        'en': "Your cart is empty",
    },
    'cart_header': {
        'uz': "<b>Savat</b>\n\n",
        'ru': "<b>Корзина</b>\n\n",
        'en': "<b>Cart</b>\n\n",
    },
    'cart_item': {
        'uz': "{num}. {name}\n   {color} | {size} | {type}\n   {qty} x {price} = <b>{subtotal} so'm</b>\n\n",
        'ru': "{num}. {name}\n   {color} | {size} | {type}\n   {qty} x {price} = <b>{subtotal} сум</b>\n\n",
        'en': "{num}. {name}\n   {color} | {size} | {type}\n   {qty} x {price} = <b>{subtotal} sum</b>\n\n",
    },
    'cart_total': {
        'uz': "<b>Jami: {total} so'm</b>",
        'ru': "<b>Итого: {total} сум</b>",
        'en': "<b>Total: {total} sum</b>",
    },
    'btn_order': {
        'uz': "Buyurtma berish",
        'ru': "Оформить заказ",
        'en': "Place order",
    },
    'btn_clear_cart': {
        'uz': "Savatni tozalash",
        'ru': "Очистить корзину",
        'en': "Clear cart",
    },
    'cart_cleared': {
        'uz': "Savat tozalandi",
        'ru': "Корзина очищена",
        'en': "Cart cleared",
    },
    'btn_add_to_cart': {
        'uz': "Savatga qo'shish",
        'ru': "В корзину",
        'en': "Add to cart",
    },

    # =============================================
    # BUYURTMA
    # =============================================
    'order_phone': {
        'uz': "Telefon raqamingizni yuboring:",
        'ru': "Отправьте ваш номер телефона:",
        'en': "Send your phone number:",
    },
    'btn_send_phone': {
        'uz': "Telefon raqamni yuborish",
        'ru': "Отправить номер",
        'en': "Send phone number",
    },
    'order_address': {
        'uz': "Yetkazib berish manzilini yozing:",
        'ru': "Напишите адрес доставки:",
        'en': "Enter delivery address:",
    },
    'order_confirm': {
        'uz': (
            "<b>Buyurtma tasdiqlash</b>\n\n"
            "Telefon: {phone}\n"
            "Manzil: {address}\n\n"
            "{items}\n"
            "<b>Jami: {total} so'm</b>\n\n"
            "Tasdiqlaysizmi?"
        ),
        'ru': (
            "<b>Подтверждение заказа</b>\n\n"
            "Телефон: {phone}\n"
            "Адрес: {address}\n\n"
            "{items}\n"
            "<b>Итого: {total} сум</b>\n\n"
            "Подтверждаете?"
        ),
        'en': (
            "<b>Order confirmation</b>\n\n"
            "Phone: {phone}\n"
            "Address: {address}\n\n"
            "{items}\n"
            "<b>Total: {total} sum</b>\n\n"
            "Confirm?"
        ),
    },
    'btn_confirm_yes': {
        'uz': "Ha, tasdiqlash",
        'ru': "Да, подтвердить",
        'en': "Yes, confirm",
    },
    'btn_confirm_no': {
        'uz': "Bekor qilish",
        'ru': "Отменить",
        'en': "Cancel",
    },
    'order_success': {
        'uz': "Buyurtma qabul qilindi\n\nBuyurtma raqami: #{order_id}\n\nTez orada siz bilan bog'lanamiz.",
        'ru': "Заказ принят\n\nНомер заказа: #{order_id}\n\nМы свяжемся с вами.",
        'en': "Order accepted\n\nOrder number: #{order_id}\n\nWe will contact you soon.",
    },
    'order_cancelled': {
        'uz': "Buyurtma bekor qilindi",
        'ru': "Заказ отменён",
        'en': "Order cancelled",
    },

    # =============================================
    # BUYURTMALAR TARIXI
    # =============================================
    'no_orders': {
        'uz': "Sizda hali buyurtmalar yo'q",
        'ru': "У вас пока нет заказов",
        'en': "You have no orders yet",
    },
    'orders_list': {
        'uz': "<b>Buyurtmalar</b>\n\n",
        'ru': "<b>Заказы</b>\n\n",
        'en': "<b>Orders</b>\n\n",
    },
    'order_item_line': {
        'uz': "#{id} | {status} | {total} so'm | {date}\n",
        'ru': "#{id} | {status} | {total} сум | {date}\n",
        'en': "#{id} | {status} | {total} sum | {date}\n",
    },

    # =============================================
    # BIZ HAQIMIZDA
    # =============================================
    'about_text': {
        'uz': (
            "<b>Milana Textile</b>\n\n"
            "Sifatli va zamonaviy kiyimlar ishlab chiqaruvchi.\n\n"
            "Manzil: Toshkent shahri\n"
            "Telefon: +998 XX XXX XX XX\n"
            "Ish vaqti: 09:00 - 18:00"
        ),
        'ru': (
            "<b>Milana Textile</b>\n\n"
            "Производитель качественной и современной одежды.\n\n"
            "Адрес: город Ташкент\n"
            "Телефон: +998 XX XXX XX XX\n"
            "Время работы: 09:00 - 18:00"
        ),
        'en': (
            "<b>Milana Textile</b>\n\n"
            "Quality and modern clothing manufacturer.\n\n"
            "Address: Tashkent city\n"
            "Phone: +998 XX XXX XX XX\n"
            "Working hours: 09:00 - 18:00"
        ),
    },

    # =============================================
    # SOZLAMALAR
    # =============================================
    'settings_menu': {
        'uz': "<b>Sozlamalar</b>",
        'ru': "<b>Настройки</b>",
        'en': "<b>Settings</b>",
    },
    'select_language': {
        'uz': "Tilni tanlang:",
        'ru': "Выберите язык:",
        'en': "Select language:",
    },

    # =============================================
    # XATOLIKLAR
    # =============================================
    'error_general': {
        'uz': "Xatolik yuz berdi. Qaytadan urinib ko'ring.",
        'ru': "Произошла ошибка. Попробуйте снова.",
        'en': "An error occurred. Please try again.",
    },
    'product_not_found': {
        'uz': "Mahsulot topilmadi",
        'ru': "Товар не найден",
        'en': "Product not found",
    },
    'invalid_quantity': {
        'uz': "Noto'g'ri son kiritildi.",
        'ru': "Неверное количество.",
        'en': "Invalid quantity.",
    },

    # =============================================
    # PAGINATION
    # =============================================
    'btn_next': {
        'uz': "Keyingi",
        'ru': "Далее",
        'en': "Next",
    },
    'btn_prev': {
        'uz': "Oldingi",
        'ru': "Назад",
        'en': "Previous",
    },
    'page_info': {
        'uz': "{current}/{total}",
        'ru': "{current}/{total}",
        'en': "{current}/{total}",
    },

    # =============================================
    # SAVAT ITEM O'CHIRISH
    # =============================================
    'cart_item_removed': {
        'uz': "Mahsulot o'chirildi",
        'ru': "Товар удалён",
        'en': "Item removed",
    },
    'btn_remove': {
        'uz': "O'chirish",
        'ru': "Удалить",
        'en': "Remove",
    },
    'btn_increase': {
        'uz': "+",
        'ru': "+",
        'en': "+",
    },
    'btn_decrease': {
        'uz': "-",
        'ru': "-",
        'en': "-",
    },
}


def get_text(key, lang='uz'):
    """Tilga mos matn olish"""
    text_dict = TEXTS.get(key, {})
    return text_dict.get(lang, text_dict.get('uz', f'[{key}]'))
