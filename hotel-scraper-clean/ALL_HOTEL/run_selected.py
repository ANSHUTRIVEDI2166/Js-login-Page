from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import subprocess
import os
import json
from typing import List
import asyncio

# Attempt to import the required functions from your custom module
try:
    from Combined_hotel_scrapping import (
        fetch_and_process,
        GOIBIBO_ROBOT_ID,
        MMT_ROBOT_ID,
        parse_goibibo_text,
        parse_mmt_text,
        send_combined_email
    )
    BROWSEAI_AVAILABLE = True
except ImportError:
    BROWSEAI_AVAILABLE = False
    print("⚠️ Warning: 'Combined_hotel_scrapping.py' not found. BrowseAI functionality will be disabled.")


app = FastAPI(title="Hotel Scraper API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/run-selected/")
async def run_selected(
    checkin: str = Query(..., description="Check-in date in YYYY-MM-DD format"),
    checkout: str = Query(..., description="Check-out date in YYYY-MM-DD format"),
    hotels: List[str] = Query(..., description="A list of hotel platforms to scrape")
):
    print(f"\U0001F4C5 Checkin: {checkin}, Checkout: {checkout}")
    print(f"\U0001F3E8 Hotels selected: {hotels}")

    print("\n--- Starting Step 1: HTML Download ---")
    sites_for_downloader = [h for h in hotels if h != 'browseai']

    if sites_for_downloader:
        try:
            command = ["python", "main.py", "--checkin", checkin, "--checkout", checkout, "--sites", *sites_for_downloader]
            print(f"\U0001F680 Running downloader for: {sites_for_downloader}")
            subprocess.run(command, check=True, timeout=300)
            print("✅ HTML downloader finished successfully.")
        except (subprocess.CalledProcessError, subprocess.TimeoutExpired) as e:
            error_msg = f"❌ Downloader script (main.py) failed: {e}"
            print(error_msg)
            return {"status": "error", "details": error_msg}
    else:
        print("No sites selected for Playwright download, skipping.")

    print("\n--- Starting Step 2: Data Processing ---")
    all_scraped_data = {}

    try:
        if "browseai" in hotels and BROWSEAI_AVAILABLE:
            print("📦 Running BrowseAI scraper for Goibibo and MMT...")
            ci = datetime.strptime(checkin, "%Y-%m-%d").strftime("%m%d%Y")
            co = datetime.strptime(checkout, "%Y-%m-%d").strftime("%m%d%Y")

            goibibo_url = f"https://www.goibibo.com/hotels/hotel-details/?checkin={checkin}&checkout={checkout}&roomString=1-2-0&searchText=Goverdhan%20Greens"
            mmt_url = f"https://www.makemytrip.com/hotels/hotel-details/?hotelId=201203212233088600&checkin={ci}&checkout={co}"

            try:
                goibibo_task = asyncio.create_task(fetch_and_process(GOIBIBO_ROBOT_ID, goibibo_url, "Goverdhan Greens (Goibibo)", parse_goibibo_text))
                mmt_task = asyncio.create_task(fetch_and_process(MMT_ROBOT_ID, mmt_url, "Goverdhan Greens (MMT)", parse_mmt_text))

                goibibo_file, goibibo_data = await goibibo_task
                mmt_file, mmt_data = await mmt_task

                all_scraped_data["goibibo"] = goibibo_data
                all_scraped_data["mmt"] = mmt_data

                print("✅ Collected Goibibo and MMT data.")
                send_combined_email([goibibo_file, mmt_file])

            except Exception as e:
                print(f"⚠️ BrowseAI scrape failed: {e}")

        site_map = {
            "booking": ("Booking_BeautifulSoup.py", "booking_room_data.json"),
            "agoda": ("Agoda_BeautifulSoup.py", "agoda_room_data.json"),
            "trip": ("Trip_BeautifulSoup.py", "trip_room_data.json"),
            "expedia": ("Expedia_BeautifulSoup.py", "expedia_room_data.json"),
            "airbnb": ("Airbnb_BeautifulSoup.py", "airbnb_room_data.json"),
            "travelguru": ("Travelguru_BeautifulSoup.py", "travelguru_room_data.json"),
            "yatra": ("Yatra_BeautifulSoup.py", "yatra_room_data.json"),
            "cleartrip": ("Cleartrip_BeautifulSoup.py", "cleartrip_room_data.json"),
        }

        for hotel in hotels:
            if hotel in site_map:
                script, json_output_file = site_map[hotel]
                print(f"⚙️ Running parser: {script}...")
                subprocess.run(["python", script], check=True, timeout=60)

                if os.path.exists(json_output_file):
                    print(f"✅ Parser {script} finished, loading {json_output_file}.")
                    with open(json_output_file, 'r', encoding='utf-8') as f:
                        all_scraped_data[hotel] = json.load(f)
                else:
                    print(f"⚠️ Output file {json_output_file} not found after parsing.")

        print("\n🎉 Process complete. Returning all collected data to the frontend.")
        return all_scraped_data

    except Exception as e:
        error_msg = f"❌ An unexpected error occurred during processing: {e}"
        print(error_msg)
        return {"status": "error", "details": error_msg}
