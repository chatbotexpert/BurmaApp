import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source

def seed():
    source, created = Source.objects.get_or_create(
        url='http://rss.cnn.com/rss/edition_asia.rss',
        defaults={
            'name': 'CNN Asia',
            'source_type': 'RSS',
            'is_active': True
        }
    )
    if created:
        print(f"Created source: {source}")
    else:
        print(f"Source already exists: {source}")

if __name__ == '__main__':
    seed()
