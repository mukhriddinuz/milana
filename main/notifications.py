"""Admin xabarnomalari uchun helper funksiyalar."""
import html
import traceback

from django.conf import settings

from .bot import bot


def notify_admin_error(title, error, extra=None):
    """Xatolik tafsilotlarini admin Telegram akkauntiga yuborish."""
    admin_chat_id = getattr(settings, 'ADMIN_TELEGRAM_ID', 0)
    if not admin_chat_id:
        return False

    error_text = html.escape(str(error))
    traceback_text = html.escape(traceback.format_exc())

    parts = [
        f"<b>{html.escape(title)}</b>",
        f"<b>Error:</b> <code>{error_text[:1200]}</code>",
    ]

    if extra:
        parts.append(f"<b>Context:</b>\n<code>{html.escape(extra)[:1200]}</code>")

    if traceback_text and traceback_text != 'NoneType: None\n':
        parts.append(f"<b>Traceback:</b>\n<code>{traceback_text[:2500]}</code>")

    message = "\n\n".join(parts)

    try:
        bot.send_message(admin_chat_id, message[:4096], parse_mode='HTML')
        return True
    except Exception as notify_error:
        print(f"[ADMIN NOTIFY ERROR] {notify_error}")
        return False
