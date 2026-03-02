"""
Facebook Playwright scraper (library version)
============================================

This module defines a Playwright-based scraper for Facebook pages.
"""

from __future__ import annotations

import asyncio
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Tuple
import logging
import re

from bs4 import BeautifulSoup
from playwright.async_api import async_playwright, Browser, Page, BrowserContext
from django.conf import settings

# ---------------------------------------------------------------------------
# Helper functions
# ---------------------------------------------------------------------------


def parse_cookie_string(cookie_string: str, domain: str = ".facebook.com") -> List[Dict[str, str]]:
    """
    Parse a semicolon-separated cookie string into a list of cookie dictionaries.
    """
    cookies: List[Dict[str, str]] = []
    for segment in cookie_string.split(";"):
        segment = segment.strip()
        if not segment or "=" not in segment:
            continue
        name, value = segment.split("=", 1)
        cookies.append(
            {
                "name": name.strip(),
                "value": value.strip(),
                "domain": domain,
                "path": "/",
            }
        )
    return cookies


async def create_page_with_cookies(cookie_string: str, headless: bool) -> Tuple[Page, BrowserContext, Browser, object]:
    """
    Create a Playwright page with stealth settings and cookies applied.
    """
    cookies = parse_cookie_string(cookie_string)
    pw = await async_playwright().start()
    browser: Browser = await pw.chromium.launch(
        headless=headless,
        args=[
            "--disable-blink-features=AutomationControlled",
            "--disable-dev-shm-usage",
            "--disable-gpu",
            "--no-sandbox",
            "--disable-setuid-sandbox",
            "--single-process",
            "--disable-notifications",
        ],
    )
    user_agent = (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
    context = await browser.new_context(
        user_agent=user_agent,
        viewport={"width": 1280, "height": 800},
        locale="en-US",
        timezone_id="Europe/London",
    )
    await context.add_init_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined});"
    )
    await context.add_cookies(cookies)
    page = await context.new_page()
    return page, context, browser, pw



async def click_see_more_buttons(page: Page) -> None:
    """Click all visible “See more” buttons to expand truncated posts."""
    logging.info("Clicking 'See more' buttons...")
    for _ in range(5): # Limit to 5 iterations to avoid infinite loop
        buttons = page.locator("div[role='button']:has-text('See more')")
        count = await buttons.count()
        if count == 0:
            break
        logging.info(f"Found {count} 'See more' buttons.")
        for idx in range(count):
            try:
                await buttons.nth(idx).click(timeout=1000)
                await page.wait_for_timeout(300)
            except Exception as e:
                logging.debug(f"Error clicking button: {e}")
        await page.wait_for_timeout(500)


# --- Alt-text / permalink helpers ------------------------------------------


AUTO_ALT_PREFIXES = (
    "may be an image of",
    "image may contain",
    "no photo description available",
    "no description available",
)


def _clean_image_alt(alt: Optional[str]) -> Optional[str]:
    if not alt:
        return None
    text = alt.strip()
    lower = text.lower()
    if any(lower.startswith(prefix) for prefix in AUTO_ALT_PREFIXES):
        return None
    return text or None


def _normalise_facebook_url(url: Optional[str], page_url: str) -> str:
    if not url:
        return page_url
    url = url.strip()
    if url.startswith("http://") or url.startswith("https://"):
        pass
    elif url.startswith("/"):
        url = "https://www.facebook.com" + url
    elif url.startswith("facebook.com"):
        url = "https://" + url
    elif url.startswith("?"):
        url = "https://www.facebook.com" + url
    
    # Strip query parameters to prevent duplicates, except 'v' for videos
    try:
        from urllib.parse import urlparse, parse_qs, urlencode, urlunparse
        parsed = urlparse(url)
        # Keep only 'v' parameter if it exists (for FB video URLs)
        query_dict = parse_qs(parsed.query)
        new_query = {}
        if 'v' in query_dict:
            new_query['v'] = query_dict['v']
        
        # Reconstruct the URL without tracking parameters
        url = urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            urlencode(new_query, doseq=True),
            parsed.fragment
        ))
    except Exception as e:
        logging.debug(f"Error normalising URL {url}: {e}")
        
    return url


# ---------------------------------------------------------------------------
# HTML extraction
# ---------------------------------------------------------------------------


