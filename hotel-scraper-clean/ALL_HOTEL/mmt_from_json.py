import re
import json
import pandas as pd
import subprocess, sys

def install_package(package):
    try:
        __import__(package)
    except ImportError:
        print(f"Installing required package: {package}")
        subprocess.check_call([sys.executable, "-m", "pip", "install", package])

install_package("openpyxl")

def extract_mmt_prices(input_file="mmt_firecrawl_output.json",
                       excel_output="mmt_hotel_prices.xlsx",
                       json_output="mmt_firecrawl_output.json"):
    with open(input_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    markdown_content = data.get("markdown", "")
    extracted_data = []

    # ✅ Detect currency
    is_usd = "$" in markdown_content and "₹" not in markdown_content
    exchange_rate = 78 if is_usd else 1
    currency_symbol = "USD" if is_usd else "INR"

    print(f"✅ Detected currency: {currency_symbol}")

    # ✅ Regex patterns
    price_pattern = re.compile(r'[$₹]\s*([\d,]+)\s*(?:\n)?\s*\+?\s*[$₹]?\s*([\d,]+)\s*tax', re.IGNORECASE)

    room_sections = re.split(r'\n##\s+', '## ' + markdown_content)

    for section in room_sections:
        if not section.strip():
            continue

        room_type = section.split('\n')[0].strip()
        plan_sections = re.split(r'#####\s+', section)

        for plan_section in plan_sections[1:]:
            plan_name = plan_section.split('\n', 1)[0].strip()

            match = price_pattern.search(plan_section)
            if match:
                price = int(match.group(1).replace(",", "")) * exchange_rate
                taxes = int(match.group(2).replace(",", "")) * exchange_rate
                total = price + taxes

                extracted_data.append({
                    "Room Type": room_type,
                    "Plan": plan_name,
                    "Price (INR)": price,
                    "Taxes (INR)": taxes,
                    "Total Price (INR)": total
                })

    if not extracted_data:
        print("⚠️ No data extracted.")
        return

    df = pd.DataFrame(extracted_data)
    print(df.to_string())
    df.to_excel(excel_output, index=False)
    print(f"✅ Data saved to '{excel_output}'")

    # ✅ Goibibo-style JSON
    hotel_name_match = re.search(r"#\s*(.*?)\n", markdown_content)
    rating_match = re.search(r"(\d\.\d)\s*(?:Very Good|Excellent|Average)", markdown_content)

    hotel_name = hotel_name_match.group(1).strip() if hotel_name_match else "Unknown Hotel"
    rating = float(rating_match.group(1)) if rating_match else None
    rooms_available = len(set([d["Room Type"] for d in extracted_data]))

    room_options = [{
        "room_type": d["Room Type"],
        "plan": d["Plan"],
        "price_per_night": d["Price (INR)"],
        "taxes_and_fees": d["Taxes (INR)"],
        "total_price": d["Total Price (INR)"],
        "extras": "",
        "amenities": []
    } for d in extracted_data]

    final_json = {
        "hotel_name": hotel_name,
        "rating": rating,
        "rooms_available": rooms_available,
        "room_options": room_options
    }

    with open(json_output, "w", encoding="utf-8") as f:
        json.dump(final_json, f, ensure_ascii=False, indent=4)

    print(f"✅ JSON saved to '{json_output}' (overwriting for FastAPI)")

if __name__ == "__main__":
    extract_mmt_prices()
