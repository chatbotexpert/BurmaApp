import feedparser
import logging
import sys
from datetime import datetime
import requests
from bs4 import BeautifulSoup
from time import mktime
from django.utils import timezone
from .models import Source, Post
from .translator import translate_text

# Configure logging to stdout
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[logging.StreamHandler(sys.stdout)]
)
logger = logging.getLogger(__name__)

def _extract_rss_image(entry):
    """
    Helper to extract image URL from an RSS entry
    """
    # 1. Try media_content
    if 'media_content' in entry:
        for media in entry.media_content:
            if media.get('medium') == 'image' and 'url' in media:
                return media['url']
    
    # 2. Try media_thumbnail
    if 'media_thumbnail' in entry:
        for media in entry.media_thumbnail:
            if 'url' in media:
                return media['url']
                
    # 3. Try enclosures
    if 'enclosures' in entry:
        for enclosure in entry.enclosures:
            if enclosure.get('type', '').startswith('image/') and 'url' in enclosure:
                return enclosure['url']
                
    # 4. Try parsing HTML content for <img> tags
    content = ''
    if 'content' in entry:
        content = entry.content[0].value
    elif 'summary' in entry:
        content = entry.summary
        
    if content:
        soup = BeautifulSoup(content, 'html.parser')
        img = soup.find('img')
        if img and img.get('src'):
            return img['src']
            
    return None

def _fetch_og_image(url):
    """
    Helper to fetch Open Graph image from a URL
    """
    try:
        # User-Agent is important to avoid being blocked
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=5)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            og_image = soup.find('meta', property='og:image')
            if og_image and og_image.get('content'):
                return og_image['content']
                
            # Fallback to twitter:image
            twitter_image = soup.find('meta', name='twitter:image')
            if twitter_image and twitter_image.get('content'):
                return twitter_image['content']
    except Exception as e:
        print(f"Error fetching OG image for {url}: {e}")
    return None

def _is_valid_image(url):
    """
    Checks if an image URL is valid and substantial (not an emoji or pixel).
    """
    if not url:
        return False
    
    # Filter out Facebook emojis and generic assets
    if "emoji.php" in url or "static.xx.fbcdn.net" in url:
        return False
        
    return True

