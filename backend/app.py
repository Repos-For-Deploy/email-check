from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from flask_mysqldb import MySQL
from functools import wraps
from werkzeug.security import check_password_hash
from datetime import datetime
from imapclient import IMAPClient
from email import policy
from email.parser import BytesParser
from dotenv import load_dotenv
import imaplib 
import os, jwt

# Load .env
load_dotenv()

import config

app = Flask(__name__, static_folder="../frontend/build", static_url_path="/")
CORS(app)

# MySQL configuration
app.config['MYSQL_HOST'] = config.MYSQL_HOST
app.config['MYSQL_USER'] = config.MYSQL_USER
app.config['MYSQL_PASSWORD'] = config.MYSQL_PASSWORD
app.config['MYSQL_DB'] = config.MYSQL_DB

mysql = MySQL()
mysql.init_app(app)



@app.route("/")
def serve():
    return send_from_directory(app.static_folder, "index.html")


def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            return jsonify({'error': 'Token is missing'}), 401

        try:
            data = jwt.decode(token,  os.getenv("SECRET_KEY"), algorithms=["HS256"])
            user_id = data['user_id']
        except:
            return jsonify({'error': 'Invalid token'}), 401

        cur = mysql.connection.cursor()
        cur.execute("SELECT session_token FROM users WHERE id=%s", (user_id,))
        user = cur.fetchone()
        cur.close()

        if not user or user[0] != token:
            return jsonify({'error': 'Session expired (another login detected)'}), 403

        return f(*args, **kwargs)
    return decorated


@app.route('/api/emails', methods=['GET'])
@token_required
def get_emails():

    cur = mysql.connection.cursor()
    cur.execute("SELECT id,email FROM check_email_address ORDER BY id ASC LIMIT 10")
    address_info = cur.fetchall()
    result = []
    for acc in address_info:
        result.append({"id": acc[0], "email": acc[1]})
        
    return jsonify({"status": "OK", "results": result})


@app.route('/api/check', methods=['POST'])
@token_required
def check_email():


    data = request.json
    from_name_or_email = data.get("search")
    account_email = data.get("email")

    cur = mysql.connection.cursor()
    cur.execute("SELECT password FROM check_email_address WHERE email = %s", (account_email,))
    account_email_info = cur.fetchone()
    cur.close()

    # for acc in address_info:
    # Check email status for each account
    status_list = check_email_status(account_email, account_email_info[0], from_name_or_email)

    return jsonify({"status": "OK", "results": status_list})



