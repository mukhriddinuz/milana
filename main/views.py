"""
Webhook endpoint va bot boshqaruv view'lari.
Telegram serveridan kelgan update'larni qabul qiladi.
"""
import json

import telebot
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.conf import settings

from .bot import bot


@csrf_exempt
@require_POST
def telegram_webhook(request):
    """
    Telegram webhook endpoint.
    Telegram serveridan POST orqali kelgan update'larni
    bot.process_new_updates() ga uzatadi.
    """
    try:
        json_data = json.loads(request.body)
        update = telebot.types.Update.de_json(json_data)
        bot.process_new_updates([update])
    except Exception as e:
        # Log the error but return 200 to prevent Telegram from retrying
        print(f"[WEBHOOK ERROR] {e}")

    return JsonResponse({'status': 'ok'})


@require_GET
def set_webhook(request):
    """
    Webhookni o'rnatish uchun GET endpoint.
    Brauzerdan yoki curl bilan chaqirish mumkin:
    GET /bot/set-webhook/
    """
    webhook_url = f"{settings.TELEGRAM_WEBHOOK_URL}/bot/webhook/"

    try:
        # Avvalgi webhookni o'chirish
        try:
            bot.remove_webhook()
        except Exception:
            pass

        # Yangi webhook o'rnatish
        import time
        time.sleep(1)
        result = bot.set_webhook(url=webhook_url)

        if result:
            return JsonResponse({
                'status': 'success',
                'message': f'Webhook muvaffaqiyatli o\'rnatildi: {webhook_url}'
            })
        else:
            return JsonResponse({
                'status': 'error',
                'message': 'Webhook o\'rnatishda xatolik yuz berdi'
            }, status=500)
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Xatolik: {str(e)}'
        }, status=500)


@require_GET
def remove_webhook(request):
    """
    Webhookni o'chirish uchun GET endpoint.
    GET /bot/remove-webhook/
    """
    bot.remove_webhook()
    return JsonResponse({
        'status': 'success',
        'message': 'Webhook muvaffaqiyatli o\'chirildi'
    })


@require_GET
def bot_info(request):
    """
    Bot haqida ma'lumot olish.
    GET /bot/info/
    """
    try:
        me = bot.get_me()
        return JsonResponse({
            'id': me.id,
            'username': me.username,
            'first_name': me.first_name,
            'is_bot': me.is_bot,
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
