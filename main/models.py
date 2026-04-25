"""
Milana Textile Bot — Database modellari.
Barcha modellar: BotUser, Category, Product, ProductImage,
ProductColor, ProductSize, Cart, CartItem, Order, OrderItem
"""
from django.db import models


# =============================================
# FOYDALANUVCHI
# =============================================

class BotUser(models.Model):
    """Telegram bot foydalanuvchisi"""
    LANGUAGE_CHOICES = [
        ('uz', "O'zbekcha"),
        ('ru', 'Русский'),
        ('en', 'English'),
    ]

    telegram_id = models.BigIntegerField(unique=True)
    first_name = models.CharField(max_length=150, blank=True, default='')
    last_name = models.CharField(max_length=150, blank=True, default='')
    username = models.CharField(max_length=150, blank=True, default='')
    language = models.CharField(max_length=5, choices=LANGUAGE_CHOICES, default='uz')
    phone = models.CharField(max_length=20, blank=True, default='')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Bot foydalanuvchi"
        verbose_name_plural = "Bot foydalanuvchilar"

    def __str__(self):
        return f"{self.first_name} ({self.telegram_id})"


# =============================================
# KATEGORIYALAR VA MAHSULOTLAR
# =============================================

class Category(models.Model):
    """Mahsulot kategoriyasi — har bir bo'lim (erkak/ayol/bola) uchun alohida"""
    GENDER_CHOICES = [
        ('erkak', 'Erkaklar'),
        ('ayol', 'Ayollar'),
        ('bola', 'Bolalar'),
    ]

    name_uz = models.CharField("Nomi (uz)", max_length=150)
    name_ru = models.CharField("Nomi (ru)", max_length=150, blank=True, default='')
    name_en = models.CharField("Nomi (en)", max_length=150, blank=True, default='')
    gender = models.CharField("Bo'lim", max_length=10, choices=GENDER_CHOICES)
    icon = models.CharField("Emoji/Icon", max_length=10, blank=True, default='👕')
    order = models.PositiveIntegerField("Tartib", default=0)
    is_active = models.BooleanField("Faol", default=True)

    class Meta:
        verbose_name = "Kategoriya"
        verbose_name_plural = "Kategoriyalar"
        ordering = ['gender', 'order']

    def __str__(self):
        return f"{self.get_gender_display()} — {self.name_uz}"

    def get_name(self, lang='uz'):
        """Tilga mos nom olish"""
        names = {'uz': self.name_uz, 'ru': self.name_ru, 'en': self.name_en}
        return names.get(lang) or self.name_uz


class ProductColor(models.Model):
    """Mahsulot ranglari"""
    name_uz = models.CharField("Rang (uz)", max_length=50)
    name_ru = models.CharField("Rang (ru)", max_length=50, blank=True, default='')
    name_en = models.CharField("Rang (en)", max_length=50, blank=True, default='')
    hex_code = models.CharField("HEX kodi", max_length=7, blank=True, default='',
                                help_text="Masalan: #FF0000")
    emoji = models.CharField("Emoji", max_length=10, blank=True, default='🔵')

    class Meta:
        verbose_name = "Rang"
        verbose_name_plural = "Ranglar"

    def __str__(self):
        return f"{self.emoji} {self.name_uz}"

    def get_name(self, lang='uz'):
        names = {'uz': self.name_uz, 'ru': self.name_ru, 'en': self.name_en}
        return names.get(lang) or self.name_uz


class ProductSize(models.Model):
    """Mahsulot o'lchamlari"""
    SIZE_TYPE_CHOICES = [
        ('clothes', 'Kiyim (S, M, L, XL...)'),
        ('shoes', 'Oyoq kiyim (36, 37, 38...)'),
        ('kids', 'Bolalar (1-2 yosh, 3-4 yosh...)'),
    ]

    name = models.CharField("O'lcham nomi", max_length=20)  # S, M, L, XL, 38, 39...
    size_type = models.CharField("Turi", max_length=20, choices=SIZE_TYPE_CHOICES, default='clothes')
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "O'lcham"
        verbose_name_plural = "O'lchamlar"
        ordering = ['size_type', 'order']

    def __str__(self):
        return self.name


