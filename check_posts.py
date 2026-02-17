import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Post

print(f"Total posts: {Post.objects.count()}")
