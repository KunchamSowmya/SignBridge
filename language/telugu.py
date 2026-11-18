from deep_translator import GoogleTranslator
from gtts import gTTS
import os
import uuid


AUDIO_FOLDER = os.path.join(
    "static",
    "audio"
)

os.makedirs(AUDIO_FOLDER, exist_ok=True)


def translate_to_telugu(text):
    """
    Translate English text to Telugu.
    """

    if not text or not text.strip():
        return ""

    try:

        translated = GoogleTranslator(
            source="en",
            target="te"
        ).translate(text)

        return translated

    except Exception as e:

        print("Translation error:", e)

        return text


def create_telugu_audio(telugu_text):
    """
    Convert Telugu text into an MP3 audio file.
    """

    if not telugu_text or not telugu_text.strip():
        return None

    try:

        filename = f"telugu_{uuid.uuid4().hex}.mp3"

        filepath = os.path.join(
            AUDIO_FOLDER,
            filename
        )

        tts = gTTS(
            text=telugu_text,
            lang="te",
            slow=False
        )

        tts.save(filepath)

        return f"/static/audio/{filename}"

    except Exception as e:

        print("Telugu TTS error:", e)

        return None