def width_too_small(img_tag):
    try:
        w = img_tag.get("width")
        if w and int(str(w).replace("px", "")) < 50:
            return True
        h = img_tag.get("height")
        if h and int(str(h).replace("px", "")) < 50:
            return True
    except Exception:
        pass
    return False

def extract_posts_from_html(html: str) -> List[Dict[str, Optional[str]]]:
    soup = BeautifulSoup(html, "html.parser")
    posts_data: List[Dict[str, Optional[str]]] = []
    
    # Use generic ARIA role selector which is much more stable than class names
    # Facebook posts almost always have role="article"
    posts = soup.find_all("div", {"role": "article"})
    
    if not posts:
        # Fallback 1: Common post wrapper class
        posts = soup.find_all("div", class_=lambda c: c and "x1yztbdb" in c.split())
        
    if not posts:
        # Fallback 2: data-pagelet indicating a feed unit or timeline post
        posts = [d for d in soup.find_all("div") if isinstance(d.get("data-pagelet"), str) and ("FeedUnit_" in d.get("data-pagelet") or "ProfileTimeline" in d.get("data-pagelet"))]

    if not posts:
        # Fallback 3: If still nothing, try class x1n2onr6 x1ja2u2z
        posts = soup.find_all("div", class_=lambda c: c and "x1n2onr6" in c.split() and "x1ja2u2z" in c.split())

    for post in posts:
        try:
            # STATS
            likes = None
            comments = None
            shares = None
            
            # TEXT EXTRACTION
            post_text = ""
            msg_divs = post.find_all("div", {"data-ad-preview": "message"})
            if msg_divs:
                 post_text = " ".join([msg.get_text(strip=True) for msg in msg_divs])
            else:
                 # Fallback: Get text from paragraphs or bare text not in hidden elements
                 # Videos and multi-image posts often have specific text containers
                 text_containers = post.find_all("div", {"dir": "auto"})
                 # Filter out numbers (likes count) and common UI text
                 ui_terms = {"See more", "Like", "Comment", "Share", "Send", "Reply", "View"}
                 valid_texts = []
                 for t_node in text_containers:
                     txt = t_node.get_text(" ", strip=True)
                     if txt and not any(txt == ui for ui in ui_terms) and not txt.isdigit():
                         if len(txt) > 10: # Likely actual post text
                             valid_texts.append(txt)
                 
                 if valid_texts:
                     post_text = " ".join(valid_texts)
                 else:
                     # If no valid text containers found, check if it's just a login button group
                     if "Log in" in post.get_text() or "Create new account" in post.get_text():
                         logging.debug("Skipping post-like element that appears to be login UI.")
                         continue
                     post_text = post.get_text(" ", strip=True) # Final noisy fallback

            # TIME
            post_time = None
            
            # LINK
            post_link = None
            for a_tag in post.find_all("a", href=True):
                href = a_tag.get("href") or ""
                if "/posts/" in href or "story_fbid" in href or "permalink.php" in href or "/watch/" in href or "/photo" in href or "/video" in href or "/reel/" in href:
                    post_link = href
                    break
            
            # IMAGE
            preview_image = None
            
            # Find the FIRST valid image. We skip emojis, icons, and transparent spacers.
            for img in post.find_all("img", attrs={"src": True}):
                src = img.get("src")
                if "emoji.php" in src or "static.xx.fbcdn.net" in src or "data:image/svg+xml" in src or width_too_small(img):
                     continue
                preview_image = src
                break # We only want one image!
                
            if not preview_image:
                 video_poster = post.find("img", attrs={"referrerpolicy": "origin-when-cross-origin"})
                 if video_poster:
                      preview_image = video_poster.get("src")

            posts_data.append(
                {
                    "text": post_text,
                    "likes": likes,
                    "comments": comments,
                    "shares": shares,
                    "time": post_time,
                    "preview_title": None,
                    "preview_url": None,
                    "preview_image": preview_image,
                    "post_link": post_link,
                }
            )
        except Exception:
            continue
    return posts_data


def remove_duplicate_posts(posts: List[Dict[str, Optional[str]]]) -> List[Dict[str, Optional[str]]]:
    seen = set()
    unique_posts: List[Dict[str, Optional[str]]] = []
    for post in posts:
        text = (post.get("text") or "").strip()
        link = (post.get("post_link") or post.get("preview_url") or "").strip()
        key = (text, link)
        if key in seen:
            continue
        seen.add(key)
        unique_posts.append(post)
    return unique_posts


