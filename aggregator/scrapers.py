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
from newspaper import Article

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
        response.encoding = response.apparent_encoding
        
        # Parse the decoded string using feedparser
        feed = feedparser.parse(response.text)
        
        # Check for bozo (malformed feed) but try to process anyway if entries exist
        if hasattr(feed, 'bozo_exception'):
             logger.warning(f"Feed Bozo Exception for {source.name}: {feed.bozo_exception}")

        # Auto-detect source platform from the feed link if it exists
        feed_link = feed.feed.get('link', '').lower()
        if 'facebook.com' in feed_link and source.source_type != 'FACEBOOK':
            source.source_type = 'FACEBOOK'
            source.save(update_fields=['source_type'])
        elif ('twitter.com' in feed_link or 'x.com' in feed_link) and source.source_type != 'TWITTER':
            source.source_type = 'TWITTER'
            source.save(update_fields=['source_type'])
        elif 't.me' in feed_link and source.source_type != 'TELEGRAM':
            source.source_type = 'TELEGRAM'
            source.save(update_fields=['source_type'])

        new_posts_count = 0
        
        # Fetch all entries in the feed
        for entry in feed.entries: 
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
            
            # For Social Sources (Facebook, Twitter, Telegram) via RSS, prioritize the feed content
            # since trying to scrape the link directly usually hits a login wall or bot detection.
            is_social = source.source_type in ['FACEBOOK', 'TWITTER', 'TELEGRAM']
            
            if is_social:
                if 'content' in entry:
                    soup = BeautifulSoup(entry.content[0].value, 'html.parser')
                    content = soup.get_text(separator='\n', strip=True)
                elif 'summary' in entry:
                    soup = BeautifulSoup(entry.summary, 'html.parser')
                    content = soup.get_text(separator='\n', strip=True)
                
                logger.debug(f"Social RSS feed content used for {title}")

            # If not social, or if feed content was empty, try to fetch full article
            if not content:
                # Fetch Full Article Text using newspaper3k
                try:
                    # Add headers to bypass 403 Forbidden on some sites
                    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
                    response = requests.get(entry.link, headers=headers, timeout=10)
                    response.encoding = response.apparent_encoding
                    html = response.text
                    
                    # Detect block messages
                    if "working on getting this fixed" in html.lower() or "log in or sign up to view" in html.lower():
                        logger.warning(f"Detected block message from {entry.link}, skipping external extraction.")
                        html = "" # Force fallback to feed content
                    
                    if html:
                        article = Article(entry.link)
                        article.set_html(html)
                        article.parse()
                        
                        # Newspaper3k often fails on Burmese text because it uses space-based word counting 
                        # to finding "content" text blocks. If text is short or is a menu item, use fallback.
                        if article.text and len(article.text) > 150 and "what are you looking for" not in article.text.lower():
                            content = article.text
                        else:
                            # Fallback: Parse with BeautifulSoup and extract <p> tags
                            soup = BeautifulSoup(html, 'html.parser')
                            
                            # Try to find the main article container
                            article_container = soup.find('article') or soup.find(class_='entry-content') or soup.find(class_='post-content') or soup.find(class_='content')
                            
                            if article_container:
                                paragraphs = article_container.find_all('p')
                                if paragraphs:
                                    content = '\n\n'.join(p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True))
                                else:
                                    content = article_container.get_text(separator='\n', strip=True)
                            else:
                                # Last ditch: grab all paragraphs in body
                                paragraphs = soup.find('body').find_all('p') if soup.find('body') else []
                                if paragraphs:
                                    content = '\n\n'.join(p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True))
                except Exception as e:
                    logger.warning(f"Could not extract full article from {entry.link}: {e}")
                    
            # Fallback to feed summary if extraction failed OR if we just didn't try external fetch
            if not content:
                if 'content' in entry:
                    # Some feeds provide full content as HTML
                    soup = BeautifulSoup(entry.content[0].value, 'html.parser')
                    content = soup.get_text(separator='\n', strip=True)
                elif 'summary' in entry:
                    soup = BeautifulSoup(entry.summary, 'html.parser')
                    content = soup.get_text(separator='\n', strip=True)
            
            # Extract Image
            image_url = _extract_rss_image(entry)
            
            # Fallback: Fetch OG image if no image found in feed
            if not image_url:
                 image_url = _fetch_og_image(entry.link)

            if not _is_valid_image(image_url):
                 image_url = None
            
            # Final Fallback: If content is empty, use title
            if not content and title:
                content = title

            # Ensure both Title and Content are translated cleanly
            trans_title = translate_text(title)
            trans_content = translate_text(content)
            
            # Save
            try:
                Post.objects.create(
                    source=source,
                    title=trans_title,
                    original_content=content,
                    translated_content=trans_content,
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

def run_scraping():
    sources = Source.objects.filter(is_active=True)
    total_new = 0
    print(f"DEBUG: Found {sources.count()} active sources")
    
    for source in sources:
        try:
            # We strictly use RSS fetching now
            total_new += fetch_rss(source)
        except Exception as e:
            logger.error(f"Failed to process source {source.name} ({source.url}): {e}")
            
    return total_new
