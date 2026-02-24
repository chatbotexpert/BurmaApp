import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burmafinal.settings')
django.setup()

from aggregator.models import Post
from django.db.models import Count

# Find all titles that have duplicates
duplicate_titles = Post.objects.values('title').annotate(count=Count('title')).filter(count__gt=1)

deleted_count = 0
for item in duplicate_titles:
    title = item['title']
    # Get all posts with this title, ordered by published date (keep the oldest/first scraped one)
    posts = list(Post.objects.filter(title=title).order_by('id'))
    
    if len(posts) > 1:
        # Keep the first one, delete the rest
        for p in posts[1:]:
            p.delete()
            deleted_count += 1

print(f"Cleanup complete. Deleted {deleted_count} duplicate posts.")
