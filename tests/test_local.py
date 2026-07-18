import asyncio
from playwright.async_api import async_playwright
import os

async def fetch_local_drugs():
    drugs = set()
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        file_path = f"file://{os.path.abspath('test_mi_table.html')}"
        
        await page.goto(file_path)
        await page.wait_for_selector('table.ddc-table-sortable')
        
        elements = await page.locator('table.ddc-table-sortable tbody tr.ddc-table-row-medication').all()
        for row in elements:
            drug_link = row.locator('th .ddc-table-row-medication-info-link-wrap a')
            if await drug_link.count() > 0:
                name = await drug_link.inner_text()
                if name:
                    drugs.add(name.strip())
                    
        await browser.close()
    return list(set([d.split(' (')[0] for d in drugs]))

print(asyncio.run(fetch_local_drugs()))
