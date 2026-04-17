import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

import requests
from bs4 import BeautifulSoup
import feedparser
from aggregator.translator import translate_text

def test_fetch_burmese(url="https://khitthitnews.com/feed"):
    print(f"Testing fetch from: {url}")
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    
    # 1. Test Feed parsing
    feed_response = requests.get(url, headers=headers, timeout=10)
    if feed_response.encoding is None or feed_response.encoding.lower() == 'iso-8859-1':
        feed_response.encoding = 'utf-8' # Force UTF-8 on missing/default charsets
    
    feed = feedparser.parse(feed_response.text)
    if not feed.entries:
        print("No entries found in feed.")
        return
        
    entry = feed.entries[0]
    print(f"\n--- FEED ENTRY TITLE ---")
    print(entry.title)
    
    # 2. Test HTML parsing
    print(f"\n--- FETCHING FULL ARTICLE: {entry.link} ---")
    response = requests.get(entry.link, headers=headers, timeout=10)
    if response.encoding is None or response.encoding.lower() == 'iso-8859-1':
        response.encoding = 'utf-8' # Force UTF-8 fallback
        
    html = response.text
    soup = BeautifulSoup(html, 'html.parser')
    
    # Simple extraction strategy from scrapers.py fallback
    content = ""
    article_container = soup.find('article') or soup.find(class_='entry-content') or soup.find(class_='post-content') or soup.find(class_='content')
    if article_container:
        paragraphs = article_container.find_all('p')
        if paragraphs:
            content = '\n\n'.join(p.get_text(separator=' ', strip=True) for p in paragraphs if p.get_text(strip=True))
        else:
            content = article_container.get_text(separator='\n', strip=True)
            
    print(f"\n--- ORIGINAL EXTRACTED CONTENT (First 300 chars) ---")
    print(content[:300] if content else "No content extracted.")
    
    # 3. Test Translation
    print(f"\n--- TESTING DEEPSEEK TRANSLATION (First 300 chars) ---")
    translated = translate_text(content[:1000]) if content else ""
    print(translated[:300] if translated else "No translation returned.")

def test_chinese():
    print(f"\n=======================")
    print(f"Testing Chinese Translation Fallback")
    chinese_text = "【果敢通讯社】4月17日讯：水花飞溅庆佳节，警徽闪耀护平安。泼水节期间，老街市沉浸在欢乐祥和的节日氛围中"
    print(f"Original: {chinese_text}")
    print(f"Translated: {translate_text(chinese_text)}")

if __name__ == "__main__":
    test_fetch_burmese()
    test_chinese()
