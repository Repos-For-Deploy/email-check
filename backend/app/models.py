# app/models.py
from app import mysql

# For raw SQL execution using cursor
def create_tables():
    cur = mysql.connection.cursor()

    # USERS table (Admins only, no registration)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(50) NOT NULL UNIQUE,
        password_hash TEXT NOT NULL,
        session_token TEXT,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS check_email_address (
        id INT AUTO_INCREMENT PRIMARY KEY,
        email VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP
    );
    """)

    # GMAIL_LOG table (connected test inboxes via app password)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS emaillog (
        id INT AUTO_INCREMENT PRIMARY KEY,
        user_id INT NOT NULL,
        test_email VARCHAR(255) NOT NULL,
        app_password TEXT NOT NULL,
        is_active BOOLEAN DEFAULT TRUE,
        created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
    );
    """)

    # EMAIL_CHECK_LOG table (for inbox/spam/not_found results)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS email_check_log (
        id INT AUTO_INCREMENT PRIMARY KEY,
        gmail_account_id INT NOT NULL,
        sender_email VARCHAR(255) NOT NULL,
        subject TEXT,
        folder ENUM('inbox', 'spam', 'not_found') NOT NULL,
        checked_at DATETIME DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (gmail_account_id) REFERENCES emaillog(id) ON DELETE CASCADE
    );
    """) 
    mysql.connection.commit()
    cur.close()
