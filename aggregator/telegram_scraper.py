from .telegram_client import get_telegram_client
from telethon.tl.types import MessageMediaPhoto
import logging
import os
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

def save_telegram_image(message):
    """
    Downloads image from message and returns the relative URL.
    """
    if not message.media or not isinstance(message.media, MessageMediaPhoto):
        return None
        
    try:
        # Create directory if not exists
        media_root = os.path.join(settings.MEDIA_ROOT, 'telegram_images')
        os.makedirs(media_root, exist_ok=True)
        
        # Filename: msg_id.jpg
        # We assume channel ID is unique enough combined with msg ID or just handle overwrite
        filename = f"{message.chat_id}_{message.id}.jpg"
        filepath = os.path.join(media_root, filename)
        
        # Download if not exists
        if not os.path.exists(filepath):
            message.download_media(file=filepath)
            
        return f"/media/telegram_images/{filename}"
    except Exception as e:
        logger.error(f"Error downloading image: {e}")
        return None

def fetch_telegram_posts(channel_url, limit=10):
    client = get_telegram_client()
    if not client:
        return []
        
    if not client.is_user_authorized():
        logger.error("Telegram client not authorized. Run telegram_setup.py first.")
        return []

    posts = []
    try:
        # Extract username
        # Expected formats: https://t.me/username, t.me/username, username
        if 't.me/s/' in channel_url:
             username = channel_url.split('t.me/s/')[-1].strip('/')
        elif 't.me/' in channel_url:
            username = channel_url.split('t.me/')[-1].strip('/')
        else:
            username = channel_url

        # Get messages
        messages = client.get_messages(username, limit=limit)
        
        for message in messages:
            # Skip empty messages (service messages etc)
            if not message.message and not message.media:
                continue
                
            # Construct permalink
            # Public channel link: https://t.me/username/id
            permalink = f"https://t.me/{username}/{message.id}"
            
            # Download Image
            image_url = save_telegram_image(message)
            
            posts.append({
                'title': 'Telegram Post', # Telegram posts don't typically have titles
                'text': message.message,
                'image_url': image_url,
                'permalink': permalink,
                'published_at': message.date
            })
            
    except Exception as e:
        logger.error(f"Error fetching telegram channel {channel_url}: {e}")

    return posts
