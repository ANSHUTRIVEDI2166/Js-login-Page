import json
from bs4 import BeautifulSoup

# Load the saved HTML file
with open("travelguru_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}

# 🔹 Hotel Name
try:
    hotel_elem = soup.select_one("span[class='fl ng-binding']")
    hotel_name = hotel_elem.get_text(strip=True) if hotel_elem else "N/A"
except:
    hotel_name = "N/A"
data["Hotel Name"] = hotel_name

# 🔹 Review Count
# try:
#     review_elem = soup.select_one("span[class='ng-scope'] a")
#     review_count = review_elem.get_text(strip=True) if review_elem else "N/A"
# except:
#     review_count = "N/A"
# data["Review Count"] = review_count
#
# # 🔹 Rating
# try:
#     rating_elem = soup.select_one("span[class='fl mr10 fs-18 fm-lb green ng-binding']")
#     rating = rating_elem.get_text(strip=True) if rating_elem else "N/A"
# except:
#     rating = "N/A"
# data["Rating"] = rating

# 🔹 Highlights / Amenities
# highlights = []
# try:
#     sections = soup.select("div[class='tipsy from-right-top'] div")
#     for section in sections:
#         p_tags = section.select("p")
#         for p in p_tags:
#             text = p.get_text(strip=True)
#             if text:
#                 highlights.append(text)
#                 break  # take only the first <p> per section
# except:
#     pass
#
# data["Highlights"] = highlights if highlights else "N/A"

# 🔹 Room Data
rooms = []
seen = set()
try:
    sections = soup.select("div[class='template-2 full row room-details-wrapper cr-wrapper ng-scope']")
    for section in sections:
        # Room Title
        title_elem = section.select_one("p[class='cr-name ng-binding']")
        title = title_elem.get_text(strip=True) if title_elem else "N/A"

        sub_rooms = []
        blocks = section.select("li[class='row cr-det']")
        for block in blocks:
            # Description
            desc_elem = block.select_one("span[class='room-content fs-14 txt-new-gray ng-binding']")
            desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"

            # Capacity
            cap_elem = block.select_one("div[ng-if='room.overview.guest.showGuestIcon']")
            if cap_elem:
                adult_icons = cap_elem.select("i.ytfi-adult")
                kid_icons = cap_elem.select("i.ytfi-kid")
                adult_count = len(adult_icons)
                kid_count = len(kid_icons)

                cap = []
                if adult_count:
                    cap.append(f"{adult_count} Adult{'s' if adult_count > 1 else ''}")
                if kid_count:
                    cap.append(f"{kid_count} Kid{'s' if kid_count > 1 else ''}")

                cap = " | ".join(cap)
            else:
                cap_elem_alt = block.select_one("div[ng-if=' !room.overview.guest.showGuestIcon']")
                print(cap_elem_alt)
                if cap_elem_alt:
                    li_items = cap_elem_alt.select("li")
                    cap = " | ".join(li.get_text(strip=True) for li in li_items if li.get_text(strip=True))
                else:
                    cap = "N/A"

            # Price
            price_elem = block.select_one("span[class='fs-28 bold ng-binding']")
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
json_filename = "travelguru_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")
