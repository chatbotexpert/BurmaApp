import requests
import json
from datetime import datetime
from django.utils import timezone
from bs4 import BeautifulSoup
from typing import List, Dict

def fetch_twitter_posts(username: str, limit: int = 5) -> List[Dict]:
    """
    Scrapes tweets from a public Twitter profile using the official Syndication API.
    This works reliably without login or headless browsers and is extremely fast.
    """
    if "twitter.com/" in username:
        username = username.split("twitter.com/")[-1].split("/")[0]
    elif "x.com/" in username:
        username = username.split("x.com/")[-1].split("/")[0]
        
    username = username.strip().strip('@')
    url = f"https://syndication.twitter.com/srv/timeline-profile/screen-name/{username}"
    
    posts = []
    
    try:
        print(f"🔹 Fetching tweets for {username} via Syndication API...")
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8'
        }
        res = requests.get(url, headers=headers, timeout=15)
        res.raise_for_status()
        
        soup = BeautifulSoup(res.text, 'html.parser')
        script_tag = soup.find('script', id='__NEXT_DATA__')
        
        if not script_tag:
            print(f"❌ Could not find tweet data for {username}. X.com might have blocked syndication.")
            return []
            
        data = json.loads(script_tag.string)
        entries = data.get('props', {}).get('pageProps', {}).get('timeline', {}).get('entries', [])
        
        print("✅ Tweets API data loaded!")
        
        for entry in entries:
            if len(posts) >= limit:
                break
                
            tweet_data = entry.get('content', {}).get('tweet', {})
            if not tweet_data:
                continue
                
            text = tweet_data.get('text', '')
            tweet_id = tweet_data.get('id_str', '')
            
            if not text and not tweet_id:
                continue
                
            # Extract image if exists
            image_url = None
            media_list = tweet_data.get('entities', {}).get('media', [])
            if media_list and len(media_list) > 0:
                # Prioritize 'media_url_https'
                image_url = media_list[0].get('media_url_https')
            
            # Publish Date Format: 'Sat Mar 07 19:12:34 +0000 2026'
            created_at_str = tweet_data.get('created_at', '')
            published_at = timezone.now()
            if created_at_str:
                try:
                    parsed_date = datetime.strptime(created_at_str, '%a %b %d %H:%M:%S %z %Y')
                    published_at = parsed_date
                except ValueError:
                    pass
            
            permalink = f"https://x.com/{username}/status/{tweet_id}"
            title = text[:100] + "..." if len(text) > 100 else text
            
            posts.append({
                "title": title if title else f"Tweet {tweet_id}",
                "text": text,
                "image_url": image_url,
                "permalink": permalink,
                "published_at": published_at
            })
            
        print(f"Found {len(posts)} tweets.")
        
    except Exception as e:
        print(f"Twitter Scraper Error: {e}")
        
    return posts