class Product(models.Model):
    """Asosiy mahsulot modeli"""
    SEASON_CHOICES = [
        ('bahor', 'Bahor'),
        ('yoz', 'Yoz'),
        ('kuz', 'Kuz'),
        ('qish', 'Qish'),
        ('universal', 'Universal'),
    ]

    # Asosiy ma'lumotlar
    name_uz = models.CharField("Nomi (uz)", max_length=200)
    name_ru = models.CharField("Nomi (ru)", max_length=200, blank=True, default='')
    name_en = models.CharField("Nomi (en)", max_length=200, blank=True, default='')

    model_name = models.CharField("Model nomi", max_length=100, blank=True, default='',
                                  help_text="Masalan: Classic Fit, Slim Fit")
    variant = models.CharField("Variant", max_length=100, blank=True, default='',
                               help_text="Masalan: Premium, Standard")

    description_uz = models.TextField("Tavsif (uz)", blank=True, default='')
    description_ru = models.TextField("Tavsif (ru)", blank=True, default='')
    description_en = models.TextField("Tavsif (en)", blank=True, default='')

    # Narxlar
    price = models.DecimalField("Dona narxi", max_digits=12, decimal_places=0)
    box_price = models.DecimalField("Karobka narxi", max_digits=12, decimal_places=0,
                                    null=True, blank=True,
                                    help_text="Karobkada nechta dona bo'lsa, shu narx")
    box_quantity = models.PositiveIntegerField("Karobkadagi soni", default=1,
                                              help_text="1 karobkada nechta dona bor")

    # Bog'lanishlar
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products', verbose_name="Kategoriya")
    colors = models.ManyToManyField(ProductColor, blank=True,
                                   related_name='products', verbose_name="Ranglar")
    sizes = models.ManyToManyField(ProductSize, blank=True,
                                  related_name='products', verbose_name="O'lchamlar")

    # Qo'shimcha
    season = models.CharField("Mavsum", max_length=15, choices=SEASON_CHOICES, default='universal')
    in_stock = models.BooleanField("Sotuvda bor", default=True)
    stock_quantity = models.PositiveIntegerField("Ombordagi soni", default=0)

    # Asosiy rasm
    main_image = models.ImageField("Asosiy rasm", upload_to='products/', blank=True, null=True)

    created_at = models.DateTimeField("Yaratilgan", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan", auto_now=True)

    class Meta:
        verbose_name = "Mahsulot"
        verbose_name_plural = "Mahsulotlar"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name_uz} ({self.category})"

    def get_name(self, lang='uz'):
        names = {'uz': self.name_uz, 'ru': self.name_ru, 'en': self.name_en}
        return names.get(lang) or self.name_uz

    def get_description(self, lang='uz'):
        descs = {'uz': self.description_uz, 'ru': self.description_ru, 'en': self.description_en}
        return descs.get(lang) or self.description_uz

    def get_gender(self):
        return self.category.gender


class ProductImage(models.Model):
    """Mahsulotning qo'shimcha rasmlari"""
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images', verbose_name="Mahsulot")
    image = models.ImageField("Rasm", upload_to='products/')
    order = models.PositiveIntegerField("Tartib", default=0)

    class Meta:
        verbose_name = "Mahsulot rasmi"
        verbose_name_plural = "Mahsulot rasmlari"
        ordering = ['order']

    def __str__(self):
        return f"Rasm #{self.order} — {self.product.name_uz}"


# =============================================
# SAVAT VA BUYURTMA
# =============================================

class Cart(models.Model):
    """Foydalanuvchi savati"""
    user = models.OneToOneField(BotUser, on_delete=models.CASCADE,
                                related_name='cart', verbose_name="Foydalanuvchi")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Savat"
        verbose_name_plural = "Savatlar"

    def __str__(self):
        return f"Savat — {self.user}"

    def get_total(self):
        """Savatdagi jami narx"""
        total = 0
        for item in self.items.all():
            total += item.get_subtotal()
        return total

    def get_items_count(self):
        """Savatdagi mahsulotlar soni"""
        return self.items.count()


