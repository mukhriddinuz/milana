"""
main app URL konfiguratsiyasi.
Bot webhook va boshqaruv endpointlari.
"""
from django.urls import path
from . import views

app_name = 'main'

urlpatterns = [
    # Telegram webhook endpoint (POST)
    path('webhook/', views.telegram_webhook, name='webhook'),

    # Webhook boshqaruv (GET)
    path('set-webhook/', views.set_webhook, name='set-webhook'),
    path('remove-webhook/', views.remove_webhook, name='remove-webhook'),

    # Bot info (GET)
    path('info/', views.bot_info, name='bot-info'),

    # Gemini AI Chatbot API
    path('chatbot/', views.chatbot_api, name='chatbot-api'),
    path('chatbot/reset/', views.chatbot_reset, name='chatbot-reset'),
]
