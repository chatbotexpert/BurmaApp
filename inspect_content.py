import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Post

def inspect_posts():
    print("Inspecting latest 5 posts...")
    for post in Post.objects.all().order_by('-published_date')[:5]:
        print(f"--- Post ID: {post.id} ---")
        print(f"Title: {post.title}")
        print(f"Original Content Preview: {post.original_content[:100]}")
        print(f"Translated Content: {post.translated_content}")
        print("-" * 20)

if __name__ == '__main__':
    inspect_posts()
