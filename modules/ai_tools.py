import os
import json
from mistralai import Mistral
from groq import Groq

def read_json_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        return file.read()

def speech_to_text(audio_path, language="fr"):
    client = Groq(api_key=os.environ["GROQ_API_KEY"])
    with open(audio_path, "rb") as file:
        transcription = client.audio.transcriptions.create(
            file=file,
            model="whisper-large-v3-turbo",
            prompt="Extrait le texte de l'audio de la manière la plus factuelle possible",
            response_format="verbose_json",
            timestamp_granularities=["segment"],
            language=language,
            temperature=0.0
        )
    return transcription.text

def text_analysis(text: str):
    client = Mistral(api_key=os.environ["MISTRAL_API_KEY"])
    chat_response = client.chat.complete(
        model="magistral-small-2506",
        messages=[
            {
                "role": "system",
                "content": read_json_file("context_analysis.txt"),
            },
            {
                "role": "user",
                "content": f"Analyse le texte ci-dessous (ta réponse doit être dans le format JSON) : {text}",
            },
        ],
        response_format={"type": "json_object"}
    )
    return chat_response.choices[0].message.content

def normalize_emotions(analysis_json: dict):
    emotions = analysis_json.get("émotions", [])
    total = sum(e["score"] for e in emotions)
    if total == 0:
        return emotions
    return [
        {"type": e["type"], "score": round(e["score"] / total, 3)}
        for e in emotions if e["score"] > 0
    ]
