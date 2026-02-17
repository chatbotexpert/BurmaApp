import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source
from aggregator.scrapers import fetch_telegram

def add_and_scrape_telegram():
    # Channel: Mratt Kyaw Thu
    name = "Mratt Kyaw Thu"
    url = "https://t.me/mrattkya"
    
    source, created = Source.objects.get_or_create(
        url=url,
        defaults={
            'name': name,
            'source_type': 'TELEGRAM',
            'is_active': True
        }
    )
    
    if created:
        print(f"Created new source: {name}")
    else:
        print(f"Source already exists: {name}")
        # Ensure it's set to TELEGRAM type (in case it was added wrongly before)
        if source.source_type != 'TELEGRAM':
            source.source_type = 'TELEGRAM'
            source.save()
            print("Updated source type to TELEGRAM")

    print("Fetching posts...")
    count = fetch_telegram(source)
    print(f"Successfully scraped {count} new posts from {name}")

if __name__ == '__main__':
    add_and_scrape_telegram()
