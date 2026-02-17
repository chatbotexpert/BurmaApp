import os
import django
import sys

# Setup Django environment
sys.path.append(r'd:\burmafinal')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Post
from aggregator.translator import translate_text

def fix_posts():
    # Find posts with empty original content
    posts = Post.objects.filter(original_content='')
    print(f"Found {posts.count()} posts with empty content.")
    
    for post in posts:
        if post.title:
            print(f"Fixing post: {post.title[:50]}...")
            post.original_content = post.title
            post.translated_content = translate_text(post.title)
            post.save()
            print("  Fixed.")
        else:
            print(f"  Skipping post {post.id} (no title).")

if __name__ == "__main__":
    fix_posts()
