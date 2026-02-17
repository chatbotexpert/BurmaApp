import asyncio
from playwright.async_api import async_playwright

async def main():
    print("Starting Playwright...")
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        )
        page = await context.new_page()
        try:
            print("Navigating to Reuters...")
            await page.goto("https://www.facebook.com/Reuters", timeout=60000)
            title = await page.title()
            print(f"Page Title: {title}")
            await page.screenshot(path="reuters_basic.png")
            print("Screenshot saved.")
            
            content = await page.content()
            print(f"Content length: {len(content)}")
        except Exception as e:
            print(f"Error: {e}")
        finally:
            await browser.close()
            print("Browser closed.")

if __name__ == "__main__":
    asyncio.run(main())
