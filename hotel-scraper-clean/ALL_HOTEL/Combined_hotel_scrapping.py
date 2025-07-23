from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse
import requests
import time
import re
import pandas as pd
import tempfile
import smtplib
from email.message import EmailMessage
from datetime import datetime

app = FastAPI()

API_KEY = "0c0ddd40-f3e2-4000-bfc6-dfa794bc88fb:d3c10830-c4ba-4803-a6a0-b45c81def1b4"
HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}
GOIBIBO_ROBOT_ID = "6982b9ab-2ee4-44c2-85ec-14090a8eb244"
MMT_ROBOT_ID = "6982b9ab-2ee4-44c2-85ec-14090a8eb244"

SENDER_EMAIL = "tithi.radia@gmail.com"
SENDER_PASSWORD = "xyxt epsl pysx yktt"
RECEIVER_EMAIL = "manthanjethwani02@gmail.com"

def extract_text_fields(obj):
    results = []
    if isinstance(obj, dict):
        if "TEXT" in obj and obj["TEXT"]:
            results.append(obj["TEXT"])
        for value in obj.values():
            results.extend(extract_text_fields(value))
    elif isinstance(obj, list):
        for item in obj:
            results.extend(extract_text_fields(item))
    return results

def parse_goibibo_text(extracted_text):
    raw_text = "\n".join(extracted_text)
    room_data = []
    room_pattern = re.finditer(
        r"(?P<room_name>[A-Z][^\n]+Room[^\n]*)\s*\+\d+\sPhotos.*?(?=\n[A-Z][^\n]+Room|\Z)",
        raw_text,
        re.DOTALL
    )
    for room_match in room_pattern:
        room_name = room_match.group("room_name").strip()
        room_block = room_match.group(0)
        plans = []
        for plan_match in re.finditer(
            r"\d+\.\s(?P<plan_name>.*?)\s+(?:Non-Refundable|Free Cancellation|Book @ ₹0.*?)?\s*View plan.*?₹[\s]?[0-9,]+\s+(?P<price>[\d,]+)\s+\+\s*₹\s*(?P<taxes>[\d,]+)\s+taxes & fees",
            room_block,
            re.DOTALL
        ):
            plans.append({
                "Plan": plan_match.group("plan_name").strip(),
                "Price": f"₹{plan_match.group('price').strip()} + ₹{plan_match.group('taxes').strip()} taxes & fees"
            })
        if plans:
            room_data.append({"Room Type": room_name, "Plans": plans})
    return room_data

def parse_mmt_text(extracted_text):
    raw_text = "\n".join(extracted_text)
    room_data = []
    room_blocks = re.split(
        r"(?=\n?(?P<room_name>(?:Deluxe|Super|Superior|Executive|Classic|Premium|Suite)[^\n]+?(?:Room|Rooms)(?: with Balcony)?))",
        raw_text,
        flags=re.IGNORECASE
    )
    for i in range(1, len(room_blocks), 2):
        room_name = room_blocks[i].strip().title()
        room_block = room_blocks[i + 1] if i + 1 < len(room_blocks) else ""
        plans = []
        plan_regex = re.finditer(
            r"(?P<plan_name>(Room Only|Room With Free Cancellation|Room with Breakfast|Room With Free Cancellation \| Breakfast only|Free Breakfast \| Free Cancellation))"
            r"(.*?)₹\s?[\d,]+\s+₹\s?(?P<price>[\d,]+)\s*\+\s*₹\s*(?P<taxes>[\d,]+)\s+Taxes & Fees",
            room_block,
            flags=re.DOTALL | re.IGNORECASE
        )
        for match in plan_regex:
            plans.append({
                "Plan": match.group("plan_name").strip(),
                "Price": f"₹{match.group('price').strip()} + ₹{match.group('taxes').strip()} taxes & fees"
            })
        if plans:
            room_data.append({"Room Type": room_name, "Plans": plans})
    return room_data

