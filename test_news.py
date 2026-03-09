import sys
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.scrapers import fetch_rss
from aggregator.models import Source

def main():
    print("Testing RSS scrape...")
    # Mock a source object for Kachin News
    mock_source = Source(name="Kachin News", source_type="RSS", url="https://burmese.kachinnews.com/feed/")
    fetch_rss(mock_source)
    print("Fetch complete. Check db or logs.")

if __name__ == "__main__":
    main()
