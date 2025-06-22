import streamlit as st
import matplotlib.pyplot as plt
import sounddevice as sd
from scipy.io.wavfile import write
import tempfile

def record_voice(duration=5, fs=44100):
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmpfile:
        audio_path = tmpfile.name
    st.info("🎙️ Enregistrement en cours...")
    audio = sd.rec(int(duration * fs), samplerate=fs, channels=1)
    sd.wait()
    write(audio_path, fs, audio)
    st.success("✅ Enregistrement terminé.")
    return audio_path

def show_emotion_pie_chart(emotions):
    labels = [e["type"] for e in emotions]
    scores = [e["score"] for e in emotions]

    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown("### 🧠 Répartition des émotions")
        fig, ax = plt.subplots()
        ax.pie(scores, labels=labels, autopct="%1.1f%%", startangle=90)
        ax.axis("equal")
        st.pyplot(fig)
