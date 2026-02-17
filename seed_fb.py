import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source

def seed_fb():
    # Using a public page Example: Reuters
    # https://www.facebook.com/Reuters
    source, created = Source.objects.get_or_create(
        url='https://www.facebook.com/Reuters',
        defaults={
            'name': 'Reuters Facebook',
            'source_type': 'FACEBOOK',
            'is_active': True
        }
    )
    if created:
        print(f"Created FB source: {source}")
    else:
        print(f"FB Source already exists: {source}")

if __name__ == '__main__':
    seed_fb()
