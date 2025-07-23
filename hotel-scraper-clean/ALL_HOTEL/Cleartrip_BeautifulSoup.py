import json
from bs4 import BeautifulSoup

# Load the saved HTML file
with open("cleartrip_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}

# 🔹 Hotel Name
hotel_elem = soup.select_one("h1.sc-fqkvVR.fGeVYp")
data["Hotel Name"] = hotel_elem.get_text(strip=True) if hotel_elem else "N/A"

# 🔹 Rating
# rating_elem = soup.select_one("h1.sc-fqkvVR.eHmROS")
# data["Rating"] = rating_elem.get_text(strip=True) if rating_elem else "N/A"
#
# # 🔹 Highlights / Amenities
# highlights = []
# highlight_section = soup.select_one("div.sc-aXZVg.cNXFsj.flex.flex-wrap.flex-between.flex-rg-6")
# if highlight_section:
#     highlights = [div.get_text(strip=True) for div in highlight_section.select("div") if div.get_text(strip=True)]
# data["Highlights"] = highlights if highlights else "N/A"
#
# 🔹 Room Data
rooms = []
seen = set()
sections = soup.select("div.sc-aXZVg.iWfHoM.component-stacked-slots")
for section in sections:
    title_elem = section.select_one("h4.sc-fqkvVR.PmZQd")
    title = title_elem.get_text(strip=True) if title_elem else "N/A"

    sub_rooms = []
    blocks = section.select("div.sc-aXZVg.gaaSNY.flex.flex-column.pt-6.px-6.pb-5.inclusionCardWrapper")
    for block in blocks:
        desc_elem = block.select_one("h4.sc-fqkvVR.kYqeTM.room--inclusions--header")
        desc = desc_elem.get_text(strip=True) if desc_elem else "N/A"

        price_elem = block.select_one("h5.sc-fqkvVR.PmZQd.mr-1")
        price = price_elem.get_text(strip=True) if price_elem else "N/A"

        key = (title, desc, price)
        if key not in seen:
            seen.add(key)
            sub_rooms.append({
                "description": desc,
                "price": price
            })

    if sub_rooms:
        rooms.append({
            "title": title,
            "sub_rooms": sub_rooms
        })

data["Rooms"] = rooms if rooms else "N/A"

# ✅ Save to JSON
all_hotels_data.append(data)
json_filename = "cleartrip_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")
