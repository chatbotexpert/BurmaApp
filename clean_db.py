import os
import django
import re

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'burma_news.settings')
django.setup()

from aggregator.models import Post

def clean_database():
    print("Cleaning database duplicates...")
    posts = Post.objects.all()
    count = 0
    
    # Regex to find the bold title pattern: **...** followed by newlines
    # We use dotall to capture multi-line titles if any, though usually they are single line
    pattern = re.compile(r'^\*\*(.*?)\*\*\s+', re.DOTALL)
    
    for post in posts:
        if not post.translated_content:
            continue
            
        match = pattern.match(post.translated_content)
        if match:
            # Check if what remains is just the same as the title (repetition) 
            # OR if we just want to strip the title regardless to be clean.
            # Strategy: Strip the title prefix.
            
            clean_content = pattern.sub('', post.translated_content, count=1).strip()
            
            # If stripping leaves nothing (e.g. if content was ONLY the title), 
            # then we might want to keep the title (but unbolded) or just leave it empty?
            # If the original content was just the title, then we have English Title / Burmese Title.
            # That is acceptable.
            
            if not clean_content:
                # The content was ONLY the header. 
                # e.g. "**Title**"
                # We should strip the ** marks and keep the text.
                clean_content = match.group(1).strip()
            
            # Update
            if clean_content != post.translated_content:
                post.translated_content = clean_content
                post.save()
                count += 1
                if count % 100 == 0:
                    print(f"Cleaned {count} posts...")

    print(f"Finished. Total duplicate titles removed: {count}")

if __name__ == '__main__':
    clean_database()
