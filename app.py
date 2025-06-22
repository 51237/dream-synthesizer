from dotenv import load_dotenv
import streamlit as st
import json
from modules.ai_tools import speech_to_text, text_analysis, normalize_emotions
from modules.ui import record_voice, show_emotion_pie_chart
from modules.auth_db import init_db, login_user, register_user, logout_user, get_current_user

load_dotenv()
init_db()

st.set_page_config(page_title="Synthétiseur de Rêves", page_icon="🌙")

# Initialise la navigation si elle n’existe pas encore
if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Connexion"

# ⛔ Auth non faite → afficher auth_page
if get_current_user() is None:
    st.markdown("## 🔐 Connexion ou Inscription")

    st.session_state.auth_page = st.radio("Choisis une action", ["Connexion", "Créer un compte"], index=0 if st.session_state.auth_page == "Connexion" else 1)

    if st.session_state.auth_page == "Connexion":
        username = st.text_input("Nom d'utilisateur", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Se connecter"):
            success, message = login_user(username, password)
            if success:
                st.success(message)
                st.experimental_set_query_params()  # efface les params pour relancer l’app si besoin
                st.rerun()
            else:
                st.error(message)

    else:  # Créer un compte
        new_user = st.text_input("Nom d'utilisateur", key="new_user")
        new_pass = st.text_input("Mot de passe", type="password", key="new_pass")
        if st.button("Créer un compte"):
            if new_user and new_pass:
                success, message = register_user(new_user, new_pass)
                if success:
                    st.success(message)
                    st.info("🧭 Redirection vers Connexion...")
                    st.session_state.auth_page = "Connexion"  # 🔁 redirige vers Connexion
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Veuillez remplir tous les champs.")

    st.stop()

# ✅ Si connecté : interface principale
st.sidebar.markdown(f"👋 Connecté en tant que **{get_current_user()}**")
if st.sidebar.button("🔓 Se déconnecter"):
    logout_user()
    st.success("Déconnecté.")
    st.rerun()

# Interface principale
if "dream" not in st.session_state:
    st.session_state.dream = ""

st.title("🌙 Synthétiseur de Rêves")
st.markdown("🎤 Enregistre ton rêve, il sera ensuite transcrit et analysé émotionnellement.")

duration = st.slider("Durée de l'enregistrement vocal (en secondes)", 3, 15, 5)

if st.button("🎤 Enregistrer ma voix"):
    audio_path = record_voice(duration)
    try:
        transcribed_text = speech_to_text(audio_path)
        st.session_state.dream = transcribed_text
        st.text_area("Texte transcrit", transcribed_text, height=150, disabled=True)
    except Exception as e:
        st.error(f"❌ Erreur pendant la transcription : {e}")

if st.button("🔍 Analyser le rêve"):
    if st.session_state.dream.strip():
        with st.spinner("Analyse en cours..."):
            try:
                raw_analysis = text_analysis(st.session_state.dream)
                parsed = json.loads(raw_analysis)
                parsed["émotions"] = normalize_emotions(parsed)

                if parsed["émotions"]:
                    show_emotion_pie_chart(parsed["émotions"])
                else:
                    st.warning("Aucune émotion détectée.")
            except Exception as e:
                st.error(f"❌ Erreur pendant l'analyse : {e}")
    else:
        st.warning("Veuillez enregistrer un rêve avant d’analyser.")
