import speech_recognition as sr


def listen_and_recognize():
    recognizer = sr.Recognizer()

    with sr.Microphone() as source:

        print("\nAdjusting for background noise...")
        recognizer.adjust_for_ambient_noise(source, duration=1)

        print("====================================")
        print("🎤 SPEAK NOW")
        print("====================================")

        audio = recognizer.listen(source)

    try:
        print("Recognizing speech...")

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You said:", text)

        return text

    except sr.UnknownValueError:
        print("Could not understand the speech.")
        return ""

    except sr.RequestError as e:
        print("Speech recognition service error:", e)
        return ""


if __name__ == "__main__":
    listen_and_recognize()