class CartItem(models.Model):
    """Savatdagi mahsulot"""
    PURCHASE_TYPE_CHOICES = [
        ('dona', 'Donalik'),
        ('karobka', 'Karobkalik'),
    ]

    cart = models.ForeignKey(Cart, on_delete=models.CASCADE,
                             related_name='items', verbose_name="Savat")
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                verbose_name="Mahsulot")
    color = models.ForeignKey(ProductColor, on_delete=models.SET_NULL,
                              null=True, blank=True, verbose_name="Rang")
    size = models.ForeignKey(ProductSize, on_delete=models.SET_NULL,
                             null=True, blank=True, verbose_name="O'lcham")
    quantity = models.PositiveIntegerField("Soni", default=1)
    purchase_type = models.CharField("Sotib olish turi", max_length=10,
                                     choices=PURCHASE_TYPE_CHOICES, default='dona')

    class Meta:
        verbose_name = "Savat elementi"
        verbose_name_plural = "Savat elementlari"

    def __str__(self):
        return f"{self.product.name_uz} x{self.quantity}"

    def get_subtotal(self):
        """Mahsulot jami narxi"""
        if self.purchase_type == 'karobka' and self.product.box_price:
            return self.product.box_price * self.quantity
        return self.product.price * self.quantity


class Order(models.Model):
    """Buyurtma"""
    STATUS_CHOICES = [
        ('yangi', '🆕 Yangi'),
        ('tasdiqlangan', '✅ Tasdiqlangan'),
        ('yetkazilmoqda', '🚚 Yetkazilmoqda'),
        ('yetkazildi', '📦 Yetkazildi'),
        ('bekor', '❌ Bekor qilingan'),
    ]

    user = models.ForeignKey(BotUser, on_delete=models.CASCADE,
                             related_name='orders', verbose_name="Foydalanuvchi")
    total_price = models.DecimalField("Jami narx", max_digits=12, decimal_places=0, default=0)
    status = models.CharField("Status", max_length=20, choices=STATUS_CHOICES, default='yangi')
    phone = models.CharField("Telefon", max_length=20, blank=True, default='')
    address = models.TextField("Manzil", blank=True, default='')
    note = models.TextField("Izoh", blank=True, default='')
    created_at = models.DateTimeField("Yaratilgan", auto_now_add=True)
    updated_at = models.DateTimeField("Yangilangan", auto_now=True)

    class Meta:
        verbose_name = "Buyurtma"
        verbose_name_plural = "Buyurtmalar"
        ordering = ['-created_at']

    def __str__(self):
        return f"Buyurtma #{self.pk} — {self.user}"


class OrderItem(models.Model):
    """Buyurtma elementi"""
    PURCHASE_TYPE_CHOICES = [
        ('dona', 'Donalik'),
        ('karobka', 'Karobkalik'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE,
                              related_name='items', verbose_name="Buyurtma")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL,
                                null=True, verbose_name="Mahsulot")
    product_name = models.CharField("Mahsulot nomi", max_length=200)
    color_name = models.CharField("Rang", max_length=50, blank=True, default='')
    size_name = models.CharField("O'lcham", max_length=20, blank=True, default='')
    quantity = models.PositiveIntegerField("Soni", default=1)
    price = models.DecimalField("Narx", max_digits=12, decimal_places=0)
    purchase_type = models.CharField("Sotib olish turi", max_length=10,
                                     choices=PURCHASE_TYPE_CHOICES, default='dona')

    class Meta:
        verbose_name = "Buyurtma elementi"
        verbose_name_plural = "Buyurtma elementlari"

    def __str__(self):
        return f"{self.product_name} x{self.quantity}"

    def get_subtotal(self):
        return self.price * self.quantity
