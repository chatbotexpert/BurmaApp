import os
import django
import sys

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burmafinal.settings')
django.setup()

from aggregator.models import Post
from django.db.models import Count

duplicates = Post.objects.values('title').annotate(count=Count('title')).filter(count__gt=1).order_by('-count')[:5]

for dup in duplicates:
    title = dup['title']
    print(f"Title: {title} (Count: {dup['count']})")
    posts = Post.objects.filter(title=title)
    for p in posts:
        print(f"  - URL: {p.url}")
        print(f"  - Original Content: {repr(p.original_content)[:100]}...")
    print("-" * 40)
