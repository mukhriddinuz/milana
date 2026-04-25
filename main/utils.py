"""Yordamchi funksiyalar"""
from .models import BotUser, Cart
from .translations import get_text


def get_or_create_user(message):
    """Foydalanuvchini olish yoki yaratish"""
    user = message.from_user
    bot_user, created = BotUser.objects.get_or_create(
        telegram_id=user.id,
        defaults={
            'first_name': user.first_name or '',
            'last_name': user.last_name or '',
            'username': user.username or '',
        }
    )
    if not created:
        bot_user.first_name = user.first_name or ''
        bot_user.last_name = user.last_name or ''
        bot_user.username = user.username or ''
        bot_user.save(update_fields=['first_name', 'last_name', 'username'])
    return bot_user


def get_user_lang(telegram_id):
    """Foydalanuvchi tilini olish"""
    try:
        return BotUser.objects.get(telegram_id=telegram_id).language
    except BotUser.DoesNotExist:
        return 'uz'


def get_cart(bot_user):
    """Foydalanuvchi savatini olish yoki yaratish"""
    cart, _ = Cart.objects.get_or_create(user=bot_user)
    return cart


def t(key, telegram_id):
    """Qisqacha tarjima funksiyasi"""
    return get_text(key, get_user_lang(telegram_id))


def format_price(price):
    """Narxni formatlash: 1000000 -> 1,000,000"""
    return f"{int(price):,}".replace(",", " ")
