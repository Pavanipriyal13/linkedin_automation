from pathlib import Path
from playwright.async_api import async_playwright


async def launch_browser(headless: bool = False, storage_state_path: str | None = "auth.json"):
    playwright = await async_playwright().start()
    browser = await playwright.chromium.launch(headless=headless)
    context = None
    if storage_state_path and Path(storage_state_path).exists():
        context = await browser.new_context(storage_state=storage_state_path)
    else:
        context = await browser.new_context()
    page = await context.new_page()
    return playwright, browser, page
