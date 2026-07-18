import asyncio
from playwright.async_api import async_playwright

async def run():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a common user agent to appear as a standard browser
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        print("Navigating to page...")
        await page.goto("https://www.drugs.com/condition/myocardial-infarction.html", wait_until='domcontentloaded', timeout=60000)
        
        html = await page.content()
        with open("dump.html", "w") as f:
            f.write(html)
        
        await browser.close()

asyncio.run(run())
