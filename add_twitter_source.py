import os
import django
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source
from aggregator.scrapers import run_scraping

def add_twitter_source():
    # Example: SpaceX
    source_name = "SpaceX"
    source_url = "https://x.com/SpaceX"
    
    # Check if exists
    source, created = Source.objects.get_or_create(
        url=source_url,
        defaults={
            'name': source_name,
            'source_type': 'TWITTER',
            'is_active': True
        }
    )
    
    if created:
        print(f"✅ Created new source: {source_name}")
    else:
        print(f"ℹ️ Source already exists: {source_name}")
        # Ensure it is set to TWITTER type and Active
        source.source_type = 'TWITTER'
        source.is_active = True
        source.save()

    print(f"🚀 Starting scrape for {source_name}...")
    run_scraping()
    print("✨ Scraping complete!")

if __name__ == '__main__':
    add_twitter_source()
