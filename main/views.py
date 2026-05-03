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
from .notifications import notify_admin_error


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
        notify_admin_error(
            title='Telegram webhook xatoligi',
            error=e,
            extra=request.body.decode('utf-8', errors='ignore')[:1500]
        )

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
        notify_admin_error(
            title='Webhook o‘rnatish xatoligi',
            error=e,
            extra=f"webhook_url={webhook_url}"
        )
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
        notify_admin_error(
            title='Bot info xatoligi',
            error=e
        )
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)


# =============================================
# GEMINI AI CHATBOT API
# =============================================

@csrf_exempt
@require_POST
def chatbot_api(request):
    """
    Gemini AI Chatbot API endpoint.
    POST /bot/chatbot/

    Request body (JSON):
    {
        "message": "Erkaklar uchun qishki kurtka bormi?",
        "lang": "uz",           // ixtiyoriy, default: "uz"
        "session_id": "abc123"  // ixtiyoriy, sessiya uchun
    }

    Response (JSON):
    {
        "status": "ok",
        "response": "...",       // AI javobi
        "products": [1, 5, 12], // Tavsiya etilgan mahsulot IDlari
        "session_id": "abc123"
    }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON body'
        }, status=400)

    message = data.get('message', '').strip()
    if not message:
        return JsonResponse({
            'status': 'error',
            'message': 'message field is required'
        }, status=400)

    lang = data.get('lang', 'uz')
    if lang not in ('uz', 'ru', 'en'):
        lang = 'uz'

    session_id = data.get('session_id', None)

    from .chatbot import get_ai_response_api
    result = get_ai_response_api(
        message_text=message,
        lang=lang,
        session_id=session_id
    )

    return JsonResponse({
        'status': 'ok',
        'response': result['response'],
        'products': result['products'],
        'session_id': result['session_id'],
    })


@csrf_exempt
@require_POST
def chatbot_reset(request):
    """
    Chatbot sessiyasini tozalash.
    POST /bot/chatbot/reset/

    Request body (JSON):
    {
        "session_id": "abc123",
        "lang": "uz"
    }
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid JSON body'
        }, status=400)

    session_id = data.get('session_id', 'api_default')
    lang = data.get('lang', 'uz')

    from .chatbot import reset_chat_session
    reset_chat_session(user_id=f"api_{session_id}", lang=lang)

    return JsonResponse({
        'status': 'ok',
        'message': 'Chat session reset successfully'
    })