# ---------------------------------------------------------------------------
# Core Playwright scraping
# ---------------------------------------------------------------------------


async def close_popups(page: Page):
    """Attempt to close common Facebook popups and forcefully unlock scroll."""
    try:
        # Force scroll bypass every time we check for popups
        await page.evaluate("""
            document.body.style.setProperty('overflow', 'auto', 'important');
            document.documentElement.style.setProperty('overflow', 'auto', 'important');
            
            // Remove dialogs and login blocks
            document.querySelectorAll('div[data-nosnippet="yes"], div[role="dialog"]').forEach(e => e.remove());
            
            // Aggressively remove large fixed/absolute overlays
            document.querySelectorAll('*').forEach(e => {
                const style = window.getComputedStyle(e);
                if ((style.position === 'fixed' || style.position === 'absolute') && parseInt(style.zIndex) > 5) {
                    if (e.offsetWidth > window.innerWidth * 0.5 && e.offsetHeight > window.innerHeight * 0.5) {
                        e.remove();
                    }
                }
            });
        """)
        
        # Generic close button for "See more" or login prompts
        close_buttons = page.locator('div[aria-label="Close"], div[aria-label="Decline optional cookies"], div[role="button"]:has-text("Not Now"), div[role="button"]:has-text("Close")')
        count = await close_buttons.count()
        if count > 0:
            logging.info(f"Unwanted popups found: {count}. Closing...")
            for i in range(count):
                if await close_buttons.nth(i).is_visible():
                    await close_buttons.nth(i).click(timeout=1000)
                    await page.wait_for_timeout(500)
    except Exception as e:
        logging.debug(f"Popup close error: {e}")

async def scrape_facebook_posts(
    profile_url: str,
    cookie_string: str,
    max_posts: int,
    headless: bool,
    scroll_step: int = 800,
    scroll_delay: float = 3.0,
) -> List[Dict[str, Optional[str]]]:
    page, context, browser, pw = None, None, None, None
    try:
        page, context, browser, pw = await create_page_with_cookies(cookie_string, headless)

        await page.goto(profile_url, wait_until="domcontentloaded", timeout=60000)
        await page.wait_for_timeout(5000)
        
        # Check for login wall or issues
        title = await page.title()
        logging.info(f"Page Title: {title}")
        
        if "Log In" in title or "Log into" in title or title.strip() == "Facebook":
             logging.warning(f"Hit a login wall or security block. Title: {title}")
             await page.screenshot(path="debug_fb_fail.png")
             with open("debug_fb_fail.html", "w", encoding="utf-8") as f:
                 f.write(await page.content())
             return [] # Abort immediately if we hit a login wall
        
        # Bypass scroll locks and hide overlay dialogs forcefully
        await close_popups(page)
        await click_see_more_buttons(page)
        
        collected: List[Dict[str, Optional[str]]] = []
        scroll_count = 0
        MAX_SCROLLS = 15
        consecutive_no_new_posts = 0
        
        while len(collected) < max_posts and scroll_count < MAX_SCROLLS:
            await close_popups(page)
            
            html = await page.content()
            new_posts = extract_posts_from_html(html)
            logging.info(f"Extracted {len(new_posts)} raw posts from current view.")
            
            if len(new_posts) > 0:
                 logging.info(f"Sample Post Text: {new_posts[0].get('text', '')[:100]}...")
            
            prev_len = len(collected)
            collected.extend(new_posts)
            collected = remove_duplicate_posts(collected)
            logging.info(f"Total collected unique posts: {len(collected)}")
            
            if len(collected) == prev_len:
                consecutive_no_new_posts += 1
            else:
                consecutive_no_new_posts = 0
                
            if consecutive_no_new_posts >= 3:
                logging.info("No new posts found after 3 scrolls. Breaking early.")
                await page.screenshot(path="debug_early_break.png")
                break
            
            if len(collected) >= max_posts:
                break
                
            await page.keyboard.press("PageDown")
            await page.wait_for_timeout(int(scroll_delay * 1000))
            await click_see_more_buttons(page)
            scroll_count += 1
            
        if len(collected) == 0:
             logging.warning("No posts collected. Taking screenshot and dumping HTML.")
             await page.screenshot(path="debug_fb_fail.png")
             with open("debug_fb_fail.html", "w", encoding="utf-8") as f:
                 f.write(await page.content())
                 
        return collected[:max_posts]
    except Exception as e:
        logging.error(f"Facebook scraping error for {profile_url}: {e}")
        if page:
             await page.screenshot(path="error_state.png")
        return []
    finally:
        if page:
            try:
                await page.close()
            except Exception:
                pass
        if context:
            try:
                await context.close()
            except Exception:
                pass
        if browser:
            try:
                await browser.close()
            except Exception:
                pass
        if pw:
            try:
                await pw.stop()
            except Exception:
                pass


