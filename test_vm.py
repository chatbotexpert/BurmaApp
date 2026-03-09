import asyncio
import logging
from playwright.async_api import async_playwright
logging.basicConfig(level=logging.INFO)

async def test_vm_scraper():
    async with async_playwright() as pw:
        # Standard launch matching fb_scraper
        browser = await pw.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            locale="en-US"
        )
        
        # Add anti-detection script
        await context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)
        
        page = await context.new_page()
        
        logging.info("Going to Mongla News...")
        response = await page.goto("https://www.facebook.com/MonglaNews/", wait_until="domcontentloaded", timeout=60000)
        logging.info(f"Response status: {response.status if response else 'None'}")
        
        await page.wait_for_timeout(5000)
        title = await page.title()
        logging.info(f"Title: {title}")
        
        html = await page.content()
        with open("fb_vm_dom.html", "w", encoding="utf-8") as f:
            f.write(html)
            
        logging.info("HTML dumped to fb_vm_dom.html")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(test_vm_scraper())
