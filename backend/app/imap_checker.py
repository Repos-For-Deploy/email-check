from imap_tools import MailBox, AND
import imaplib  # for specific IMAP errors
from datetime import datetime, timezone

def check_email_status(gmail_email, app_password, from_email_or_name):
    result = {"inbox": False, "spam": False, "not_found": True, "diff_time": ""}
    
    # List of folders to search
    folders = ["INBOX", "[Gmail]/Spam"]
    def find_msg(folder):        
        msges = []
        try:
            with MailBox('imap.gmail.com').login(gmail_email, app_password, initial_folder=folder) as box:
                criteria = AND(from_=from_email_or_name)
                for msg in box.fetch(criteria, limit=20):
                    msges.append(msg)
            return msges
        except imaplib.IMAP4.error as e:
            print(f"IMAP error occurred while accessing folder {folder}: {e}")
            return []
        except Exception as e:
            print(f"Unexpected error while accessing folder {folder}: {e}")
            return []

    # Loop through each folder
    results = []
    for folder in folders:
        msges = find_msg(folder)  # Get messages from this folder (return value, not global)
        for msg in msges:
            result = {}  # Create a new result dictionary for each message
            
            # Check folder status
            if folder == "INBOX":
                result["status"] = "Inbox"
            elif folder == "[Gmail]/Spam" or folder == "Spam" or folder == "Junk":
                result["status"] = "Spam"
            else:
                result["status"] = "NoFind"
                continue  # Skip processing if folder isn't Inbox or Spam

            try:
                send_time = msg.date  # Assume this is timezone-aware
                now = datetime.now(timezone.utc)
                diff_time = now - send_time

                result["name"] = msg.from_values.name
                # ⏱ Format time difference
                if diff_time.total_seconds() < 60:
                    result["diff_time"] = "Just now"
                elif diff_time.total_seconds() < 3600:
                    result["diff_time"] = f"{int(diff_time.total_seconds() // 60)} minutes ago"
                elif diff_time.total_seconds() < 86400:
                    result["diff_time"] = f"{int(diff_time.total_seconds() // 3600)} hours ago"
                else:
                    result["diff_time"] = f"{diff_time.days} days ago"

                # Truncate message text
                text_cut = msg.text[:30] + "..."
                result["text"] = text_cut
                result["account"] = msg.from_

            except Exception as e:
                result["diff_time"] = ""
                result["text"] = ""
            
            results.append(result)  # Append after processing

    return results