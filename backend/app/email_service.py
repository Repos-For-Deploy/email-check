import smtplib
import imaplib
import email
import json
import random
import time
from email.mime.text import MIMEText
from email.header import decode_header

# Load sender Gmail app accounts
def load_accounts():
    with open("credentials/email_accounts.json") as f:
        return json.load(f)

# Send email
def send_test_email(to_email, subject, content):
    accounts = load_accounts()
    sender = random.choice(accounts)

    msg = MIMEText(content)
    msg["Subject"] = subject
    msg["From"] = sender["email"]
    msg["To"] = to_email

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(sender["email"], sender["app_password"])
        server.sendmail(sender["email"], to_email, msg.as_string())

    return sender["email"]  # Return the sender for reference

# Check IMAP (assuming target_email supports IMAP)
def check_delivery_status(target_email, email_password, subject, timeout=10):
    imap_host = "imap.gmail.com"
    status = "Not Found"

    try:
        with imaplib.IMAP4_SSL(imap_host) as mail:
            mail.login(target_email, email_password)

            for folder in ["INBOX", "[Gmail]/Spam"]:
                mail.select(folder)
                typ, data = mail.search(None, f'SUBJECT "{subject}"')
                if data[0]:
                    return "Inbox" if folder == "INBOX" else "Spam"

    except Exception as e:
        print("IMAP error:", e)

    return status
