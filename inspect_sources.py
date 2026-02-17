import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Source

print(f"Total sources: {Source.objects.count()}")
for s in Source.objects.all():
    print(f"ID: {s.id}, Name: {s.name}, Type: {s.source_type}, Active: {s.is_active}, URL: {s.url}")
