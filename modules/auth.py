import json
import os
import hashlib
import streamlit as st

USERS_FILE = "users.json"

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def load_users():
    if not os.path.exists(USERS_FILE):
        return {}
    with open(USERS_FILE, "r") as f:
        return json.load(f)

def save_users(users):
    with open(USERS_FILE, "w") as f:
        json.dump(users, f)

def register_user(username, password):
    users = load_users()
    if username in users:
        return False, "Utilisateur déjà existant"
    users[username] = hash_password(password)
    save_users(users)
    return True, "Inscription réussie"

def login_user(username, password):
    users = load_users()
    if username not in users:
        return False, "Utilisateur introuvable"
    if users[username] != hash_password(password):
        return False, "Mot de passe incorrect"
    st.session_state.user = username
    return True, "Connexion réussie"

def logout_user():
    if "user" in st.session_state:
        del st.session_state.user

def get_current_user():
    return st.session_state.get("user", None)
