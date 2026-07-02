import random
import asyncio
from playwright.async_api import async_playwright, Page, BrowserContext

class PlaywrightHelper:
    """Helper class to manage Playwright instances and provide common utilities."""
    
    @staticmethod
    async def create_browser_context(p, headless: bool = True) -> BrowserContext:
        """Create a browser context with stealth-like settings to avoid basic bot detection."""
        browser = await p.chromium.launch(
            headless=headless,
            args=["--disable-blink-features=AutomationControlled"]
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="en-US"
        )
        # Add init script to mask webdriver
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        return context

    @staticmethod
    async def human_delay(min_ms: int = 1000, max_ms: int = 3000):
        """Simulate human reading/reaction time."""
        delay = random.uniform(min_ms / 1000, max_ms / 1000)
        await asyncio.sleep(delay)

    @staticmethod
    async def human_type(page: Page, selector: str, text: str):
        """Type text with random delays between keystrokes to simulate human typing."""
        await page.click(selector)
        for char in text:
            await page.keyboard.press(char)
            await asyncio.sleep(random.uniform(0.05, 0.15))