def send_combined_email(attachments):
    msg = EmailMessage()
    msg["Subject"] = "Combined Hotel Pricing Report"
    msg["From"] = SENDER_EMAIL
    msg["To"] = RECEIVER_EMAIL
    msg.set_content("Attached are the hotel pricing sheets for both Goibibo and MMT.")
    for path in attachments:
        with open(path, "rb") as f:
            msg.add_attachment(
                f.read(),
                maintype="application",
                subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                filename=path.split("/")[-1]
            )
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(SENDER_EMAIL, SENDER_PASSWORD)
        smtp.send_message(msg)

async def fetch_and_process(robot_id, origin_url, hotel_name, parser):
    payload = {"inputParameters": {"originUrl": origin_url}, "proxy_country": "IN"}
    create_url = f"https://api.browse.ai/v2/robots/{robot_id}/tasks"
    response = requests.post(create_url, headers=HEADERS, json=payload)
    response.raise_for_status()
    task_id = response.json().get("result", {}).get("id")
    if not task_id:
        raise ValueError("Task ID not found")
    time.sleep(180)
    task_url = f"https://api.browse.ai/v2/robots/{robot_id}/tasks/{task_id}"
    task_response = requests.get(task_url, headers=HEADERS)
    task_response.raise_for_status()
    data = task_response.json()
    extracted_text = extract_text_fields(data) 
    parsed_data = parser(extracted_text)
    rows = []
    for room in parsed_data:
        for plan in room["Plans"]:
            rows.append({
                "Hotel Name": hotel_name,
                "Room Type": room["Room Type"],
                "Plan": plan["Plan"],
                "Price": plan["Price"]
            })
    df = pd.DataFrame(rows)
    tmp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".xlsx")
    df.to_excel(tmp_file.name, index=False)
    return tmp_file.name, parsed_data

async def run_combined_scraper(checkin: str, checkout: str):
    ci = datetime.strptime(checkin, "%Y-%m-%d").strftime("%m%d%Y")
    co = datetime.strptime(checkout, "%Y-%m-%d").strftime("%m%d%Y")

    goibibo_url = (
        "https://www.goibibo.com/hotels/hotel-details/"
        f"?checkin={checkin}&checkout={checkout}&roomString=1-2-0"
        "&searchText=Goverdhan%20Greens&locusId=CTXOP&locusType=city"
        "&cityCode=CTXOP&cc=IN&_uCurrency=INR&vcid=8369616161009722573"
        "&giHotelId=2259653877757301726&mmtId=201203212233088600"
        "&topHtlId=201203212233088600&sType=hotel"
    )
    mmt_url = (
        "https://www.makemytrip.com/hotels/hotel-details/"
        f"?hotelId=201203212233088600&_uCurrency=INR&checkin={ci}&checkout={co}"
        "&city=CTXOP&country=IN&lat=22.19207&lng=69.01994"
        "&locusId=CTXOP&locusType=city&rank=1&reference=hotel"
        "&roomStayQualifier=2e0e&rsc=1e2e0e"
        "&searchText=Goverdhan+Greens&topHtlId=201203212233088600"
        "&type=city&mtkeys=undefined&isPropSearch=T"
    )

    try:
        print("📦 Fetching Goibibo Data via BrowseAI...")
        goibibo_file, goibibo_data = await fetch_and_process(
            GOIBIBO_ROBOT_ID, goibibo_url, "Goverdhan Greens (Goibibo)", parse_goibibo_text
        )

        print("📦 Fetching MMT Data via BrowseAI...")
        mmt_file, mmt_data = await fetch_and_process(
            MMT_ROBOT_ID, mmt_url, "Goverdhan Greens (MMT)", parse_mmt_text
        )

        print("📧 Sending Email with Excel attachments...")
        send_combined_email([goibibo_file, mmt_file])

        print("✅ BrowseAI scraping complete.")

    except Exception as e:
        print(f"❌ Error: {e}")