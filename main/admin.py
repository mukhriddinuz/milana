"""
Milana Textile Bot — Admin panel konfiguratsiyasi.
Barcha modellar uchun admin panel sozlamalari.
"""
from django.contrib import admin
from .models import (
    BotUser, Category, ProductColor, ProductSize,
    Product, ProductImage, Cart, CartItem,
    Order, OrderItem
)


# =============================================
# INLINE MODELLAR
# =============================================

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ['image', 'order']


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['get_subtotal']
    fields = ['product', 'color', 'size', 'quantity', 'purchase_type', 'get_subtotal']

    def get_subtotal(self, obj):
        return f"{obj.get_subtotal():,.0f} so'm"
    get_subtotal.short_description = "Jami"


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['get_subtotal']
    fields = ['product_name', 'color_name', 'size_name', 'quantity',
              'price', 'purchase_type', 'get_subtotal']

    def get_subtotal(self, obj):
        return f"{obj.get_subtotal():,.0f} so'm"
    get_subtotal.short_description = "Jami"


# =============================================
# MODEL ADMIN'LAR
# =============================================

@admin.register(BotUser)
class BotUserAdmin(admin.ModelAdmin):
    list_display = ['telegram_id', 'first_name', 'last_name', 'username', 'language', 'phone', 'created_at']
    list_filter = ['language', 'created_at']
    search_fields = ['telegram_id', 'first_name', 'username', 'phone']
    readonly_fields = ['telegram_id', 'created_at']


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'gender', 'icon', 'order', 'is_active']
    list_filter = ['gender', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['name_uz', 'name_ru', 'name_en']


@admin.register(ProductColor)
class ProductColorAdmin(admin.ModelAdmin):
    list_display = ['emoji', 'name_uz', 'name_ru', 'hex_code']
    search_fields = ['name_uz', 'name_ru']


@admin.register(ProductSize)
class ProductSizeAdmin(admin.ModelAdmin):
    list_display = ['name', 'size_type', 'order']
    list_filter = ['size_type']
    list_editable = ['order']


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name_uz', 'model_name', 'category', 'price', 'box_price',
                    'in_stock', 'stock_quantity', 'created_at']
    list_filter = ['category__gender', 'category', 'season', 'in_stock', 'colors']
    search_fields = ['name_uz', 'name_ru', 'name_en', 'model_name', 'variant']
    filter_horizontal = ['colors', 'sizes']
    inlines = [ProductImageInline]
    fieldsets = (
        ("Asosiy ma'lumotlar", {
            'fields': ('name_uz', 'name_ru', 'name_en', 'model_name', 'variant', 'category')
        }),
        ("Tavsif", {
            'fields': ('description_uz', 'description_ru', 'description_en'),
            'classes': ('collapse',),
        }),
        ("Narxlar va ombor", {
            'fields': ('price', 'box_price', 'box_quantity', 'in_stock', 'stock_quantity')
        }),
        ("Xususiyatlar", {
            'fields': ('colors', 'sizes', 'season', 'main_image')
        }),
    )


@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ['product', 'order']
    list_filter = ['product__category']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'get_items_count', 'get_total', 'updated_at']
    inlines = [CartItemInline]

    def get_items_count(self, obj):
        return obj.get_items_count()
    get_items_count.short_description = "Mahsulotlar soni"

    def get_total(self, obj):
        return f"{obj.get_total():,.0f} so'm"
    get_total.short_description = "Jami narx"


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'total_price', 'status', 'phone', 'created_at']
    list_filter = ['status', 'created_at']
    list_editable = ['status']
    search_fields = ['user__first_name', 'user__telegram_id', 'phone']
    inlines = [OrderItemInline]
    readonly_fields = ['created_at', 'updated_at']
