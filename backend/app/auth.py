from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from app import mysql
from passlib.hash import bcrypt
from flask_jwt_extended import create_access_token
import jwt, os

auth = Blueprint('auth', __name__)

@auth.route('/api/create', methods=['POST'])
def create_user():
    data = request.json
    username = data.get("username")
    password = data.get("password")    

    hashed_password = generate_password_hash(password)
    try:
        cur = mysql.connection.cursor()
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, hashed_password)
        )
        mysql.connection.commit()
        cur.close()
        return jsonify({"message": "ok"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def validate_token(user_id, token_header):
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, session_token FROM users WHERE id=%s", (user_id,))
    user = cur.fetchone()
    return user and user.session_token == token_header

@auth.route('/api/login', methods=['POST'])
def login():
    data = request.json
    username = data.get("username")
    password = data.get("password")

    ip = request.remote_addr
    user_agent = request.headers.get('User-Agent')
    device_id = "abc-123"#request.headers.get('X-Device-ID')
    cur = mysql.connection.cursor()
    cur.execute("SELECT id, password_hash, session_token FROM users WHERE username=%s", (username,))
    user = cur.fetchone()

    cur.execute("SELECT email FROM check_email_address ORDER BY id")
    emails = cur.fetchall()

    if not user:
        return jsonify({"error": "Unregistered"}), 401  # 401 Unauthorized is more appropriate

    user_id, password_hash, session_token = user

    if not check_password_hash(password_hash, password):
        return jsonify({"error": "Invalid credentials"}), 401
    auth_header = request.headers.get("Authorization", "")
    incoming_token = auth_header.replace("Bearer ", "").strip()

    if session_token and session_token != incoming_token:
        return jsonify({"error": "User already logged in on another device"}), 401

    token =  create_access_token(
                                        identity=str(user_id),
                                        additional_claims={"ip": ip, "user_agent": user_agent, "device_id": device_id}
    )
    
    cur.execute("UPDATE users SET session_token=%s WHERE id=%s", (token, user_id))
    mysql.connection.commit()

    return jsonify({"token": token, "device_id": device_id, "emails": emails})
    # add user and password
    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    cur = mysql.connection.cursor()

    # Check if user already exists
    cur.execute("SELECT id FROM users WHERE username=%s", (username,))
    if cur.fetchone():
        return jsonify({"error": "Username already taken"}), 409  # Conflict

    password_hash = generate_password_hash(password)
    cur.execute("INSERT INTO users (username, password_hash) VALUES (%s, %s)", (username, password_hash))
    mysql.connection.commit()
