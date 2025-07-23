import re
import json
import pandas as pd
import subprocess
import sys

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing required package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("openpyxl")

def extract_goibibo_prices(input_file="firecrawl_output.json", excel_output="goibibo_hotel_prices.xlsx", json_output="firecrawl_output.json"):
    try:
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        markdown_content = data.get("markdown", "")
    except FileNotFoundError:
        print(f"Error: The file '{input_file}' was not found in the current directory.")
        return
    except json.JSONDecodeError:
        print(f"Error: Could not decode JSON from '{input_file}'. The file may be corrupted.")
        return
    except Exception as e:
        print(f"An unexpected error occurred while reading the file: {e}")
        return

    extracted_data = []

    # Regex to find all room sections starting with '### '
    room_sections = re.split(r'\n###\s+', '### ' + markdown_content)

    # Regex for price and taxes.
    price_pattern = re.compile(r'([\d,]+)\s*\n\s*\\?\+\s*₹\s*([\d,]+)\s+taxes\s*&\s*fees')

    for section in room_sections:
        if not section.strip():
            continue

        lines = section.split('\n')
        room_type = lines[0].replace('### ', '').strip()
        plan_sections = re.split(r'####\s+', section)

        for plan_section in plan_sections[1:]:
            plan_name = plan_section.split('\n', 1)[0].strip()
            price_match = price_pattern.search(plan_section)
            if price_match:
                price = int(price_match.group(1).replace(',', ''))
                taxes = int(price_match.group(2).replace(',', ''))
                total_price = price + taxes
                extracted_data.append({
                    "Room Type": room_type,
                    "Plan": plan_name,
                    "Price (INR)": price,
                    "Taxes (INR)": taxes,
                    "Total Price (INR)": total_price
                })

    if not extracted_data:
        print("No data was extracted. Please check the file format and content.")
        return

    prices_df = pd.DataFrame(extracted_data)
    print("Successfully extracted data. Here is the correct preview:")
    print(prices_df.to_string())

    try:
        prices_df.to_excel(excel_output, index=False)
        print(f"\nData has been successfully saved to '{excel_output}'")
    except Exception as e:
        print(f"\nAn error occurred while saving the Excel file: {e}")

    # Save as JSON for backend merging
    room_options = [
        {
            "room_type": d["Room Type"],
            "plan": d["Plan"],
            "price_per_night": d["Price (INR)"],
            "taxes_and_fees": d["Taxes (INR)"],
            "total_price": d["Total Price (INR)"],
            "extras": "",
            "amenities": []
        } for d in extracted_data
    ]
    final_json = {
        "hotel_name": "Goibibo Hotel",  # You can improve this by extracting from markdown
        "rooms_available": len(room_options),
        "room_options": room_options
    }
    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)
    print(f"✅ JSON saved to '{json_output}' (overwriting for backend)")

if __name__ == "__main__":
    extract_goibibo_prices()
