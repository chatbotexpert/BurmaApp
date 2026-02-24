from telethon.sync import TelegramClient
from django.conf import settings
import os
import logging
import socks
import time

logger = logging.getLogger(__name__)

# Use absolute path for session file to avoid path issues
SESSION_FILE = os.path.join(settings.BASE_DIR, 'telegram_session')
API_ID = 32729516
API_HASH = 'b9cbc7204ce06cb5d678580309dca6c9'

_client = None

def get_telegram_client():
    global _client
    if _client is None:
        # Check for proxy in environment
        proxy = None
        proxy_addr = os.getenv('TELEGRAM_PROXY_ADDR')
        proxy_port = os.getenv('TELEGRAM_PROXY_PORT')
        
        if proxy_addr and proxy_port:
            try:
                proxy = (socks.SOCKS5, proxy_addr, int(proxy_port))
                logger.info(f"Using Telegram Proxy: {proxy_addr}:{proxy_port}")
            except ValueError:
                logger.error("Invalid TELEGRAM_PROXY_PORT environment variable.")

        try:
            _client = TelegramClient(SESSION_FILE, API_ID, API_HASH, proxy=proxy)
            
            # Retry logic for connection
            connected = False
            for attempt in range(1, 4):
                try:
                    logger.info(f"Connecting to Telegram (Attempt {attempt}/3)...")
                    _client.connect()
                    connected = True
                    break
                except Exception as e:
                    logger.warning(f"Telegram connection attempt {attempt} failed: {e}")
                    if attempt < 3:
                        time.sleep(2 * attempt)
            
            if not connected:
                logger.error("Failed to connect to Telegram after multiple attempts.")
                _client = None
                return None
                
        except Exception as e:
            logger.error(f"Failed to initialize Telegram Client: {e}")
            return None
    return _client
