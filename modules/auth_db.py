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
