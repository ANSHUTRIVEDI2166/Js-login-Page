import json
import pandas as pd
from io import BytesIO
import os
import smtplib
from email.message import EmailMessage

def safe_get(obj, path, fallback=[]):
    try:
        for p in path:
            obj = obj[p]
        return obj
    except:
        return fallback

def send_email_with_excel(excel_path):
    msg = EmailMessage()
    msg["Subject"] = "Hotel Room Data Excel"
    msg["From"] = "anshutrivedi2166@gmail.com"
    msg["To"] = "23aiml072@charusat.edu.in"
    msg.set_content("Attached is the hotel room data.")

    with open(excel_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application",
                           subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           filename=os.path.basename(excel_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("tithi.radia@gmail.com", "xyxt epsl pysx yktt")  # Use app password
        smtp.send_message(msg)

def main():
    with open("merged_output.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    output = BytesIO()
    writer = pd.ExcelWriter(output, engine='xlsxwriter')

    agoda = safe_get(data, ["agoda_room_data"])
    agoda_rows = [
        [h["Hotel Name"], r["title"], s["description"], s["price"]]
        for h in agoda
        for r in h.get("Rooms", [])
        for s in r.get("sub_rooms", [])
    ]
    pd.DataFrame(agoda_rows, columns=["Hotel", "Room Title", "Description", "Price"]) \
      .to_excel(writer, sheet_name="Agoda", index=False)

    writer.close()
    output.seek(0)

    excel_path = "Hotel_Room_Data.xlsx"
    with open(excel_path, "wb") as f:
        f.write(output.read())

def send_email_with_excel(excel_path, recipient_email):
    msg = EmailMessage()
    msg["Subject"] = "Hotel Room Data Excel"
    msg["From"] = "anshutrivedi2166@gmail.com"
    msg["To"] = recipient_email
    msg.set_content("Attached is the hotel room data.")

    with open(excel_path, "rb") as f:
        msg.add_attachment(f.read(), maintype="application",
                           subtype="vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                           filename=os.path.basename(excel_path))

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login("anshutrivedi2166@gmail.com", "nzoi cawy gwji dqxv")
        smtp.send_message(msg)
