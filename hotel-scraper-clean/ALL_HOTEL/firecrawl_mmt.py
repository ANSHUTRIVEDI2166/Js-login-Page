import asyncio
from firecrawl import AsyncFirecrawlApp
import json

async def main():
    app = AsyncFirecrawlApp(api_key='fc-d59a27e925da4ad2ad1743d349859ef8')

    response = await app.scrape_url(
        url='https://www.makemytrip.com/hotels/hotel-details/?hotelId=201203212233088600&_uCurrency=INR&checkin=07202025&checkout=07212025&city=CTXOP&country=IN&lat=22.19207&lng=69.01994&locusId=CTXOP&locusType=city&rank=1&regionNearByExp=3&roomStayQualifier=2e0e&rsc=1e2e0e&searchText=Goverdhan+Greens&topHtlId=201203212233088600&mtkeys=undefined&isPropSearch=T',
        formats=['markdown'],            #  Markdown only (more stable)
        only_main_content=False,         #  Get full page content
        parse_pdf=False                  #  Keep false for faster scrape
    )

    output_data = {
        "markdown": response.markdown,
        "screenshot": response.screenshot
    }

    with open("mmt_firecrawl_output.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=4)

    print("✅ MMT Markdown saved to mmt_firecrawl_output.json")
    print("🔍 First 300 chars of markdown:\n", response.markdown[:300])

asyncio.run(main())
