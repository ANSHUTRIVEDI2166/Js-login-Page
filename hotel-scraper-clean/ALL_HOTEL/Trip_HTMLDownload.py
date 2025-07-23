import asyncio
from playwright.async_api import async_playwright
import json
import os
import sys

trip_url = sys.argv[1] if len(sys.argv) > 1 else "Not Found URL"
async def download_trip_html():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1366, 'height': 768},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            locale="en-US"
        )

        # Optional: load saved cookies
        if os.path.exists("trip_cookies.json"):
            with open("trip_cookies.json", "r") as f:
                cookies = json.load(f)
                await context.add_cookies(cookies)

        page = await context.new_page()

        # Remove bot detection flag
        await page.add_init_script("Object.defineProperty(navigator, 'webdriver', { get: () => undefined })")

        print("\U0001F30D Navigating to Trip.com...")
        await page.goto(trip_url, timeout=120_000)
        await page.wait_for_timeout(5000)

        # Show more room types (simulating original Selenium logic)
        try:
            for xpath in [
                "//span[contains(text(),'Show') and contains(text(),'Remaining Room Type')]",
                "//span[contains(text(),'More Room Types')]",
                "//span[contains(text(),'Show') and contains(text(),'More Room Rate')]"
            ]:
                while True:
                    show_more_buttons = await page.locator(xpath).all()
                    if not show_more_buttons:
                        break
                    for btn in show_more_buttons:
                        try:
                            await btn.scroll_into_view_if_needed()
                            await btn.click()
                            await page.wait_for_timeout(5000)
                        except:
                            continue
        except:
            pass

        # Save cookies after page load
        cookies = await context.cookies()
        with open("trip_cookies.json", "w") as f:
            json.dump(cookies, f)

        # Wait for rooms to load
        # try:
        #     await page.wait_for_selector("div.price-box", timeout=15000)
        #     print("✅ Room data visible.")
        # except:
        #     print("⚠️ Room info not detected.")

        html = await page.content()
        with open("trip_page.html", "w", encoding="utf-8") as f:
            f.write(html)

        print("✅ HTML saved.")
        await browser.close()

if __name__ == "__main__":
    asyncio.run(download_trip_html())
