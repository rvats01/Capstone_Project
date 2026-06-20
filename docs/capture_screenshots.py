
import asyncio
from pyppeteer import launch

async def screenshot():
    browser = await launch()
    pages = [
        ("http://localhost:8000", "dashboard"),
        ("http://localhost:8000/submit", "submit_claim"),
        ("http://localhost:8000/claims", "claims_list"),
        ("http://localhost:8000/docs", "api_docs"),
    ]
    
    for url, name in pages:
        page = await browser.newPage()
        await page.setViewport({'width': 1280, 'height': 960})
        await page.goto(url, {'waitUntil': 'networkidle2'})
        await asyncio.sleep(1)
        await page.screenshot({'path': f'screenshot_{name}.png'})
        await page.close()
        print(f"✓ {name}")
    
    await browser.close()

asyncio.run(screenshot())
