import os
import time
import subprocess
import tempfile

from deep_translator import GoogleTranslator
from gtts import gTTS


class SpeechManager:

    def __init__(self):
        print("Initializing Speech Manager...")
        print("Speech Manager ready.")

    # ==========================================================
    # ENGLISH SPEECH
    # ==========================================================

    def speak_english(self, text):

        if not text:
            print("No English text available.")
            return

        print()
        print("🔊 English:")
        print(text)

        try:
            self._speak_gtts(text, "en")
        except Exception as e:
            print("English speech error:", e)

    # ==========================================================
    # ENGLISH → TELUGU TRANSLATION
    # ==========================================================

    def translate_to_telugu(self, text):

        if not text:
            return ""

        print()
        print("================================")
        print("English → Telugu")
        print("================================")

        print("English:", text)

        try:

            translator = GoogleTranslator(
                source="en",
                target="te"
            )

            telugu = translator.translate(text)

            if telugu:
                print("Telugu:", telugu)
                return telugu

            print("Translation returned empty result.")
            return text

        except Exception as e:

            print("Translation error:", e)

            return text

    # ==========================================================
    # TELUGU SPEECH
    # ==========================================================

    def speak_translated_telugu(self, text):

        if not text:
            print("No text available.")
            return ""

        print()
        print("🔊 Telugu:")

        # Translate English → Telugu
        telugu_text = self.translate_to_telugu(text)

        print("Speaking Telugu:")
        print(telugu_text)

        try:

            self._speak_gtts(
                telugu_text,
                "te"
            )

        except Exception as e:

            print("Telugu speech error:", e)

        return telugu_text

    # ==========================================================
    # GOOGLE TEXT TO SPEECH
    # ==========================================================

    def _speak_gtts(self, text, language):

        if not text:
            return

        # Create temporary MP3
        temp_file = tempfile.NamedTemporaryFile(
            delete=False,
            suffix=".mp3"
        )

        temp_path = temp_file.name

        temp_file.close()

        try:

            tts = gTTS(
                text=text,
                lang=language,
                slow=False
            )

            tts.save(temp_path)

            # Windows Media Player
            os.startfile(temp_path)

            # Give Windows time to start audio
            time.sleep(1)

        finally:

            # Do not delete immediately because
            # Windows may still be playing the file.
            pass


# ==========================================================
# TEST
# ==========================================================

if __name__ == "__main__":

    print()
    print("================================")
    print("SIGNBRIDGE SPEECH TEST")
    print("================================")

    speech = SpeechManager()

    test_text = "Hello, I am happy."

    speech.speak_english(test_text)

    time.sleep(2)

    telugu = speech.speak_translated_telugu(
        test_text
    )

    print()
    print("================================")
    print("Speech test completed.")
    print("================================")