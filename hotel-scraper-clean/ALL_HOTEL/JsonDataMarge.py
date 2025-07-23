import json
import os

# Folder where your JSON files are located
folder_path = "C:\\Users\\tithi\\Desktop\\Tithi\\4th Semester\\Internship\\Web Scrap\\ALL_HOTEL-20250527T062616Z-1-001\\ALL_HOTEL"  # Replace with your actual folder path
merged_data = {}

# Loop through all JSON files in the folder
for filename in os.listdir(folder_path):
    if filename.endswith(".json"):
        file_path = os.path.join(folder_path, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                data = json.load(f)
                # Use filename (without .json) as key
                key_name = os.path.splitext(filename)[0]
                merged_data[key_name] = data
            except json.JSONDecodeError as e:
                print(f"❌ Error reading {filename}: {e}")

# Write merged data to one JSON file
output_path = os.path.join(folder_path, "merged_output.json")
with open(output_path, "w", encoding="utf-8") as out_file:
    json.dump(merged_data, out_file, indent=4, ensure_ascii=False)

print(f"✅ Merged file saved to: {output_path}")
