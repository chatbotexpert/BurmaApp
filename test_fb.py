import asyncio
from aggregator.fb_scraper import fetch_posts

def main():
    print("Fetching posts from NYTimes...")
    posts = fetch_posts('https://www.facebook.com/nytimes', 2, False)
    
    with open("fb_debug_output.txt", "w", encoding="utf-8") as f:
        for p in posts:
            f.write(f"TITLE: {p['title']}\n")
            f.write(f"TEXT: {p['text']}\n")
            f.write(f"LINK: {p['permalink']}\n")
            f.write("-" * 80 + "\n")

if __name__ == "__main__":
    main()
