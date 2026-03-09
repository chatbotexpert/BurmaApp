import asyncio
from aggregator.fb_scraper import create_page_with_cookies

async def dump_dom():
    page, context, browser, pw = await create_page_with_cookies('', True)
    await page.goto("https://www.facebook.com/nytimes")
    await page.wait_for_timeout(5000)
    
    html = await page.content()
    with open("fb_dom.html", "w", encoding="utf-8") as f:
        f.write(html)
        
    await browser.close()
    await pw.stop()

if __name__ == "__main__":
    asyncio.run(dump_dom())
