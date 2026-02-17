import requests
from bs4 import BeautifulSoup
from datetime import datetime
from django.utils import timezone
import logging
import re

logger = logging.getLogger(__name__)

def fetch_telegram_posts(channel_username, limit=10):
    """
    Scrapes public Telegram channel preview for posts.
    :param channel_username: Username of the channel (e.g., 'mrattkya')
    :param limit: Number of posts to attempt to fetch
    :return: List of dicts with post data
    """
    # Clean username
    channel_username = channel_username.replace('@', '').replace('https://t.me/', '').replace('s/', '')
    if channel_username.endswith('/'):
        channel_username = channel_username[:-1]

    url = f"https://t.me/s/{channel_username}"
    logger.info(f"Scraping Telegram: {url}")

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
    except Exception as e:
        logger.error(f"Failed to fetch Telegram page: {e}")
        return []

    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Telegram web preview messages are in .tgme_widget_message
    messages = soup.find_all('div', class_='tgme_widget_message', limit=limit)
    
    posts = []
    for msg in messages:
        try:
            # 1. Extract Text
            text_elem = msg.find('div', class_='tgme_widget_message_text')
            text = text_elem.get_text(separator="\n", strip=True) if text_elem else ""
            
            # 2. Extract Image
            image_url = None
            photo_wrap = msg.find('a', class_='tgme_widget_message_photo_wrap')
            if photo_wrap:
                style = photo_wrap.get('style', '')
                # Extract url('...') from background-image
                match = re.search(r"url\('?(.*?)'?\)", style)
                if match:
                    image_url = match.group(1)
            
            # 3. Extract Date and Link
            date_elem = msg.find('a', class_='tgme_widget_message_date')
            if not date_elem:
                continue

            post_url = date_elem.get('href') # e.g., https://t.me/channel/123
            
            time_elem = date_elem.find('time')
            if time_elem and time_elem.get('datetime'):
                dt_str = time_elem.get('datetime')
                # Format is roughly ISO: 2023-10-27T08:30:19+00:00
                try:
                    published_date = datetime.fromisoformat(dt_str)
                    if timezone.is_naive(published_date):
                         published_date = timezone.make_aware(published_date)
                except ValueError:
                    published_date = timezone.now()
            else:
                 published_date = timezone.now()

            # Skip empty posts (no text/no image)
            if not text and not image_url:
                continue
                
            # Create title from first line or truncated text
            title = text.split('\n')[0][:100] if text else "Telegram Post"
            if len(title) < 5 and image_url:
                title = "Photo Update"

            posts.append({
                'title': title,
                'content': text,
                'image_url': image_url,
                'url': post_url,
                'published_date': published_date
            })
            
        except Exception as e:
            logger.error(f"Error parsing a telegram message: {e}")
            continue

    return posts
