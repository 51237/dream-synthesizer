import streamlit as st

st.set_page_config(page_title="Synthétiseur de Rêves", page_icon="🌙")

st.title("🌙 Synthétiseur de Rêves")
st.markdown("Décris ton rêve ci-dessous, et une image sera générée à partir de celui-ci.")

# Zone de texte
dream = st.text_area("Ton rêve", placeholder="Exemple : Je marchais dans une forêt remplie d'horloges suspendues...")

# Bouton pour générer
if st.button("Générer l'image"):
    st.info("Fonctionnalité à venir : ici, l'image sera générée à partir du rêve.")