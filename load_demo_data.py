"""
Milana Textile Bot — Demo ma'lumotlar.
Ranglar, o'lchamlar, kategoriyalar va mahsulotlar.
"""
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'home.settings')
django.setup()

from main.models import (
    ProductColor, ProductSize, Category, Product
)


def create_colors():
    colors_data = [
        ("Qora", "Чёрный", "Black", "#000000", "⚫"),
        ("Oq", "Белый", "White", "#FFFFFF", "⚪"),
        ("Ko'k", "Синий", "Blue", "#0000FF", "🔵"),
        ("Qizil", "Красный", "Red", "#FF0000", "🔴"),
        ("Yashil", "Зелёный", "Green", "#008000", "🟢"),
        ("Kulrang", "Серый", "Gray", "#808080", "🩶"),
        ("Jigarrang", "Коричневый", "Brown", "#8B4513", "🟤"),
        ("Pushti", "Розовый", "Pink", "#FFC0CB", "🩷"),
        ("Sariq", "Жёлтый", "Yellow", "#FFD700", "🟡"),
        ("Moviy", "Голубой", "Light Blue", "#87CEEB", "💠"),
        ("Binafsha", "Фиолетовый", "Purple", "#800080", "🟣"),
        ("To'q ko'k", "Тёмно-синий", "Navy", "#000080", "🔵"),
    ]
    created = []
    for uz, ru, en, hex_code, emoji in colors_data:
        obj, _ = ProductColor.objects.get_or_create(
            name_uz=uz,
            defaults={'name_ru': ru, 'name_en': en, 'hex_code': hex_code, 'emoji': emoji}
        )
        created.append(obj)
    print(f"✅ {len(created)} ta rang yaratildi")
    return created


def create_sizes():
    # Kiyim o'lchamlari
    clothes = ["XS", "S", "M", "L", "XL", "XXL", "3XL"]
    for i, name in enumerate(clothes):
        ProductSize.objects.get_or_create(
            name=name, size_type='clothes', defaults={'order': i}
        )

    # Oyoq kiyim
    shoes = ["36", "37", "38", "39", "40", "41", "42", "43", "44", "45"]
    for i, name in enumerate(shoes):
        ProductSize.objects.get_or_create(
            name=name, size_type='shoes', defaults={'order': i}
        )

    # Bolalar
    kids = ["1-2 yosh", "3-4 yosh", "5-6 yosh", "7-8 yosh", "9-10 yosh", "11-12 yosh"]
    for i, name in enumerate(kids):
        ProductSize.objects.get_or_create(
            name=name, size_type='kids', defaults={'order': i}
        )

    print(f"✅ O'lchamlar yaratildi: kiyim({len(clothes)}), oyoq({len(shoes)}), bolalar({len(kids)})")


def create_categories():
    cats_data = [
        # Erkaklar
        ("Ko'ylak", "Рубашка", "Shirt", "erkak", "👔", 1),
        ("Shim", "Брюки", "Pants", "erkak", "👖", 2),
        ("Futbolka", "Футболка", "T-Shirt", "erkak", "👕", 3),
        ("Kurtka", "Куртка", "Jacket", "erkak", "🧥", 4),
        ("Kostyum", "Костюм", "Suit", "erkak", "🤵", 5),
        # Ayollar
        ("Ko'ylak", "Платье", "Dress", "ayol", "👗", 1),
        ("Bluzka", "Блузка", "Blouse", "ayol", "👚", 2),
        ("Yubka", "Юбка", "Skirt", "ayol", "🩱", 3),
        ("Palto", "Пальто", "Coat", "ayol", "🧥", 4),
        ("Sport kiyim", "Спортивная одежда", "Sportswear", "ayol", "🏃‍♀️", 5),
        # Bolalar
        ("Futbolka", "Футболка", "T-Shirt", "bola", "👕", 1),
        ("Shim", "Брюки", "Pants", "bola", "👖", 2),
        ("Ko'ylak", "Рубашка", "Shirt", "bola", "👔", 3),
        ("Kurtka", "Куртка", "Jacket", "bola", "🧥", 4),
        ("Sport kiyim", "Спортивная одежда", "Sportswear", "bola", "⚽", 5),
    ]
    created = []
    for uz, ru, en, gender, icon, order in cats_data:
        obj, _ = Category.objects.get_or_create(
            name_uz=uz, gender=gender,
            defaults={'name_ru': ru, 'name_en': en, 'icon': icon, 'order': order}
        )
        created.append(obj)
    print(f"✅ {len(created)} ta kategoriya yaratildi")
    return created


