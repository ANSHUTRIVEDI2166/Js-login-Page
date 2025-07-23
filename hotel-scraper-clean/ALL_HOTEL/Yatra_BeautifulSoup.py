import json
from bs4 import BeautifulSoup

# Load the saved HTML file
with open("yatra_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}

# 🔹 Hotel Name
try:
    hotel_elem = soup.select_one("h2[class*='Typography_h2']")
    hotel_name = hotel_elem.get_text(strip=True) if hotel_elem else "N/A"
except:
    hotel_name = "N/A"
data["Hotel Name"] = hotel_name

# # 🔹 Review Count
# try:
#     review_elem = soup.select_one("span[class*='reviewCount']")
#     review_count = review_elem.get_text(strip=True) if review_elem else "N/A"
# except:
#     review_count = "N/A"
# data["Review Count"] = review_count
#
# # 🔹 Rating
# try:
#     rating_elem = soup.select_one("span[class*='ratingValue']")
#     rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
# except:
#     rating = "N/A"
# data["Rating"] = rating

# 🔹 Highlights / Amenities
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
    sections = soup.select("div[class='SelectRoomContent_deluxeRoomWrapper__NdSPP false']")
    for section in sections:
        # Room Title
        title_elem = section.select_one("h3[class*='Typography_h3']")
        title = title_elem.get_text(strip=True) if title_elem else "N/A"
        # Capacity
        # Capacity using XPath-equivalent logic
        cap = []
        max_guest_header = section.find("h4", string=lambda text: "Maximum Guests" in text if text else False)
        if max_guest_header:
            # Find all divs with the target class *after* the h4
            facilities_divs = section.find_all("div", class_="DoubleDeluxeRoom_roomFacilities___rcD_")
            for div in facilities_divs:
                h5_tags = div.find_all("h5")
                for h5 in h5_tags:
                    cap_text = h5.get_text(strip=True)
                    if cap_text:
                        cap.append(cap_text)

        # Join multiple capacity values with |
        cap_str = " | ".join(cap) if cap else "N/A"

        # Convert list to '|' separated string
        cap_str = " | ".join(cap) if cap else "N/A"
        sub_rooms = []
        blocks = section.select("div.SelectRoomContent_twinWrapper__7ejWq")
        for block in blocks:
            # Description
            desc_elem = block.select_one("h3[class*='Typography_typography']")
            desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"

            # Price
            price_elem = block.select_one("span[class='HotelCardPrice_discountedPrice__gHVxD']")
            price = price_elem.get_text(strip=True) if price_elem else "N/A"

            # Avoid duplicates
            key = (title, desc, price)
            if key not in seen:
                seen.add(key)
                sub_rooms.append({
                    "description": desc,
                    "price": price
                })

        rooms.append({
            "title": title,
            "capacity": cap,
            "sub_rooms": sub_rooms
        })
except Exception as e:
    print("Room error:", e)

# ✅ Add room data to final hotel data
data["Rooms"] = rooms if rooms else "N/A"

# ✅ Final output
all_hotels_data.append(data)
json_filename = "yatra_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")
