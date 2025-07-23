import json
from bs4 import BeautifulSoup

# Load the saved HTML file
with open("agoda_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}

# 🔹 Click all "Show more deals" spans — this is just for debug info, not functional in BS4
try:
    deal_spans = soup.find_all("span", string=lambda text: text and "Show more deals" in text)
    for span in deal_spans:
        parent = span.find_parent()
        print(f"Found a 'Show more deals' span under: {parent.name}")
except Exception as e:
    print(f"❌ Error locating 'Show more deals': {e}")

# 🔹 Hotel Name
try:
    hotel_elem = soup.select_one("h1[data-selenium='hotel-header-name']")
    hotel_name = hotel_elem.get_text(strip=True) if hotel_elem else "N/A"
except:
    hotel_name = "N/A"
data["Hotel Name"] = hotel_name

# 🔹 Review Count
# try:
#     review_elem = soup.select_one("button#reviews-tab-1")
#     review_count = review_elem.get_text(strip=True) if review_elem else "N/A"
# except:
#     review_count = "N/A"
# data["Review Count"] = review_count
#
# # 🔹 Rating
# try:
#     rating_elem = soup.select_one("h2.sc-jrAGrp.sc-kEjbxe > span")
#     rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
# except:
#     rating = "N/A"
# data["Rating"] = rating
#
# # 🔹 Highlights / Amenities
# highlights = []
# try:
#     section = soup.select_one("div[data-element-name='atf-top-amenities']")
#     if section:
#         highlights = [p.get_text(strip=True) for p in section.select("p") if p.get_text(strip=True)]
# except:
#     pass
# data["Highlights"] = highlights if highlights else "N/A"

# 🔹 Room Data
rooms = []
seen = set()
try:
    sections = soup.select("div.MasterRoom, div.MasterRoom.MasterRoom--withMoreLess")
    for section in sections:
        # Room Title
        title_elem = section.select_one("span[data-selenium='masterroom-title-name']")
        title = title_elem.get_text(strip=True) if title_elem else "N/A"

        sub_rooms = []
        blocks = section.select("div.ChildRoomsList-room-contents")
        for block in blocks:
            # Description
            desc_elem = block.select_one("div.ChildRoomsList-room-featurebuckets")
            desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"

            # Capacity
            cap_elem = block.select_one("button[data-selenium='ChildRoomsList-capacity-container']")
            cap = cap_elem.get("aria-label", "N/A").strip() if cap_elem else "N/A"

            # Price
            price_elem = block.select_one("span.finalPrice")
            price = price_elem.get_text(strip=True).replace("₹", "").replace(",", "") if price_elem else "N/A"

            # Avoid duplicates
            key = (title, desc, cap, price)
            if key not in seen:
                seen.add(key)
                sub_rooms.append({
                    "description": desc,
                    "capacity": cap,
                    "price": price
                })

        rooms.append({
            "title": title,
            "sub_rooms": sub_rooms
        })
except Exception as e:
    print("Room error:", e)

# ✅ Add room data to final hotel data
data["Rooms"] = rooms if rooms else "N/A"

# ✅ Final output
all_hotels_data.append(data)
json_filename = "agoda_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")
