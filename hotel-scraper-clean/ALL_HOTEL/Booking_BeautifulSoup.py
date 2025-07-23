import json
from bs4 import BeautifulSoup


# Load the saved HTML file
with open("booking_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}
# Hotel Name
try:
    hotelname = (soup.select_one("h2.ddb12f4f86.pp-header__title"))
    hotel_name=hotelname.get_text(strip=True)
    data["Hotel Name"] = hotel_name
except:
    data["Hotel Name"] = "N/A"
# try:
#     # Use better selector
#     review_elem = soup.select_one("div[data-testid='review-score-component']")
#     review = review_elem.get_text(strip=True)
#     data["Rating & Review"] = review
# except:
#     data["Rating & Review"] = "N/A"
# # Amenities
# try:
#     # Alternative selector that may work
#     amenity_items = soup.select('div.hp_desc_important_facilities ul li')
#     amenities = [item.get_text(strip=True) for item in amenity_items if item.get_text(strip=True)]
#     data["Amenities"] = " | ".join(amenities) if amenities else "N/A"
# except Exception as e:
#     print(f"⚠️ Error extracting amenities: {e}")
#     data["Amenities"] = "N/A"
# Room Table Data
room_data = []
try:
    # Select all room rows
    rows = soup.find_all("tr", class_=lambda x: x and "hprt-table-row" in x)
    #rows = soup.select('table#hprt-table tr.hprt-table-row')
    current_room_type = ""
    for row in rows:
        cells = row.find_all("td")
        if not cells:
            continue
        room_info = {}
        # Room Type
        room_type_elem = row.select_one("span.hprt-roomtype-icon-link")
        if room_type_elem:
            current_room_type = room_type_elem.get_text(strip=True)
        room_info["Room Type"] = current_room_type
        # Number of Guests
        guest_elem = row.select_one("span.bui-u-sr-only")
        room_info["Number of Guests"] = guest_elem.get_text(strip=True) if guest_elem else "N/A"
        # Today's Price
        price_elem = row.select_one("span.prco-valign-middle-helper")
        if price_elem:
            price_text = price_elem.get_text(strip=True).replace('\xa0', '')
            room_info["Today's Price"] = price_text
        else:
            room_info["Today's Price"] = "N/A"
            # Booking Conditions
        condition_elem = row.select_one("td.hprt-table-cell-conditions")
        room_info["Booking Conditions"] = condition_elem.get_text(strip=True) if condition_elem else "N/A"
        # Select Options
        # select_elem = row.select_one("select.hprt-nos-select")
        # if select_elem:
        #     options = [opt.get_text(strip=True) for opt in select_elem.select("option") if opt.get_text(strip=True)]
        # else:
        #     options = []
        # room_info["Select Options"] = options
        room_data.append(room_info)
except Exception as e:
    print(f"❌ Could not parse room table: {e}")
    room_data = [{"Room Info": "Not Available"}]
data["Room Details"] = room_data
#data in json
all_hotels_data.append(data)
json_filename = "booking_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")