from datetime import datetime
from django.utils import timezone
from django.conf import settings
import time
from typing import List, Dict, Optional

# Try importing sync_playwright, handle error if not installed
try:
    from playwright.sync_api import sync_playwright
except ImportError:
    sync_playwright = None

def fetch_twitter_posts(username: str, limit: int = 5) -> List[Dict]:
    """
    Scrapes tweets from a public Twitter profile using Playwright.
    
    Args:
        username (str): The Twitter username (without @).
        limit (int): Number of tweets to try and fetch.
        
    Returns:
        List[Dict]: A list of dictionaries with 'title', 'text', 'image_url', 'permalink', 'published_at'.
    """
    if not sync_playwright:
        print("Playwright not installed. Cannot scrape Twitter.")
        return []

    # Clean username if full URL is passed
    if "twitter.com/" in username:
        username = username.split("twitter.com/")[-1].split("/")[0]
    elif "x.com/" in username:
        username = username.split("x.com/")[-1].split("/")[0]
        
    username = username.strip().strip('@')
    url = f"https://x.com/{username}"
    
    posts = []
    
    try:
        with sync_playwright() as p:
            # Launch browser (headless=True for background execution)
            # Use a proxy if configured in environment, else None
            headless_mode = getattr(settings, 'SELENIUM_HEADLESS', True)
            browser = p.chromium.launch(headless=headless_mode)
            
            context = browser.new_context(
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
            )
            page = context.new_page()
            
            print(f"🔹 Navigating to {url} ...")
            
            try:
                page.goto(url, timeout=60000)
            except Exception as e:
                print(f"❌ Connection failed: {e}")
                print("⚠️ REMINDER: You need a System VPN or Proxy to access X if it is blocked in your region.")
                browser.close()
                return []

            # Wait for tweets
            try:
                # Wait for the timeline to load
                page.wait_for_selector('[data-testid="tweet"]', timeout=20000)
                print("✅ Tweets loaded!")
            except Exception:
                print("❌ Timed out waiting for tweets. (Are you logged in? Is the VPN on?)")
                browser.close()
                return []

            # Scroll to trigger lazy loading
            for _ in range(3):
                page.mouse.wheel(0, 1000)
                time.sleep(1.5)

            # Extract tweets
            tweet_elements = page.locator('[data-testid="tweet"]').all()
            print(f"Found {len(tweet_elements)} tweets.")
            
            for i, tweet in enumerate(tweet_elements):
                if len(posts) >= limit:
                    break
                    
                try:
                    # 1. Text
                    text_el = tweet.locator('[data-testid="tweetText"]').first
                    text = text_el.inner_text() if text_el.count() > 0 else ""
                    
                    # 2. Image
                    image_url = None
                    photo = tweet.locator('[data-testid="tweetPhoto"] img').first
                    if photo.count() > 0:
                        image_url = photo.get_attribute("src")
                        
                    # 3. Permalink & ID
                    # The timestamp is usually a link in the format /username/status/ID
                    time_el = tweet.locator('time').first
                    permalink = None
                    published_at = timezone.now()
                    
                    if time_el.count() > 0:
                        datetime_str = time_el.get_attribute("datetime")
                        if datetime_str:
                            try:
                                published_at = datetime.fromisoformat(datetime_str.replace('Z', '+00:00'))
                            except ValueError:
                                pass
                        
                        # Find the parent anchor tag for the permalink
                        # Playwright locator logic: time element -> parent -> attribute href
                        link_el = tweet.locator('a[href*="/status/"]').first
                        if link_el.count() > 0:
                            href = link_el.get_attribute("href")
                            if href:
                                permalink = f"https://x.com{href}" if href.startswith('/') else href

                    if not permalink:
                        # Fallback if we can't find link
                        continue
                        
                    if not text and not image_url:
                        continue
                        
                    posts.append({
                        "title": text[:100] + "..." if len(text) > 100 else text, # Use truncated text as title
                        "text": text,
                        "image_url": image_url,
                        "permalink": permalink,
                        "published_at": published_at
                    })
                    
                except Exception as e:
                    print(f"Error parsing tweet {i}: {e}")
                    continue
            
            browser.close()
            
    except Exception as e:
        print(f"Twitter Scraper Error: {e}")
        
    return posts
