import sqlite3
import hashlib
import streamlit as st

DB_FILE = "users.db"

def get_connection():
    return sqlite3.connect(DB_FILE)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            username TEXT PRIMARY KEY,
            password TEXT NOT NULL
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS dreams (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user TEXT,
            texte_reve TEXT,
            image_url TEXT,
            date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS friends (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            from_user TEXT NOT NULL,
            to_user TEXT NOT NULL,
            status TEXT CHECK(status IN ('pending', 'accepted', 'rejected')) NOT NULL,
            UNIQUE(from_user, to_user)
        )
    """)

    conn.commit()
    conn.close()


def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def register_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)",
                       (username, hash_password(password)))
        conn.commit()
        return True, "Inscription réussie"
    except sqlite3.IntegrityError:
        return False, "Nom d'utilisateur déjà pris"
    finally:
        conn.close()

def login_user(username, password):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT password FROM users WHERE username = ?", (username,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0] == hash_password(password):
        st.session_state.user = username
        return True, "Connexion réussie"
    elif not row:
        return False, "Utilisateur introuvable"
    else:
        return False, "Mot de passe incorrect"

def logout_user():
    st.session_state.pop("user", None)

def get_current_user():
    return st.session_state.get("user", None)


def save_dream(username, texte, image_url):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO dreams (user, texte_reve, image_url) VALUES (?, ?, ?)",
                   (username, texte, image_url))
    conn.commit()
    conn.close()

def get_user_dreams(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT texte_reve, image_url, date_creation 
        FROM dreams 
        WHERE user = ? 
        ORDER BY date_creation DESC
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return rows


def send_friend_request(from_user, to_user):
    if from_user == to_user:
        return False, "Tu ne peux pas t’ajouter toi-même."

    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute("SELECT username FROM users WHERE username = ?", (to_user,))
    if not cursor.fetchone():
        conn.close()
        return False, "L'utilisateur n'existe pas."

    cursor.execute("""
        SELECT * FROM friends 
        WHERE (from_user=? AND to_user=?) 
           OR (from_user=? AND to_user=?)
    """, (from_user, to_user, to_user, from_user))
    if cursor.fetchone():
        conn.close()
        return False, "Déjà en attente ou déjà amis."

    cursor.execute("""
        INSERT INTO friends (from_user, to_user, status) 
        VALUES (?, ?, 'pending')
    """, (from_user, to_user))
    conn.commit()
    conn.close()
    return True, "Demande envoyée avec succès."

def get_friend_requests(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT from_user 
        FROM friends 
        WHERE to_user=? AND status='pending'
    """, (username,))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def respond_to_friend_request(current_user, from_user, response):
    conn = get_connection()
    cursor = conn.cursor()
    if response == "accepted":
        cursor.execute("""
            UPDATE friends 
            SET status='accepted' 
            WHERE from_user=? AND to_user=?
        """, (from_user, current_user))
    elif response == "rejected":
        cursor.execute("""
            DELETE FROM friends 
            WHERE from_user=? AND to_user=?
        """, (from_user, current_user))
    conn.commit()
    conn.close()

def get_friends_list(username):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT 
            CASE 
                WHEN from_user = ? THEN to_user 
                ELSE from_user 
            END 
        FROM friends 
        WHERE (from_user = ? OR to_user = ?) AND status = 'accepted'
    """, (username, username, username))
    rows = cursor.fetchall()
    conn.close()
    return [row[0] for row in rows]

def send_message(sender, receiver, texte=None, image_url=None):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (sender, receiver, texte, image_url)
        VALUES (?, ?, ?, ?)
    """, (sender, receiver, texte, image_url))
    conn.commit()
    conn.close()

def get_messages(user1, user2):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("""
        SELECT sender, texte, image_url, timestamp
        FROM messages
        WHERE (sender=? AND receiver=?) OR (sender=? AND receiver=?)
        ORDER BY timestamp ASC
    """, (user1, user2, user2, user1))
    rows = cursor.fetchall()
    conn.close()
    return rows
