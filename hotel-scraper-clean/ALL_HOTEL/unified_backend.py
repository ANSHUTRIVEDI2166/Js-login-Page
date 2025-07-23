import os
import json
import subprocess
import pandas as pd
from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from typing import List
from send_email import send_email_with_excel

app = FastAPI(title="Hotel Scraper API (Unified)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Map platform to their extraction script and output
PLATFORM_CONFIG = {
    "booking": {"html": "booking_page.html", "extractor": "Booking_BeautifulSoup.py", "json": "booking_room_data.json"},
    "agoda": {"html": "agoda_page.html", "extractor": "Agoda_BeautifulSoup.py", "json": "agoda_room_data.json"},
    "airbnb": {"html": "airbnb_page.html", "extractor": "Airbnb_BeautifulSoup.py", "json": "airbnb_room_data.json"},
    "expedia": {"html": "expedia_page.html", "extractor": "Expedia_BeautifulSoup.py", "json": "expedia_room_data.json"},
    "trip": {"html": "trip_page.html", "extractor": "Trip_BeautifulSoup.py", "json": "trip_room_data.json"},
    "yatra": {"html": "yatra_page.html", "extractor": "Yatra_BeautifulSoup.py", "json": "yatra_room_data.json"},
    "travelguru": {"html": "travelguru_page.html", "extractor": "Travelguru_BeautifulSoup.py", "json": "travelguru_room_data.json"},
    "cleartrip": {"html": "cleartrip_page.html", "extractor": "Cleartrip_BeautifulSoup.py", "json": "cleartrip_room_data.json"},
    "goibibo": {"json": "firecrawl_output.json", "extractor": "goibibo_extractor.py"},
    "mmt": {"json": "mmt_firecrawl_output.json", "extractor": "mmt_from_json.py"}
}

@app.get("/")
async def home():
    """Serve the main HTML interface"""
    return FileResponse("index.html", media_type="text/html")

@app.get("/run-selected/")
async def run_selected(
    checkin: str = Query(...),
    checkout: str = Query(...),
    hotels: List[str] = Query(...),
    user_email: str = Query(...)
):
    # 1. Download HTMLs (for Playwright-based platforms)
    playwright_sites = [h for h in hotels if h in PLATFORM_CONFIG and 'html' in PLATFORM_CONFIG[h]]
    if playwright_sites:
        subprocess.run(["python", "main.py", "--checkin", checkin, "--checkout", checkout, "--sites", *playwright_sites], check=True)

    # 2. Run extractors for each platform
    merged_data = {}
    for h in hotels:
        conf = PLATFORM_CONFIG.get(h)
        if not conf:
            continue
        # For Firecrawl/JSON-based platforms
        if h == "mmt":
            # Always run firecrawl_mmt.py before extracting MMT data
            subprocess.run(["python", "firecrawl_mmt.py"], check=True)
            subprocess.run(["python", conf["extractor"]], check=True)
            with open(conf["json"], "r", encoding="utf-8") as f:
                merged_data[h] = json.load(f)
        elif h == "goibibo":
            # Always run firecrawl_goibibo.py before extracting Goibibo data
            subprocess.run(["python", "firecrawl_goibibo.py"], check=True)
            subprocess.run(["python", conf["extractor"]], check=True)
            with open(conf["json"], "r", encoding="utf-8") as f:
                merged_data[h] = json.load(f)
        else:
            # For BeautifulSoup-based platforms
            subprocess.run(["python", conf["extractor"]], check=True)
            with open(conf["json"], "r", encoding="utf-8") as f:
                merged_data[h] = json.load(f)

    # 3. Smart Excel formatting based on JSON structure
    excel_path = "merged_hotel_data.xlsx"
    
    def smart_excel_format(platform_name, data):
        """Intelligently format JSON data for Excel based on platform and structure"""
        
        try:
            rooms = []
            
            # Handle different JSON structures per platform
            if isinstance(data, dict) and "room_options" in data:
                # Goibibo/MMT format
                rooms = data["room_options"]
                
            elif isinstance(data, list):
                for hotel in data:
                    try:
                        if "Room Details" in hotel:
                            # Booking.com format
                            for room in hotel["Room Details"]:
                                room["Hotel Name"] = hotel.get("Hotel Name", "Unknown")
                                rooms.append(room)
                                
                        elif "Rooms" in hotel:
                            # Agoda/Travelguru/etc format  
                            hotel_name = hotel.get("Hotel Name", "Unknown")
                            rooms_data = hotel["Rooms"]
                            
                            # Handle case where Rooms might be a string instead of list
                            if isinstance(rooms_data, str):
                                formatted_room = {
                                    "Hotel Name": hotel_name,
                                    "Room Type": rooms_data,
                                    "Description": "",
                                    "Capacity": "",
                                    "Price": "",
                                    "Total": ""
                                }
                                rooms.append(formatted_room)
                            elif isinstance(rooms_data, list):
                                for room_type in rooms_data:
                                    # Handle case where room_type might be a string
                                    if isinstance(room_type, str):
                                        formatted_room = {
                                            "Hotel Name": hotel_name,
                                            "Room Type": room_type,
                                            "Description": "",
                                            "Capacity": "",
                                            "Price": "",
                                            "Total": ""
                                        }
                                        rooms.append(formatted_room)
                                    elif isinstance(room_type, dict):
                                        if "sub_rooms" in room_type:
                                            # Has sub-rooms
                                            for sub_room in room_type["sub_rooms"]:
                                                formatted_room = {
                                                    "Hotel Name": hotel_name,
                                                    "Room Type": room_type.get("title", "Unknown"),
                                                    "Description": sub_room.get("description", ""),
                                                    "Capacity": sub_room.get("capacity", ""),
                                                    "Price": sub_room.get("price", ""),
                                                    "Total": sub_room.get("total_price", "")
                                                }
                                                rooms.append(formatted_room)
                                        else:
                                            # Direct room data
                                            formatted_room = {
                                                "Hotel Name": hotel_name,
                                                "Room Type": room_type.get("title", room_type.get("Room Type", "Unknown")),
                                                "Description": room_type.get("description", ""),
                                                "Capacity": room_type.get("capacity", room_type.get("Number of Guests", "")),
                                                "Price": room_type.get("price", room_type.get("Today's Price", "")),
                                                "Conditions": room_type.get("Booking Conditions", "")
                                            }
                                            rooms.append(formatted_room)
                        else:
                            # Direct room data in list - handle various formats
                            if isinstance(hotel, dict):
                                rooms.append(hotel)
                            else:
                                # If it's not a dict, convert to basic format
                                rooms.append({"Hotel Name": "Unknown", "Room Type": str(hotel)})
                    except Exception as e:
                        print(f"Error processing hotel data for {platform_name}: {e}")
                        continue
            else:
                rooms = [data] if isinstance(data, dict) else []
            
            if not rooms:
                return pd.DataFrame([{"Status": f"No room data found for {platform_name}"}])
            
            # Create DataFrame
            df = pd.DataFrame(rooms)
            
        except Exception as e:
            print(f"Error in smart_excel_format for {platform_name}: {e}")
            return pd.DataFrame([{"Status": f"Error processing {platform_name}: {str(e)}"}])
        
        # Clean up price columns (remove currency symbols)
        price_columns = ['Price', 'Total', 'Today\'s Price', 'price', 'total_price']
        for col in price_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('₹', '').str.replace('Rs.', '').str.replace(',', '').str.strip()
        
        # Clean up capacity/guest info
        capacity_columns = ['Capacity', 'Number of Guests', 'capacity']
        for col in capacity_columns:
            if col in df.columns:
                df[col] = df[col].astype(str).str.replace('Max persons:', '').str.replace('Room capacity information:', '').str.strip()
        
        # Reorder columns for better readability
        preferred_order = ['Hotel Name', 'Room Type', 'Description', 'Capacity', 'Price', 'Total', 'Conditions']
        
        # Keep existing columns in preferred order, then add any extras
        existing_cols = [col for col in preferred_order if col in df.columns]
        remaining_cols = [col for col in df.columns if col not in existing_cols]
        final_cols = existing_cols + remaining_cols
        
        if final_cols:
            df = df[final_cols]
        
        return df

    with pd.ExcelWriter(excel_path, engine='xlsxwriter') as writer:
        for platform, data in merged_data.items():
            try:
                df = smart_excel_format(platform, data)
                sheet_name = platform.capitalize()[:31]
                df.to_excel(writer, sheet_name=sheet_name, index=False)
                
                # Format the sheet for better readability
                worksheet = writer.sheets[sheet_name]
                worksheet.set_column('A:Z', 20)  # Set column width
                
                # Add header formatting
                header_format = writer.book.add_format({
                    'bold': True,
                    'text_wrap': True,
                    'valign': 'top',
                    'fg_color': '#D7E4BC',
                    'border': 1
                })
                
                for col_num, value in enumerate(df.columns.values):
                    worksheet.write(0, col_num, value, header_format)
            except Exception as e:
                print(f"Error creating Excel sheet for {platform}: {e}")
                # Create error sheet
                error_df = pd.DataFrame([{"Status": f"Error processing {platform}", "Error": str(e)}])
                error_df.to_excel(writer, sheet_name=f"{platform}_error"[:31], index=False)

    # 4. Send email
    send_email_with_excel(excel_path, user_email)

    return {"status": "success", "details": f"Data scraped and emailed for: {', '.join(hotels)}"}