def token_compare(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.headers.get('Authorization', None)
        if not token:
            # let assume that only one user is on the user table
            cur = mysql.connection.cursor()
            cur.execute("SELECT session_token FROM users LIMIT 1")
            user = cur.fetchone()
            cur.close()
            if not user:
                return jsonify({'error': 'No user found'}), 401
            elif user[0] != None and user[0] != '':
                return jsonify({'error': 'Session expired (another login detected)'}), 403
            else:
                # If token is empty, we assume the user is not logged in
                return f(*args, **kwargs)
        else:
            try:
                data = jwt.decode(token,  os.getenv("SECRET_KEY"), algorithms=["HS256"])
                user_id = data['user_id']
            except:
                return jsonify({'error': 'Invalid token'}), 401

            cur = mysql.connection.cursor()
            cur.execute("SELECT session_token FROM users WHERE id=%s", (user_id,))
            user = cur.fetchone()
            cur.close()

            if not user or user[0] != token:
                return jsonify({'error': 'Session expired (another login detected)'}), 403

            return f(*args, **kwargs)
    return decorated

@app.route('/api/login', methods=['POST'])
@token_compare
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password_hash FROM users WHERE username=%s", (username,))
    user = cur.fetchone()

    if not user:
        return jsonify({"error": "Unregister"}), 401  # 401 Unauthorized is more appropriate

    user_id, password_hash = user

    if not check_password_hash(password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401

    token = jwt.encode({"user_id": user_id}, os.getenv("SECRET_KEY"), algorithm="HS256")

    cur.execute("UPDATE users SET session_token=%s WHERE id=%s", (token, user_id))
    mysql.connection.commit()

    return jsonify({"token": token})

@app.route("/api/logout", methods=["POST"])
@token_required
def logout():
    token = request.headers.get("Authorization")

    if not token:
        return jsonify({"error": "Missing token"}), 401

    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET session_token = NULL WHERE session_token = %s", (token,))
    mysql.connection.commit()
    cur.close()

    return jsonify({"status": "OK", "message": "Logout success"}), 200

def check_email_status(gmail_email, app_password, from_email_or_name):
    result = {"inbox": False, "spam": False, "not_found": True, "diff_time": ""}
    
    # List of folders to search
    folders = ["INBOX", "[Gmail]/Spam"]

    def short_date(date):
        
        try:
            if date is None:
                return ""
            now = datetime.now()
            diff = now - date
            if diff.total_seconds() < 60:
                return "Just now"
            elif diff.total_seconds() < 3600:
                return f"{int(diff.total_seconds() // 60)} minutes ago"
            elif diff.total_seconds() < 86400:
                return f"{int(diff.total_seconds() // 3600)} hours ago"
            else:
                return f"{diff.days} days ago"
        except Exception as e:
            return "Unknown"
        
    def find_email():
        try:
            
            def fetch_emails(client, folder, search_text, limit):
                client.select_folder(folder)
                criteria = ['ALL'] if not search_text else ['FROM', search_text]
                uids = client.search(criteria)
                uids = uids[-limit:]  # take last `limit` emails
                messages = client.fetch(uids, ['ENVELOPE', 'X-GM-LABELS'])
                results = []
                for uid, data in messages.items():
                    envelope = data[b'ENVELOPE']
                    subject = envelope.subject.decode() if envelope.subject else "(No subject)"
                    sender = f"{envelope.from_[0].mailbox.decode()}@{envelope.from_[0].host.decode()}"
                    sender_name = envelope.from_[0].name.decode() if envelope.from_[0].name else "(No name)"

                    labels = [l.decode() for l in data.get(b'X-GM-LABELS', [])]
        
                    # Fetch full raw email for body parsing
                    raw_data = client.fetch([uid], ['RFC822'])[uid][b'RFC822']
                    msg = BytesParser(policy=policy.default).parsebytes(raw_data)
                    
                    # Extract plain text and html bodies
                    text_body = None
                    html_body = None
                    if msg.is_multipart():
                        for part in msg.walk():
                            ct = part.get_content_type()
                            if ct == "text/plain" and text_body is None:
                                text_body = part.get_content()
                            elif ct == "text/html" and html_body is None:
                                html_body = part.get_content()
                    else:
                        if msg.get_content_type() == "text/plain":
                            text_body = msg.get_content()
                        elif msg.get_content_type() == "text/html":
                            html_body = msg.get_content()
                    results.append({
                        "folder": folder,
                        "date": envelope.date,
                        "sender": sender,
                        "sender_name": sender_name,
                        "subject": subject,
                        "labels": [l.decode() for l in data.get(b'X-GM-LABELS', [])],
                        "text_body": text_body,
                        "html_body": html_body
                    })
                return results
                        
            with IMAPClient('imap.gmail.com', port=993, ssl=True) as client:
                client.login(gmail_email, app_password)
                
                inbox_emails = fetch_emails(client, "INBOX", from_email_or_name, 10)
                spam_emails = fetch_emails(client, "[Gmail]/Spam", from_email_or_name, 10)
                
                all_emails = inbox_emails + spam_emails
                # Sort combined by date (newest first)
                all_emails.sort(key=lambda x: x['date'], reverse=True)

                return [{"folder": "INBOX", "emails": inbox_emails}, {"folder": "SPAM", "emails": spam_emails}]



            

        except imaplib.IMAP4.error as e:
            print(f"IMAP error occurred while accessing folder : {e}")
            return False
        except Exception as e:
            print(f"Unexpected error while accessing folder : {e}")
            return False

    # Loop through each folder
    results = []
    # Check each folder for the email
    # results = [{"inbox": 0, "spam": 0, "not_found": 0, "diff_time": "", "text": "", "sender": ""}]
    inbox_count = 0
    spam_count = 0  


        
    received_list = find_email()  # Pass the folder variable here


    if received_list == False:
        return {'results':[], 'inbox': 0, 'spam': 0, 'not_found': 1, 'type': 'invalid'}

    for received in received_list:
        email_count = 0
        for email in received['emails']:
            email_count += 1
            result = {}
            result["type"] = "inbox" if received['folder'] == "INBOX" else "spam"
            result["diff_time"] = short_date(email['date'])
            result["date"] = email['date']
            result["text"] = email['text_body']
            result["subject"] = email['subject']
            result["sender_email"] = email['sender']
            result["sender_name"] = email['sender_name']
            results.append(result)
        # Count emails in each folder
        inbox_count += email_count if received['folder'] == "INBOX" else 0
        spam_count += email_count if received['folder'] == "SPAM" else 0

    return {'results': results, 'email': gmail_email, 'inbox': inbox_count, 'spam': spam_count, 'not_found': 0 if inbox_count + spam_count > 0 else 1, 'type': 'valid'}


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)