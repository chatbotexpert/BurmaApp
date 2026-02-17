import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.telegram_scraper import fetch_telegram_posts

def test_telegram():
    channel = "mrattkya" # A popular Burmese news channel
    print(f"Testing scraper for channel: {channel}")
    
    posts = fetch_telegram_posts(channel)
    print(f"Found {len(posts)} posts.")
    
    for post in posts[:3]:
        print("-" * 20)
        print(f"Title: {post['title']}")
        print(f"Date: {post['published_date']}")
        print(f"Image: {post['image_url']}")
        print(f"Content: {post['content'][:100]}...")

if __name__ == '__main__':
    test_telegram()
