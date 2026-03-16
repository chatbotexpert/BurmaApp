import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source, Post, ScraperSettings

def run():
    print("Clearing old posts and sources from the database...")
    Post.objects.all().delete()
    Source.objects.all().delete()
    
    # Also ensure settings are at the right default 15 minutes while we are at it
    settings = ScraperSettings.objects.first()
    if settings:
        settings.scraping_interval = 15
        settings.save()
    else:
        ScraperSettings.objects.create(scraping_interval=15)
        
    print("Settings updated. Creating 8 correct sources...")

    sources = [
        ('BBC BURMESE RSS', 'https://rss.app/feeds/UoZp3Rr5qosu5NMX.xml', 'FACEBOOK'),
        ('BBC Burmese', 'https://rss.app/feeds/UoZp3Rr5qosu5NMX.xml', 'FACEBOOK'),
        ('Geo News', 'https://rss.app/feeds/lJjyJygllL2iArS0.xml', 'FACEBOOK'),
        ('Myanmar Now Burmese', 'https://rss.app/feeds/HsFw5spwKn9reWMN.xml', 'FACEBOOK'),
        ('ludunwayoo (Peoples Spring)', 'https://www.ludunwayoo.com/feed/', 'RSS'),
        ('Narinjara Burmese', 'https://rss.app/feeds/PhswE6Q6rUXMArDj.xml', 'FACEBOOK'),
        ('Myanmar Now Burmese', 'https://rss.app/feeds/jdmZNzSV1A0BWyYu.xml', 'FACEBOOK'),
        ('Mongla News', 'https://rss.app/feeds/AC6YNWcKQZP7RXrs.xml', 'FACEBOOK')
    ]

    for name, url, s_type in sources:
        Source.objects.create(
            name=name,
            url=url,
            source_type=s_type,
            is_active=True
        )

    print(f"Successfully added {len(sources)} sources to the VM database!")
    print("Background scraper will now automatically pick these up on its next 15-minute cycle.")

if __name__ == '__main__':
    run()
