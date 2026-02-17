import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source

def fix_geo():
    count = Source.objects.filter(name__icontains='Geo').update(url='https://www.geo.tv/rss/1/1')
    print(f"Updated {count} sources for Geo News.")

    # Check Zeeshan URL
    z = Source.objects.filter(name__icontains='Zeeshan').first()
    if z:
        print(f"Zeeshan URL: {z.url}")

if __name__ == '__main__':
    fix_geo()
