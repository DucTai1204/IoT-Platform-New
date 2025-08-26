import smtplib
from email.mime.text import MIMEText
import json

with open("config.json") as f:
    config = json.load(f)

EMAIL_CONFIG = config["email"]

def send_email_alert(message: str):
    msg = MIMEText(message, _charset="utf-8")
    msg["Subject"] = "[CẢNH BÁO] Nền tảng IoT BDU"
    msg["From"] = EMAIL_CONFIG["sender"]
    msg["To"] = EMAIL_CONFIG["receiver"]

    try:
        server = smtplib.SMTP_SSL(EMAIL_CONFIG["server"], EMAIL_CONFIG["port"])
        server.login(EMAIL_CONFIG["sender"], EMAIL_CONFIG["password"])
        server.sendmail(EMAIL_CONFIG["sender"], [EMAIL_CONFIG["receiver"]], msg.as_string())
        server.quit()
        print("📧 Email đã gửi thành công.")
    except Exception as e:
        print(f"❌ Lỗi gửi email: {e}")
