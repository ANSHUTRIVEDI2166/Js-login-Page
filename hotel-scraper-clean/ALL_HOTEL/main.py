import asyncio
import json
import subprocess
from playwright.async_api import async_playwright
from datetime import datetime
import os
import argparse

# --- Argument Parser Setup ---
parser = argparse.ArgumentParser()
parser.add_argument("--checkin", required=True)
parser.add_argument("--checkout", required=True)
parser.add_argument("--adults", type=int, default=2)
parser.add_argument("--children", type=int, default=0)
parser.add_argument("--rooms", type=int, default=1)
# ADDED: New argument to specify which sites to scrape
parser.add_argument("--sites", nargs='*', help="A list of specific sites to download.")

args = parser.parse_args()

# This line should be commented out as per our previous discussions
# asyncio.run(run_combined_scraper(args.checkin, args.checkout))

# Use arguments dynamically
checkin = args.checkin
checkout = args.checkout
adults = args.adults
children = args.children
rooms = args.rooms

print(f"Downloading HTML for: {checkin} to {checkout}, {adults} adults, {children} children, {rooms} room(s)")

# --- Derived date formats ---
dt_checkin = datetime.strptime(checkin, "%Y-%m-%d")
dt_checkout = datetime.strptime(checkout, "%Y-%m-%d")
cin = dt_checkin.strftime("%d%m%y")
chout = dt_checkout.strftime("%d%m%y")
inc = dt_checkin.strftime("%d/%m/%Y")
outc = dt_checkout.strftime("%d/%m/%Y")
def format_date(d):
    return datetime.strptime(d, "%d%m%y").strftime("%d%%2F%m%%2F%Y")
formatted_checkin = format_date(cin)
formatted_checkout = format_date(chout)
nights = (dt_checkout - dt_checkin).days

# --- Construct URLs ---
urls = {
    "booking": (
        f"https://www.booking.com/hotel/in/goverdhan-greens-resort.en-gb.html?"
        f"checkin={checkin}&checkout={checkout}&group_adults={adults}&group_children={children}&no_rooms={rooms}&selected_currency=INR"
    ),
    "agoda": (
        f"https://www.agoda.com/goverdhan-greens/hotel/baradia-in.html?"
        f"adults={adults}&children={children}&rooms={rooms}&checkIn={checkin}&los={nights}&currencyCode=INR"
    ),
    "expedia":(
        f"https://www.expedia.co.in/Dwarka-Hotels-Goverdhan-Greens-Resort-Dwarka.h18105883.Hotel-Information?"
        f"chkin={checkin}&chkout={checkout}"
    ),
    "airbnb": (
        f"https://www.airbnb.co.in/rooms/1119198480825500272?"
        f"adults={adults}&check_in={checkin}&check_out={checkout}&search_mode=regular_search"
    ),
    "trip":(
        f"https://in.trip.com/hotels/detail/?cityId=536508&hotelId=9997818"
        f"&checkIn={checkin}&checkOut={checkout}&adult={adults}&children={children}&crn=1"
    ),
    "cleartrip": (
        f"https://www.cleartrip.com/hotels/details/goverdhan-greens-resort-3936440?"
        f"c={cin}%7C{chout}&r={adults}%2C{children}"
    ),
    "travelguru": (
        f"https://hotels.travelguru.com/hotel-search/tgdom/details?"
        f"checkoutDate={outc}&checkinDate={inc}&roomRequests[0].id={rooms}&roomRequests[0].noOfAdults={adults}&roomRequests[0].noOfChildren={children}&source=BOOKING_ENGINE&tenant=TGB2C&city.name=Dwarka&city.code=Dwarka&country.name=India&country.code=IND&hotelId=00014691"
    ),
    "yatra": (
        f"https://hotel.yatra.com/nextui/hotel-detail?"
        f"checkoutDate={formatted_checkout}&checkinDate={formatted_checkin}"
        f"&roomRequests%5B0%5D.id={rooms}&roomRequests%5B0%5D.noOfAdults={adults}"
        f"&roomRequests%5B0%5D.noOfChildren={children}&hotelId=00014691"
        f"&source=BOOKING_ENGINE&pg=1&tenant=B2C&isPersnldSrp=1&city.name=Dwarka&city.code=Dwarka&state.name=Dwarka&state.code=Dwarka&country.name=IND&country.code=IND&propertySource=TGU"
    )
}

# --- ADDED: Filter URLs based on --sites argument ---
if args.sites:
    urls_to_download = {site: url for site, url in urls.items() if site in args.sites}
    print(f"Targeting specific sites: {list(urls_to_download.keys())}")
else:
    urls_to_download = urls
    print("No specific sites provided, targeting all sites.")


# --- Scraper Function ---
async def save_site_html():
    async with async_playwright() as p:
        browser = await p.firefox.launch(headless=True)
        context = await browser.new_context(
            viewport={'width': 1920, 'height': 1080},
            locale='en-IN',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0'
        )
        page = await context.new_page()

        # MODIFIED: Loop over the filtered dictionary
        for site, url in urls_to_download.items():
            try:
                print(f"\n🌍 Navigating to {site.capitalize()}...")
                await page.goto(url, timeout=120_000, wait_until='domcontentloaded')
                await page.wait_for_timeout(4000)

                # ... (rest of your site-specific logic for agoda, booking, etc.) ...
                if site == "agoda":
                    pass # your agoda logic here
                elif site == "booking":
                    pass # your booking logic here
                elif site == "expedia":
                    pass # your expedia logic here
                elif site == "trip":
                     print("🛫 Running Trip.com scraper via Trip_HTMLDownload.py...")
                     subprocess.run(["python", "Trip_HTMLDownload.py", url])
                     continue
                
                html = await page.content()
                filename = f"{site}_page.html"
                with open(filename, "w", encoding="utf-8") as f:
                    f.write(html)
                print(f"✅ Saved HTML to {filename}")

                await page.wait_for_timeout(3000)

            except Exception as e:
                print(f"❌ Failed to load {site}: {e}")
                try:
                    await page.screenshot(path=f"{site}_error.png")
                    print(f"📸 Saved error screenshot: {site}_error.png")
                except:
                    print("📸 Screenshot also failed.")

        await context.close()
        await browser.close()
        print("🧹 Browser session closed.")


# --- Run it ---
if __name__ == "__main__":
    print("🚀 Starting HTML scraper...")
    asyncio.run(save_site_html())