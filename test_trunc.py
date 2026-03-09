import asyncio
from aggregator.fb_scraper import scrape_facebook_posts

async def test_truncation():
    posts = await scrape_facebook_posts("https://www.facebook.com/nytimes/", "", 5, True)
    
    with open("all_posts.txt", "w", encoding="utf-8") as f:
        for p in posts:
            f.write(f"TEXT: {p.get('text')}\n")
            f.write("-" * 50 + "\n")

if __name__ == "__main__":
    asyncio.run(test_truncation())
