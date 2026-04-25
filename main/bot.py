"""
Telegram bot instance.
telebot (pyTelegramBotAPI) kutubxonasi bilan ishlaydi.
"""
import telebot
from django.conf import settings


# Bot instance yaratish
token = settings.TELEGRAM_BOT_TOKEN
if not token or ':' not in token:
    # Token yo'q bo'lsa, placeholder bilan yaratish
    # (makemigrations va boshqa Django buyruqlari uchun)
    import types as _types
    bot = telebot.TeleBot.__new__(telebot.TeleBot)
    bot.token = 'placeholder:token'
    bot.message_handlers = []
    bot.edited_message_handlers = []
    bot.channel_post_handlers = []
    bot.edited_channel_post_handlers = []
    bot.inline_handlers = []
    bot.chosen_inline_handlers = []
    bot.callback_query_handlers = []
    bot.shipping_query_handlers = []
    bot.pre_checkout_query_handlers = []
    bot.poll_handlers = []
    bot.poll_answer_handlers = []
    bot.my_chat_member_handlers = []
    bot.chat_member_handlers = []
    bot.chat_join_request_handlers = []
    bot.message_reaction_handlers = []
    bot.message_reaction_count_handlers = []
    bot.custom_filters = {}
    bot.state_handlers = []
    bot.threaded = False
    bot._user_states = {}
    print("[BOT WARNING] TELEGRAM_BOT_TOKEN topilmadi! Bot ishlamaydi.")
else:
    bot = telebot.TeleBot(token, threaded=False)

# Import handlers (bot yaratilgandan keyin)
try:
    from . import handlers  # noqa: E402, F401
except Exception as e:
    print(f"[HANDLERS ERROR] {e}")