def fetch_rss(source):
    """
    Fetch and parse RSS feed
    """
    print(f"Fetching RSS feed: {source.url}")
    try:
        # Use requests with a standard browser User-Agent to bypass basic bot protection
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        }
        response = requests.get(source.url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Parse the raw XML string using feedparser
        feed = feedparser.parse(response.content)
        
        # Check for bozo (malformed feed) but try to process anyway if entries exist
        if hasattr(feed, 'bozo_exception'):
             logger.warning(f"Feed Bozo Exception for {source.name}: {feed.bozo_exception}")

        new_posts_count = 0
        
        for entry in feed.entries[:10]: # Check top 10 entries
            # Check if post already exists
            if Post.objects.filter(url=entry.link).exists():
                continue
                
            # Parse date
            published_date = timezone.now()
            if hasattr(entry, 'published_parsed'):
                 published_date = datetime.fromtimestamp(mktime(entry.published_parsed))
                 published_date = timezone.make_aware(published_date)

            # Extract content
            content = ""
            title = entry.title
            
            # Extract Image
            image_url = _extract_rss_image(entry)
            
            # Fallback: Fetch OG image if no image found in feed
            if not image_url:
                 print(f"No RSS image for {entry.title}, trying OG fetch...")
                 image_url = _fetch_og_image(entry.link)

            if not _is_valid_image(image_url):
                 image_url = None
            
            # Fallback: If content is empty, use title
            if not content and title:
                content = title

            # Translate
            trans_title = translate_text(title)
            trans_content = translate_text(content)
            
            # Save
            try:
                Post.objects.create(
                    source=source,
                    title=trans_title,
                    original_content=content,
                    translated_content=trans_content, # Changed: Only save content, not title
                    url=entry.link,
                    image_url=image_url,
                    published_date=published_date
                )
                new_posts_count += 1
            except Exception as e:
                logger.error(f"Error saving post {entry.link}: {e}")
                
        return new_posts_count
    except Exception as e:
        logger.error(f"Error fetching RSS {source.url}: {e}")
        return 0

try:
    from .fb_scraper import fetch_posts
except ImportError as e:
    fetch_posts = None
    logger.error(f"Playwright scraper import error: {e}")

def fetch_facebook(source):
    """
    Fetches posts from a public Facebook page using Playwright.
    """
    logger.info(f"Fetching Facebook: {source.name}")
    
    if not fetch_posts:
        logger.error("Playwright scraper module missing.")
        return 0

    new_posts_count = 0
    
    try:
        # Fetch posts using the new scraper
        # It returns a list of dicts: title, text, image_url, permalink, published_at
        posts = fetch_posts(source.url, limit=15)
        
        for post in posts:
            post_url = post.get('permalink')
            if not post_url:
                continue

            if Post.objects.filter(url=post_url).exists():
                continue
                
            content = post.get('text', '')
            title = post.get('title', 'Facebook Post')
            image_url = post.get('image_url')
            
            if not _is_valid_image(image_url):
                image_url = None
            
            if not content and title == 'Post' and not image_url:
                continue

            # Fallback: If content is empty but we have a title, use title as content
            if not content and title != 'Facebook Post':
                content = title
                
            published_date = post.get('published_at')
            if not published_date:
                published_date = timezone.now()
            elif timezone.is_naive(published_date):
                 published_date = timezone.make_aware(published_date)

            # Translate
            trans_content = translate_text(content)
            trans_title = translate_text(title)
            
            try:
                Post.objects.create(
                    source=source,
                    title=trans_title,
                    original_content=content,
                    translated_content=trans_content, # Changed: Only save content, not title
                    url=post_url,
                    image_url=image_url,
                    published_date=published_date
                )
                new_posts_count += 1
            except Exception as e:
                 logger.error(f"Save Error: {e}")
                
    except Exception as e:
        logger.error(f"Facebook Scraping Error for {source.url}: {e}")
        
    return new_posts_count

try:
    from .telegram_scraper import fetch_telegram_posts
except ImportError as e:
    fetch_telegram_posts = None
    logger.error(f"Telegram scraper import error: {e}")

try:
    from .twitter_scraper import fetch_twitter_posts
except ImportError as e:
    fetch_twitter_posts = None
    logger.error(f"Twitter scraper import error: {e}")

def fetch_telegram(source):
    """
    Fetches posts from a public Telegram channel.
    """
    logger.info(f"Fetching Telegram: {source.name}")
    
    if not fetch_telegram_posts:
        logger.error("Telegram scraper module missing.")
        return 0

    new_posts_count = 0
    
    try:
        # Fetch posts
        posts = fetch_telegram_posts(source.url, limit=20)
        
        for post in posts:
            post_url = post.get('permalink') # telegram scraper returns permalink
            if not post_url or Post.objects.filter(url=post_url).exists():
                continue
                
            content = post.get('text', '')
            title = post.get('title', 'Telegram Post')
            image_url = post.get('image_url')
            published_date = post.get('published_at', timezone.now())

            if not content:
                content = title

            # Translate
            trans_content = translate_text(content)
            trans_title = translate_text(title)
            
            try:
                Post.objects.create(
                    source=source,
                    title=trans_title,
                    original_content=content,
                    translated_content=trans_content,
                    url=post_url,
                    image_url=image_url,
                    published_date=published_date
                )
                new_posts_count += 1
            except Exception as e:
                logger.error(f"Save Error: {e}")
                
    except Exception as e:
        logger.error(f"Telegram Scraping Error for {source.url}: {e}")
        
    return new_posts_count

def fetch_twitter(source):
    """
    Fetches posts from a public Twitter profile.
    """
    logger.info(f"Fetching Twitter: {source.name}")
    
    if not fetch_twitter_posts:
        logger.error("Twitter scraper module missing.")
        return 0

    new_posts_count = 0
    
    try:
        # Fetch posts
        posts = fetch_twitter_posts(source.url, limit=15)
        
        for post in posts:
            post_url = post.get('permalink')
            if not post_url or Post.objects.filter(url=post_url).exists():
                continue
                
            content = post.get('text', '')
            title = post.get('title', 'Twitter Post')
            image_url = post.get('image_url')
            published_date = post.get('published_at', timezone.now())

            if not content:
                content = title

            # Translate
            trans_content = translate_text(content)
            trans_title = translate_text(title)
            
            try:
                Post.objects.create(
                    source=source,
                    title=trans_title,
                    original_content=content,
                    translated_content=trans_content,
                    url=post_url,
                    image_url=image_url,
                    published_date=published_date
                )
                new_posts_count += 1
            except Exception as e:
                logger.error(f"Save Error: {e}")
                
    except Exception as e:
        logger.error(f"Twitter Scraping Error for {source.url}: {e}")
        
    return new_posts_count

def run_scraping():
    sources = Source.objects.filter(is_active=True)
    total_new = 0
    print(f"DEBUG: Found {sources.count()} active sources")
    
    for source in sources:
        if source.source_type == 'RSS':
            total_new += fetch_rss(source)
        elif source.source_type == 'FACEBOOK':
             total_new += fetch_facebook(source)
        elif source.source_type == 'TELEGRAM':
             total_new += fetch_telegram(source)
        elif source.source_type == 'TWITTER':
             total_new += fetch_twitter(source)
        else:
            print(f"DEBUG: Unknown source type: {source.source_type}")
            
    return total_new
