# app/views.py
from flask import Flask, Blueprint, request, jsonify, send_from_directory
from app.imap_checker import check_email_status
from flask_jwt_extended import jwt_required, get_jwt_identity
from functools import wraps
from app import mysql
import os

main = Blueprint('main', __name__)

def validate_token(user_id, token_header):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, session_token FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    aaa = user[1]
    return user and aaa == token_header

@main.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    user_id = get_jwt_identity()
    cur = mysql.connection.cursor()
    cur.execute("UPDATE users SET session_token = NULL WHERE id = %s", (user_id,))
    mysql.connection.commit()
    return jsonify({"status": "OK"})

@main.route('/api/check', methods=['POST'])
@jwt_required() 
def check_email():
    user_id = get_jwt_identity()
    token_header = request.headers.get('Authorization').split(" ")[1]

    if not validate_token(user_id, token_header):
        return jsonify(msg='Session expired or device mismatch'), 401
    
    data = request.json
    from_name_or_email = data.get("search")

    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM check_email_address ORDER BY id ASC LIMIT 10")
    address_info = cur.fetchall()
    
    results = []
    inbox_num = spam_num = nofind_num = 0

    for acc in address_info:
        account = acc[1].replace('\r', '').replace('\n', '')
        password = acc[2].replace('\r', '').replace('\n', '')
        statuses = check_email_status(account, password, from_name_or_email.replace('\r', '').replace('\n', ''))  # returns list of status dicts
#        statuses = check_email_status(acc[1], acc[2], from_name_or_email)  # returns list of status dicts
        result_item = {"emails": []}
        for status in statuses:
            result_item["emails"].append({**status, "state": True})
            if status.get("status") == "Inbox":
                inbox_num += 1
            if status.get("status") == "Spam":
                spam_num += 1
            if status.get("status") == "NoFind":
                nofind_num += 1
                result_item["emails"].append({**status, "state": False, "message": "No email"})
                continue            
        results.append(result_item)
        # # Store to DB
        # cur = mysql.connection.cursor()
        # stat = 'inbox' if status["inbox"] else 'spam' if status["spam"] else 'not_found'
        # cur.execute("INSERT INTO emails (test_email, status) VALUES (%s, %s)", (acc["email"], stat))
        # mysql.connection.commit()
    total = inbox_num + spam_num + nofind_num
    if total > 0:
        p_inbox = int((inbox_num / total) * 100)
        p_spam = int((spam_num / total) * 100)
        p_nofind = int((nofind_num / total) * 100)
    else:
        p_inbox = p_spam = p_nofind = 0
    return jsonify({"status": "OK", "results": results, "inbox": p_inbox, "spam": p_spam, "nofind": p_nofind})

# Protected Route Example
@main.route("/api/profile", methods=["GET"])
def profile():
    token = request.headers.get("Authorization")
    if not token:
        return jsonify({"error": "Missing token"}), 401

    cur = mysql.connection.cursor()
    cur.execute("SELECT id, username FROM users WHERE session_token = %s", (token,))
    user = cur.fetchone()
    cur.close()

    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    return jsonify({"id": user["id"], "username": user["username"]})
