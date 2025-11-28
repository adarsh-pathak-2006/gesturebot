# backend/tts.py → FINAL WORKING gTTS
import os
import time
from gtts import gTTS
from flask import current_app

def generate_tts_url(text: str):
    if not text or not str(text).strip():
        return None

    try:
        clean_text = ''.join(c for c in str(text) if ord(c) < 128).strip()
        if not clean_text:
            return None

        filename = f"tts_{int(time.time()*1000)}.mp3"
        filepath = os.path.join(current_app.static_folder, filename)

        tts = gTTS(text=clean_text, lang='en', slow=False)
        tts.save(filepath)

        return f"/static/{filename}"
    except Exception as e:
        print(f"gTTS Error: {e}")
        return None