import json
from bs4 import BeautifulSoup

# Load the saved HTML file
with open("expedia_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}

# --- Hotel Name ---
try:
    hotelname = soup.select_one("h1.uitk-heading.uitk-heading-3")
    data["Hotel Name"] = hotelname.get_text(strip=True) if hotelname else "N/A"
except Exception as e:
    print(f"⚠️ Hotel name error: {e}")
    data["Hotel Name"] = "N/A"

# --- Rating ---
# try:
#     rating_elem = soup.select_one("span.uitk-badge-base-text")
#     data["Rating"] = rating_elem.get_text(strip=True) if rating_elem else "N/A"
# except Exception as e:
#     print(f"⚠️ Rating error: {e}")
#     data["Rating"] = "N/A"
#
# # --- Review Count ---
# try:
#     review_elem = soup.select_one("button[data-stid='reviews-link']")
#     data["Review"] = review_elem.get_text(strip=True) if review_elem else "N/A"
# except Exception as e:
#     print(f"⚠️ Review error: {e}")
#     data["Review"] = "N/A"
#
# # --- Amenities ---
# try:
#     amenity_items = soup.select("div.hp_desc_important_facilities ul li")
#     amenities = [item.get_text(strip=True) for item in amenity_items]
#     data["Amenities"] = " | ".join(amenities) if amenities else "N/A"
# except Exception as e:
#     print(f"⚠️ Amenities error: {e}")
#     data["Amenities"] = "N/A"

# --- Room Details ---
room_data = []
seen_room_types = {}

try:
    room_blocks = soup.find_all("div", attrs={"data-stid": lambda x: x and "property-offer" in x})
    print(room_blocks)
    for block in room_blocks:

        room_info = {}

        # Room Type
        room_type_elem = block.select_one("h3.uitk-heading.uitk-heading-6")
        room_type = room_type_elem.get_text(strip=True) if room_type_elem else "N/A"
        room_info["Room Type"] = room_type

        # Sleeps / Guests
        guest_elem = None
        for div in block.find_all("div"):
            if div.string and "Sleeps" in div.string:
                guest_elem = div
                break
        guests = guest_elem.get_text(strip=True) if guest_elem else "N/A"
        room_info["Number of Guests"] = guests

        # Price
        price_elem = None
        for div in block.find_all("div"):
            if div.string and "The current price" in div.string:
                price_elem = div
                break
        price = price_elem.get_text(strip=True) if price_elem else "N/A"
        if price != "N/A":
            price = price.replace("The current price is", "").strip()
        room_info["Today's Price"] = price

        # Booking Conditions
        condition_elem = block.select_one("ul.uitk-spacing.uitk-spacing-padding-blockstart-three li")
        if not condition_elem:
            condition_elem = block.select_one("ul li")
        conditions = condition_elem.get_text(strip=True) if condition_elem else "N/A"
        room_info["Booking Conditions"] = conditions

        # 🛑 Skip blocks without valid Room Type or Guest info
        if room_type == "N/A" or guests == "N/A":
            continue

        # ✅ Deduplicate by Room Type + Guests
        key = (room_type, guests)
        if key not in seen_room_types:
            seen_room_types[key] = room_info
        else:
            # Prefer one with price
            if seen_room_types[key]["Today's Price"] == "N/A" and price != "N/A":
                seen_room_types[key] = room_info

    # Final room data list
    room_data = list(seen_room_types.values())

    if not room_data:
        room_data.append({"Room Info": "No rooms found"})

except Exception as e:
    print(f"❌ Could not parse room table: {e}")
    room_data.append({"Room Info": "Error parsing room data"})

data["Room Details"] = room_data

# --- Save to JSON ---
all_hotels_data.append(data)
json_filename = "expedia_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")
