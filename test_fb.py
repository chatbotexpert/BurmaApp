from facebook_scraper import get_posts
try:
    print("Import successful")
    for post in get_posts('Reuters', pages=1):
        print(post['text'][:20])
        break
except Exception as e:
    print(f"Error: {e}")
