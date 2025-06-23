from dotenv import load_dotenv
import streamlit as st
import json
import os
import openai
from modules.ai_tools import speech_to_text, text_analysis, normalize_emotions
from modules.ui import record_voice, show_emotion_pie_chart
from modules.auth_db import (
    init_db, login_user, register_user, logout_user,
    get_current_user, save_dream, get_user_dreams,
    send_friend_request, get_friend_requests,
    respond_to_friend_request, get_friends_list,
    get_messages, send_message
)

load_dotenv()
init_db()

st.set_page_config(page_title="Synthétiseur de Rêves", page_icon="🌙")

if "auth_page" not in st.session_state:
    st.session_state.auth_page = "Connexion"
if "page" not in st.session_state:
    st.session_state.page = "main"

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
                st.session_state.page = "main"
                st.rerun()
            else:
                st.error(message)

    else:
        new_user = st.text_input("Nom d'utilisateur", key="new_user", autocomplete="off")
        new_pass = st.text_input("Mot de passe", type="password", key="new_pass", autocomplete="off")
        if st.button("Créer un compte"):
            if new_user and new_pass:
                success, message = register_user(new_user, new_pass)
                if success:
                    st.success(message)
                    st.info("🔭 Redirection vers Connexion...")
                    st.session_state.auth_page = "Connexion"
                    st.rerun()
                else:
                    st.error(message)
            else:
                st.warning("Veuillez remplir tous les champs.")
    st.stop()

st.sidebar.markdown(f"👋 Connecté en tant que **{get_current_user()}**")
if st.sidebar.button("🔓 Se déconnecter"):
    logout_user()
    st.success("Déconnecté.")
    st.rerun()
if st.sidebar.button("🗂️ Mes rêves"):
    st.session_state.page = "gallery"
    st.rerun()
if st.sidebar.button("👥 Amis"):
    st.session_state.page = "friends"
    st.rerun()
if st.sidebar.button("💬 Messagerie"):
    st.session_state.page = "messaging"
    st.rerun()

if "dream" not in st.session_state:
    st.session_state.dream = ""

if st.session_state.page == "gallery":
    st.title("🌌 Galerie de mes rêves")
    dreams = get_user_dreams(get_current_user())
    if not dreams:
        st.info("Aucun rêve enregistré pour le moment.")
    else:
        for texte, url, date in dreams:
            st.image(url, width=300, caption=f"🕰️ {date}")
            st.markdown(f"**📝 Description :** {texte}")
            st.markdown("---")
    if st.button("Retour à l'acceuil"):
        st.session_state.page = "main"
        st.rerun()
    st.stop()

if st.session_state.page == "friends":
    st.title("👥 Gestion des amis")
    current_user = get_current_user()

    st.subheader("💎 Envoyer une demande d'ami")
    target_user = st.text_input("Nom de l'utilisateur à ajouter")
    if st.button("✉️ Envoyer la demande"):
        if target_user and target_user != current_user:
            success, message = send_friend_request(current_user, target_user)
            if not success:
                st.error(message)
        else:
            st.warning("Nom invalide.")

    st.subheader("📥 Demandes reçues")
    requests = get_friend_requests(current_user)
    for sender in requests:
        col1, col2 = st.columns([3, 1])
        with col1:
            st.markdown(f"**{sender}** souhaite devenir ton ami.")
        with col2:
            if st.button(f"✅ Accepter {sender}"):
                respond_to_friend_request(current_user, sender, "accepted")
                st.rerun()
            if st.button(f"❌ Refuser {sender}"):
                respond_to_friend_request(current_user, sender, "rejected")
                st.rerun()

    st.subheader("👨‍👨‍👦 Tes amis")
    friends = get_friends_list(current_user)
    if not friends:
        st.info("Tu n'as pas encore d'amis acceptés.")
    else:
        for f in friends:
            st.markdown(f"- {f}")

    if st.button("Retour à l'acceuil"):
        st.session_state.page = "main"
        st.rerun()
    st.stop()

if st.session_state.page == "messaging":
    st.title("💬 Messagerie")
    current_user = get_current_user()
    friends = get_friends_list(current_user)

    if not friends:
        st.info("Ajoute des amis pour commencer à discuter.")
        st.stop()

    selected_friend = st.selectbox("Choisis un ami pour discuter :", friends)
    messages = get_messages(current_user, selected_friend)

    for sender, texte, image_url, timestamp in messages:
        st.markdown(f"**{sender}** ({timestamp})")
        if texte:
            st.markdown(f"> {texte}")
        if image_url:
            st.image(image_url, width=300)
        st.markdown("---")

    st.subheader("📝 Message écrit (optionnel)")
    texte = st.text_area("Rédige un message à envoyer (tu peux l’envoyer seul ou avec un rêve)")

    st.subheader("🌠 Partager un rêve (optionnel)")
    user_dreams = get_user_dreams(current_user)

    dream_options = ["Aucun rêve sélectionné"] + [f"{i+1}. {desc[:40]}..." for i, (desc, url, _) in enumerate(user_dreams)]
    selected_index = st.selectbox("Choisis un rêve à partager :", range(len(dream_options)), format_func=lambda i: dream_options[i])

    if st.button("📤 Envoyer"):
        selected_image_url = None
        selected_texte = texte if texte.strip() else ""

        if selected_index != 0:
            selected_texte, selected_image_url, _ = user_dreams[selected_index - 1]

        if not selected_texte and not selected_image_url:
            st.warning("Aucun contenu à envoyer.")
        else:
            send_message(current_user, selected_friend, selected_texte, selected_image_url)
            st.success("Message envoyé !")
            st.rerun()

    if st.button("Retour à l'acceuil"):
        st.session_state.page = "main"
        st.rerun()

    st.stop()

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

                from modules.ai_tools import generate_dream_image
                image_url = generate_dream_image(st.session_state.dream)
                if image_url:
                    st.image(image_url, caption="🔮 Image générée à partir du rêve", use_container_width=True)
                    save_dream(get_current_user(), st.session_state.dream, image_url)
                else:
                    st.warning("Image non générée.")
            except Exception as e:
                st.error(f"❌ Erreur pendant l'analyse ou la génération d'image : {e}")
    else:
        st.warning("Veuillez enregistrer un rêve avant d’analyser.")