# ---------------------------------------------------------------------------
# Normalisation into unified schema
# ---------------------------------------------------------------------------


def _convert_relative_time(rel: Optional[str]) -> datetime:
    now = datetime.now(timezone.utc)
    if not rel:
        return now
    try:
        if rel.endswith("h"):
            hours = int(rel[:-1])
            return now - timedelta(hours=hours)
        if rel.endswith("m"):
            minutes = int(rel[:-1])
            return now - timedelta(minutes=minutes)
    except Exception:
        pass
    return now


def _is_empty_normalised_post(post: Dict[str, object]) -> bool:
    text = str(post.get("text") or "").strip()
    title = str(post.get("title") or "").strip()
    image_url = post.get("image_url")
    permalink = str(post.get("permalink") or "").lower()
    
    # Let video links bypass text/image requirements
    if "/reel/" in permalink or "/video" in permalink or "/watch/" in permalink:
        return False
        
    if not text and (not title or title.lower() == "post") and not image_url:
        return True
    return False


def _normalise_post(raw: Dict[str, Optional[str]], page_url: str) -> Dict[str, object]:
    text = (raw.get("text") or "").strip()

    preview_title_raw = raw.get("preview_title")
    preview_title = _clean_image_alt(preview_title_raw) if preview_title_raw else None

    first_line_from_text = ""
    if text:
        first_line_from_text = text.split("\n")[0].strip()

    title_candidate = first_line_from_text or (preview_title or "")
    title = (title_candidate or "Post").strip()[:120]

    image_url = raw.get("preview_image")
    permalink_raw = raw.get("post_link") or raw.get("preview_url") or page_url
    permalink = _normalise_facebook_url(permalink_raw, page_url)
    published_at = _convert_relative_time(raw.get("time"))

    return {
        "title": title,
        "text": text,
        "image_url": image_url,
        "permalink": permalink,
        "published_at": published_at,
    }


# ---------------------------------------------------------------------------
# Public API (synchronous wrapper)
# ---------------------------------------------------------------------------


def fetch_posts(page_url: str, limit: int = 5, headless: bool | None = None) -> List[Dict[str, object]]:
    cookie_string = getattr(settings, 'FACEBOOK_COOKIE_STRING', '')
    if not cookie_string:
        logging.warning("FACEBOOK_COOKIE_STRING is empty. Scraping will likely fail/redirect to login.")
        # Proceeding anyway as some public pages might show content, but usually not.
        
    if headless is None:
        headless = getattr(settings, 'SELENIUM_HEADLESS', True)

    async def _run() -> List[Dict[str, Optional[str]]]:
        return await scrape_facebook_posts(
            profile_url=page_url,
            cookie_string=cookie_string,
            max_posts=limit,
            headless=headless,
        )

    try:
        try:
            loop = asyncio.get_running_loop()
        except RuntimeError:
            loop = None

        if loop and loop.is_running():
             # If we are already in an event loop (unlikely for simple django command but possible),
             # we might need to use nesting or just run in a thread.
             # but asyncio.run won't work.
             # For simpler usage let's try standard run.
             # If using Django Channels or Asgi, this might be complex.
            import nest_asyncio
            nest_asyncio.apply()
            raw_posts = loop.run_until_complete(_run())
        else:
             raw_posts = asyncio.run(_run())

    except Exception as e:
        logging.error(f"Failed to scrape Facebook page {page_url}: {e}")
        return []

    normalised: List[Dict[str, object]] = []
    seen_keys: set[tuple[str, str, str]] = set()

    for rp in raw_posts:
        if len(normalised) >= limit:
            break
        post = _normalise_post(rp, page_url)
        if _is_empty_normalised_post(post):
            continue

        key = (
            str(post.get("title") or "").strip(),
            str(post.get("text") or "").strip(),
            str(post.get("permalink") or "").strip(),
        )
        if key in seen_keys:
            continue
        seen_keys.add(key)

        normalised.append(post)

    return normalised
