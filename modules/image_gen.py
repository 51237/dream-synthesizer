import os
import openai

def generate_dream_image(prompt: str) -> str:
    try:
        openai.api_key = os.getenv("OPENAI_API_KEY")
        response = openai.images.generate(
            model="dall-e-3",
            prompt=prompt,
            n=1,
            size="1024x1024",
            quality="standard"
        )
        return response.data[0].url
    except Exception as e:
        print("Erreur DALL·E :", e)
        return None
