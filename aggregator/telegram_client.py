from telethon.sync import TelegramClient
from django.conf import settings
import os
import logging

logger = logging.getLogger(__name__)

# Use absolute path for session file to avoid path issues
SESSION_FILE = os.path.join(settings.BASE_DIR, 'telegram_session')
API_ID = 32729516
API_HASH = 'b9cbc7204ce06cb5d678580309dca6c9'

_client = None

def get_telegram_client():
    global _client
    if _client is None:
        try:
            _client = TelegramClient(SESSION_FILE, API_ID, API_HASH)
            _client.connect()
        except Exception as e:
            logger.error(f"Failed to initialize Telegram Client: {e}")
            return None
    return _client
