import asyncio
from typing import List
from playwright.async_api import async_playwright
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_mi_drugs(url: str = 'https://www.drugs.com/condition/myocardial-infarction.html') -> List[str]:
    """
    Fetches the list of drug names from Drugs.com using Playwright to bypass basic 403 blocks.
    Returns a list of drug names.
    """
    drugs = set()
    logger.info(f"Starting Playwright to fetch {url}")
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        # Using a common user agent to appear as a standard browser
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        try:
            logger.info("Navigating to page...")
            await page.goto(url, wait_until='domcontentloaded', timeout=60000)
            
            # Check for generic 403 Access Denied (Akamai)
            page_title = await page.title()
            if "Access Denied" in page_title:
                raise Exception("Access Denied (403). Bot protection active.")
            
            # Drugs.com usually has a table with the class "condition-table" or links to drugs inside it
            # We wait for the table to appear
            try:
                await page.wait_for_selector('table.ddc-table-sortable', timeout=10000)
            except Exception:
                logger.warning("Could not find condition table, trying to extract links directly.")
                
            # Extract links that look like drug pages
            elements = await page.locator('table.ddc-table-sortable tbody tr.ddc-table-row-medication').all()
            for row in elements:
                drug_link = row.locator('th .ddc-table-row-medication-info-link-wrap a')
                if await drug_link.count() > 0:
                    name = await drug_link.inner_text()
                    if name:
                        drugs.add(name.strip())
                        
            if not drugs:
                # Fallback: find all links that look like /mtm/ or /pro/ or just regular drug links
                logger.info("Fallback scraping approach...")
                links = await page.locator("a.ddc-text-wordbreak").all()
                for link in links:
                    name = await link.inner_text()
                    if name:
                        drugs.add(name.strip())

        except Exception as e:
            logger.error(f"Error fetching drugs URL: {e}")
            import os
            local_html_path = os.path.join(os.getcwd(), 'data', 'raw', 'drugs_com_mi.html')
            if os.path.exists(local_html_path):
                logger.info(f"Falling back to local HTML file: {local_html_path}")
                await page.goto(f"file://{local_html_path}")
                elements = await page.locator('table.ddc-table-sortable tbody tr.ddc-table-row-medication').all()
                for row in elements:
                    drug_link = row.locator('th .ddc-table-row-medication-info-link-wrap a')
                    if await drug_link.count() > 0:
                        name = await drug_link.inner_text()
                        if name:
                            drugs.add(name.strip())
            else:
                logger.warning(f"No local HTML fallback found at {local_html_path}. You can save the webpage manually there to bypass bot protection.")
        finally:
            await browser.close()
            
    drug_list = list(drugs)
    logger.info(f"Found {len(drug_list)} drugs from Drugs.com")
    return list(set([d.split(' (')[0] for d in drug_list])) # clean up cases where generic name is in parens

def get_drugs() -> List[str]:
    return asyncio.run(fetch_mi_drugs())

if __name__ == '__main__':
    print("Fetching drugs.com...")
    print(get_drugs())
