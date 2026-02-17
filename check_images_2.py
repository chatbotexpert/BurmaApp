import os
import django
import sys

# Add project root to path
sys.path.append(os.getcwd())

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Post

total = Post.objects.count()
with_images = Post.objects.exclude(image_url__isnull=True).exclude(image_url__exact='').count()

with open('images_found.txt', 'w') as f:
    f.write(f"Total Posts: {total}\n")
    f.write(f"Posts with Images: {with_images}\n")

    if with_images > 0:
        sample = Post.objects.exclude(image_url__isnull=True).exclude(image_url__exact='').first()
        f.write(f"Sample Image URL: {sample.image_url}\n")
    else:
        f.write("No images found yet.\n")
