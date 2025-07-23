import json
from bs4 import BeautifulSoup

# Load the saved HTML file
with open("trip_page.html", "r", encoding="utf-8") as f:
    html = f.read()

soup = BeautifulSoup(html, "html.parser")
all_hotels_data = []
data = {}
# Hotel
# --- Extract hotel name ---
try:
    hotel_name_tag = soup.find("h1")
    data["Hotel Name"] = hotel_name_tag.get_text(strip=True) if hotel_name_tag else "N/A"
except:
    data["Hotel Name"] = "N/A"

# --- Extract rating ---
# try:
#     rating_tag = soup.select_one("strong[class*='reviewScores']")
#     data["Rating"] = rating_tag.get_text(strip=True) if rating_tag else "N/A"
# except Exception as e:
#     print(f"Error extracting rating: {e}")
#     data["Rating"] = "N/A"
#
# # --- Extract number of reviews ---
# try:
#     review_tag = soup.select_one("div[class*='scoreCount']")
#     if not review_tag:
#         review_tag = soup.find('div', class_=lambda x: x and 'scoreCount' in x)
#     data["Reviews"] = review_tag.get_text(strip=True) if review_tag else "N/A"
# except Exception as e:
#     print(f"⚠️ Error getting review count: {e}")
#     data["Reviews"] = "N/A"
#
#
# # --- Extract highlights ---
# try:
#     # Select the outer div that contains all highlight content
#     highlight_tags = soup.select("div.headHighLight_highlight-content__HfPiA")
#
#     if not highlight_tags:  # If no elements found, handle gracefully
#         data["Highlights"] = "N/A"
#     else:
#         # Iterate through each outer div tag (there might be multiple highlights)
#         highlights = []
#         for tag in highlight_tags:
#             # For each highlight tag, find the inner div elements
#             inner_divs = tag.find_all('div')
#             # Get the text from each inner div and join them using "|"
#             highlight_text = " | ".join(
#                 inner_div.get_text(strip=True) for inner_div in inner_divs if inner_div.get_text(strip=True))
#             if highlight_text:  # If there is any text, append it to the highlights list
#                 highlights.append(highlight_text)
#
#         # If there are highlights found, join them using a pipe "|" symbol
#         data["Highlights"] = " | ".join(highlights) if highlights else "N/A"
#
# except Exception as e:
#     print(f"⚠️ Error retrieving highlights: {e}")
#     data["Highlights"] = "N/A"
#more data
# try:
#     show_more_spans = []
#     for pattern in [
#         "Show Remaining Room Type",
#         "More Room Types",
#         "Show More Room Rate"
#     ]:
#         try:
#             spans = soup.find_all("span", string=lambda text: text and pattern in text)
#             show_more_spans.extend(spans)
#         except Exception as inner_error:
#             print(f"Error while finding spans for pattern '{pattern}': {inner_error}")
# except Exception as outer_error:
#     print(f"Outer loop error: {outer_error}")
#
# for span in show_more_spans:
#     print("✅ Found span:", span.get_text(strip=True))
# --- Extract room details ---
rooms = []
try:
    main_blocks = soup.select(".commonRoomCard__BpNjl")
    for block in main_blocks:
        try:
            main_room_type_tag = block.select_one(".commonRoomCard-title__iYBn2")
            main_room_type = main_room_type_tag.get_text(strip=True) if main_room_type_tag else "N/A"
        except:
            main_room_type = "N/A"

        sub_rooms = []
        try:
            sub_blocks = block.select(".saleRoomItemBox__orNIv")
            for sub in sub_blocks:
                try:
                    sub_room_type_tag = sub.select_one(".saleRoomItemBox-reservationNotesInfoBox__XUpOh")
                    sub_room_type = sub_room_type_tag.get_text(strip=True) if sub_room_type_tag else "N/A"
                except:
                    sub_room_type = "N/A"

                # Sleeps
                try:
                    guest_icons = sub.select(".saleRoomItemBox-guestInfo-adultBox__5QrYn i")
                    sleeps_count = len(guest_icons)
                    sleep_extra = sub.select_one(".saleRoomItemBox-guestInfo-adultBox__5QrYn span")
                    sleep_text = f"Sleeps {sleeps_count}"
                    if sleep_extra:
                        sleep_text += f" ({sleep_extra.get_text(strip=True)})"
                except:
                    sleep_text = "N/A"

                # Price
                try:
                    price_tag = sub.select_one(".saleRoomItemBox-priceBox-displayPrice__gWiOr span")
                    price = price_tag.get_text(strip=True) if price_tag else "N/A"
                except:
                    price = "N/A"

                sub_rooms.append({
                    "Sub Room Type": sub_room_type,
                    "Sleeps": sleep_text,
                    "Today's Price": price
                })
        except:
            pass

        rooms.append({
            "Main Room Type": main_room_type,
            "Sub Rooms": sub_rooms
        })
except:
    rooms = []

data["Rooms"] = rooms

#data in json
all_hotels_data.append(data)
json_filename = "trip_room_data.json"
with open(json_filename, "w", encoding="utf-8") as f:
    json.dump(all_hotels_data, f, ensure_ascii=False, indent=4)

print(f"✅ Scraped data saved to: {json_filename}")