def create_products():
    colors = {c.name_uz: c for c in ProductColor.objects.all()}
    sizes_clothes = list(ProductSize.objects.filter(size_type='clothes'))
    sizes_shoes = list(ProductSize.objects.filter(size_type='shoes'))
    sizes_kids = list(ProductSize.objects.filter(size_type='kids'))

    products_data = [
        # ========== ERKAKLAR ==========
        {
            'name_uz': "Classic Slim Fit Ko'ylak",
            'name_ru': "Классическая рубашка Slim Fit",
            'name_en': "Classic Slim Fit Shirt",
            'model_name': "Slim Fit",
            'variant': "Premium Cotton",
            'description_uz': "100% paxta, yuqori sifatli erkaklar ko'ylagi. Ofis va kundalik uchun mos.",
            'description_ru': "100% хлопок, высококачественная мужская рубашка.",
            'description_en': "100% cotton, high quality men's shirt.",
            'price': 189000,
            'box_price': 1700000,
            'box_quantity': 10,
            'category': ('Ko\'ylak', 'erkak'),
            'season': 'universal',
            'stock_quantity': 150,
            'colors': ['Oq', 'Moviy', "To'q ko'k", 'Kulrang'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Business Classic Ko'ylak",
            'name_ru': "Деловая классическая рубашка",
            'name_en': "Business Classic Shirt",
            'model_name': "Regular Fit",
            'variant': "Oxford",
            'description_uz': "Biznes uslubidagi klassik ko'ylak. Paxta-poliester aralashmasi.",
            'price': 159000,
            'box_price': 1400000,
            'box_quantity': 10,
            'category': ('Ko\'ylak', 'erkak'),
            'season': 'universal',
            'stock_quantity': 200,
            'colors': ['Oq', "Ko'k", 'Kulrang', 'Qora'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Premium Chino Shim",
            'name_ru': "Премиум брюки Чино",
            'name_en': "Premium Chino Pants",
            'model_name': "Straight Fit",
            'variant': "Chino Cotton",
            'description_uz': "Yengil va qulay chino shimlar. Bahor-yoz mavsumi uchun ideal.",
            'price': 245000,
            'box_price': 2200000,
            'box_quantity': 10,
            'category': ('Shim', 'erkak'),
            'season': 'bahor',
            'stock_quantity': 120,
            'colors': ['Qora', 'Jigarrang', "To'q ko'k", 'Kulrang', 'Yashil'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Polo Futbolka",
            'name_ru': "Поло футболка",
            'name_en': "Polo T-Shirt",
            'model_name': "Classic Polo",
            'variant': "Pique Cotton",
            'description_uz': "Klassik polo futbolka. Yumshoq paxta, nafas oluvchi material.",
            'price': 129000,
            'box_price': 1100000,
            'box_quantity': 10,
            'category': ('Futbolka', 'erkak'),
            'season': 'yoz',
            'stock_quantity': 300,
            'colors': ['Qora', 'Oq', "Ko'k", 'Qizil', 'Yashil', 'Sariq'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Bomber Kurtka",
            'name_ru': "Куртка Бомбер",
            'name_en': "Bomber Jacket",
            'model_name': "Urban Bomber",
            'variant': "Polyester",
            'description_uz': "Zamonaviy bomber kurtka. Kuz-bahor mavsumi uchun.",
            'price': 389000,
            'box_price': 3500000,
            'box_quantity': 10,
            'category': ('Kurtka', 'erkak'),
            'season': 'kuz',
            'stock_quantity': 80,
            'colors': ['Qora', "To'q ko'k", 'Kulrang', 'Yashil'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Klassik Kostyum",
            'name_ru': "Классический костюм",
            'name_en': "Classic Suit",
            'model_name': "Italian Fit",
            'variant': "Wool Blend",
            'description_uz': "Italyan uslubidagi klassik kostyum. To'y va rasmiy tadbirlar uchun.",
            'price': 890000,
            'box_price': None,
            'box_quantity': 1,
            'category': ('Kostyum', 'erkak'),
            'season': 'universal',
            'stock_quantity': 50,
            'colors': ['Qora', "To'q ko'k", 'Kulrang'],
            'sizes': sizes_clothes,
        },

        # ========== AYOLLAR ==========
        {
            'name_uz': "Yozgi Maxi Ko'ylak",
            'name_ru': "Летнее макси платье",
            'name_en': "Summer Maxi Dress",
            'model_name': "Maxi",
            'variant': "Chiffon",
            'description_uz': "Yengil shifon yozgi ko'ylak. Guldor naqsh bilan.",
            'price': 279000,
            'box_price': 2500000,
            'box_quantity': 10,
            'category': ('Ko\'ylak', 'ayol'),
            'season': 'yoz',
            'stock_quantity': 100,
            'colors': ['Qizil', 'Pushti', 'Moviy', 'Oq'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Ofis Bluzka",
            'name_ru': "Офисная блузка",
            'name_en': "Office Blouse",
            'model_name': "Elegant Fit",
            'variant': "Silk Touch",
            'description_uz': "Zamonaviy ofis bluzka. Ipak teginishli material.",
            'price': 199000,
            'box_price': 1800000,
            'box_quantity': 10,
            'category': ('Bluzka', 'ayol'),
            'season': 'universal',
            'stock_quantity': 150,
            'colors': ['Oq', 'Pushti', 'Moviy', 'Qora', 'Binafsha'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "A-Line Yubka",
            'name_ru': "Юбка А-силуэт",
            'name_en': "A-Line Skirt",
            'model_name': "A-Line",
            'variant': "Cotton Blend",
            'description_uz': "Klassik A-shaklidagi yubka. Ofis va kundalik uchun.",
            'price': 169000,
            'box_price': 1500000,
            'box_quantity': 10,
            'category': ('Yubka', 'ayol'),
            'season': 'universal',
            'stock_quantity': 130,
            'colors': ['Qora', "To'q ko'k", 'Jigarrang', 'Kulrang'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Qishki Palto",
            'name_ru': "Зимнее пальто",
            'name_en': "Winter Coat",
            'model_name': "Long Coat",
            'variant': "Cashmere Blend",
            'description_uz': "Issiq kashmir palto. Qish mavsumi uchun ideal.",
            'price': 690000,
            'box_price': None,
            'box_quantity': 1,
            'category': ('Palto', 'ayol'),
            'season': 'qish',
            'stock_quantity': 40,
            'colors': ['Qora', 'Jigarrang', 'Kulrang', 'Pushti'],
            'sizes': sizes_clothes,
        },
        {
            'name_uz': "Sport Kostyum",
            'name_ru': "Спортивный костюм",
            'name_en': "Sport Suit",
            'model_name': "Active Fit",
            'variant': "Fleece",
            'description_uz': "Qulay sport kostyum. Yugurish va mashg'ulotlar uchun.",
            'price': 320000,
            'box_price': 2900000,
            'box_quantity': 10,
            'category': ('Sport kiyim', 'ayol'),
            'season': 'universal',
            'stock_quantity': 90,
            'colors': ['Qora', 'Pushti', 'Kulrang', 'Moviy'],
            'sizes': sizes_clothes,
        },

        # ========== BOLALAR ==========
        {
            'name_uz': "Bolalar Futbolka",
            'name_ru': "Детская футболка",
            'name_en': "Kids T-Shirt",
            'model_name': "Fun Print",
            'variant': "Organic Cotton",
            'description_uz': "Bolalar uchun organik paxta futbolka. Qiziqarli rasmlar bilan.",
            'price': 79000,
            'box_price': 700000,
            'box_quantity': 10,
            'category': ('Futbolka', 'bola'),
            'season': 'yoz',
            'stock_quantity': 250,
            'colors': ['Qizil', 'Moviy', 'Sariq', 'Yashil', 'Oq', 'Pushti'],
            'sizes': sizes_kids,
        },
        {
            'name_uz': "Bolalar Jinsi Shim",
            'name_ru': "Детские джинсы",
            'name_en': "Kids Jeans",
            'model_name': "Comfort Fit",
            'variant': "Soft Denim",
            'description_uz': "Yumshoq jinsi shim. Bolalar uchun qulay va chidamli.",
            'price': 119000,
            'box_price': 1050000,
            'box_quantity': 10,
            'category': ('Shim', 'bola'),
            'season': 'universal',
            'stock_quantity': 180,
            'colors': ["Ko'k", "To'q ko'k", 'Qora'],
            'sizes': sizes_kids,
        },
        {
            'name_uz': "Bolalar Ko'ylak",
            'name_ru': "Детская рубашка",
            'name_en': "Kids Shirt",
            'model_name': "School Classic",
            'variant': "Easy Care",
            'description_uz': "Maktab uchun klassik ko'ylak. Dazmollanishi oson.",
            'price': 99000,
            'box_price': 880000,
            'box_quantity': 10,
            'category': ('Ko\'ylak', 'bola'),
            'season': 'universal',
            'stock_quantity': 200,
            'colors': ['Oq', 'Moviy', 'Pushti'],
            'sizes': sizes_kids,
        },
        {
            'name_uz': "Bolalar Kurtka",
            'name_ru': "Детская куртка",
            'name_en': "Kids Jacket",
            'model_name': "All Weather",
            'variant': "Waterproof",
            'description_uz': "Suv o'tkazmaydigan bolalar kurtkasi. Kuz-qish uchun.",
            'price': 259000,
            'box_price': 2300000,
            'box_quantity': 10,
            'category': ('Kurtka', 'bola'),
            'season': 'qish',
            'stock_quantity': 70,
            'colors': ["Ko'k", 'Qizil', 'Yashil', 'Qora'],
            'sizes': sizes_kids,
        },
        {
            'name_uz': "Bolalar Sport Kostyum",
            'name_ru': "Детский спортивный костюм",
            'name_en': "Kids Sport Suit",
            'model_name': "Junior Active",
            'variant': "Cotton Fleece",
            'description_uz': "Bolalar sport kostyumi. Mashg'ulot va dam olish uchun.",
            'price': 189000,
            'box_price': 1700000,
            'box_quantity': 10,
            'category': ('Sport kiyim', 'bola'),
            'season': 'universal',
            'stock_quantity': 110,
            'colors': ['Qora', 'Moviy', 'Qizil', 'Kulrang'],
            'sizes': sizes_kids,
        },
    ]

    count = 0
    for data in products_data:
        cat_name, cat_gender = data.pop('category')
        color_names = data.pop('colors')
        product_sizes = data.pop('sizes')

        cat = Category.objects.get(name_uz=cat_name, gender=cat_gender)

        product, created = Product.objects.get_or_create(
            name_uz=data['name_uz'],
            category=cat,
            defaults={
                'name_ru': data.get('name_ru', ''),
                'name_en': data.get('name_en', ''),
                'model_name': data.get('model_name', ''),
                'variant': data.get('variant', ''),
                'description_uz': data.get('description_uz', ''),
                'description_ru': data.get('description_ru', ''),
                'description_en': data.get('description_en', ''),
                'price': data['price'],
                'box_price': data.get('box_price'),
                'box_quantity': data.get('box_quantity', 1),
                'season': data.get('season', 'universal'),
                'stock_quantity': data.get('stock_quantity', 0),
                'in_stock': True,
            }
        )

        # Ranglarni qo'shish
        for cn in color_names:
            if cn in colors:
                product.colors.add(colors[cn])

        # O'lchamlarni qo'shish
        for s in product_sizes:
            product.sizes.add(s)

        if created:
            count += 1

    print(f"✅ {count} ta mahsulot yaratildi")


if __name__ == '__main__':
    print("🔄 Demo ma'lumotlar yuklanmoqda...\n")
    create_colors()
    create_sizes()
    create_categories()
    create_products()
    print("\n🎉 Barcha demo ma'lumotlar muvaffaqiyatli yuklandi!")
    print(f"\n📊 Statistika:")
    print(f"   🎨 Ranglar: {ProductColor.objects.count()}")
    print(f"   📏 O'lchamlar: {ProductSize.objects.count()}")
    print(f"   📂 Kategoriyalar: {Category.objects.count()}")
    print(f"   📦 Mahsulotlar: {Product.objects.count()}")
