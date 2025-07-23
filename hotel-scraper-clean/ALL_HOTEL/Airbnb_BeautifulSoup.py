import json
from bs4 import BeautifulSoup

# Load the saved Airbnb HTML
with open("airbnb_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
data = {}

# --- Hotel Name ---
try:
    hotel_name_elem = soup.select_one("h1")
    data["Hotel Name"] = hotel_name_elem.get_text(strip=True) if hotel_name_elem else "N/A"
except Exception as e:
    print(f"⚠️ Hotel Name extraction error: {e}")
    data["Hotel Name"] = "N/A"

# --- Rating ---
# try:
#     rating_elem = soup.select_one("div[class='rmtgcc3 atm_c8_o7aogt atm_c8_l52nlx__oggzyc dir dir-ltr']")
#     data["Rating"] = rating_elem.get_text(strip=True) if rating_elem else "N/A"
# except Exception as e:
#     print(f"⚠️ Rating extraction error: {e}")
#     data["Rating"] = "N/A"
#
# # --- Reviews ---
# try:
#     review_elem_anchor = soup.find("div", class_="sdfypm1 atm_h3_1n1ank9 dir dir-ltr")
#     review_text = review_elem_anchor.find_next_sibling("a").get_text(strip=True) if review_elem_anchor else "N/A"
#     data["Review"] = review_text
# except Exception as e:
#     print(f"⚠️ Review extraction error: {e}")
#     data["Review"] = "N/A"

# --- Home Info ---
try:
    home_ol = soup.select_one("ol.lgx66tx.atm_gi_idpfg4.atm_l8_idpfg4.dir.dir-ltr")
    home_items = home_ol.select("li") if home_ol else []
    home_info = [item.get_text(strip=True) for item in home_items if item.get_text(strip=True)]
    data["Home Info"] = " | ".join(home_info) if home_info else "N/A"
except Exception as e:
    print(f"⚠️ Error extracting Home Info: {e}")
    data["Home Info"] = "N/A"
#price
try:
    price_elem = soup.select_one("span[class='umg93v9 atm_7l_rb934l atm_cs_1peztlj atm_rd_14k51in atm_cs_kyjlp1__1v156lz dir dir-ltr']")
    price = price_elem.get_text(strip=True) if price_elem else "N/A"
    data["Price"] = price
except Exception as e:
    print(f"⚠️ Error extracting price: {e}")
    data["Price"] = "N/A"
# --- Store data in JSON ---
json_filename = "airbnb_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump([data], f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")
