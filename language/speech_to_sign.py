import speech_recognition as sr


class SpeechToSign:

    def __init__(self):

        self.recognizer = sr.Recognizer()

        # Make recognition less sensitive to small noises
        self.recognizer.energy_threshold = 300

        self.recognizer.dynamic_energy_threshold = True

        self.recognizer.pause_threshold = 0.8

        self.recognizer.phrase_threshold = 0.3

        # ==========================================
        # YOUR CURRENT SIGN VOCABULARY
        # ==========================================

        self.sign_vocabulary = {

            "hello": "hello",

            "goodbye": "goodbye",

            "good": "good",

            "you": "you",

            "no": "no",

            "sorry": "sorry",

            "home": "home",

            "i am": "i_am",

            "happy": "happy",

            "eat": "eat"
        }

    # ==============================================
    # LISTEN
    # ==============================================

    def listen(self):

        microphone = sr.Microphone()

        print()
        print("================================")
        print("Checking microphone...")
        print("================================")

        try:

            with microphone as source:

                print("Adjusting for background noise...")

                self.recognizer.adjust_for_ambient_noise(
                    source,
                    duration=2
                )

                print()
                print("================================")
                print("🎤 LISTENING")
                print("Speak clearly now...")
                print("================================")

                audio = self.recognizer.listen(
                    source,
                    timeout=10,
                    phrase_time_limit=8
                )

        except sr.WaitTimeoutError:

            print()
            print("No speech detected.")

            return ""

        except OSError as e:

            print()
            print("Microphone error:")
            print(e)

            return ""

        # ==========================================
        # CONVERT SPEECH → TEXT
        # ==========================================

        print()
        print("Processing speech...")

        try:

            text = self.recognizer.recognize_google(
                audio,
                language="en-IN"
            )

            text = text.lower().strip()

            print()
            print("================================")
            print("YOU SAID:")
            print(text)
            print("================================")

            return text

        except sr.UnknownValueError:

            print()
            print("================================")
            print("Speech was captured, but")
            print("the words could not be understood.")
            print("================================")

            return ""

        except sr.RequestError as e:

            print()
            print("Google Speech Recognition error:")
            print(e)

            return ""

    # ==============================================
    # FIND SIGN VIDEOS
    # ==============================================

    def find_signs(self, text):

        if not text:

            return []

        words = text.lower().split()

        signs = []

        i = 0

        while i < len(words):

            # --------------------------------------
            # Check two-word sign
            # --------------------------------------

            if i + 1 < len(words):

                two_words = (
                    words[i]
                    + " "
                    + words[i + 1]
                )

                if two_words in self.sign_vocabulary:

                    signs.append(
                        self.sign_vocabulary[
                            two_words
                        ]
                    )

                    i += 2

                    continue

            # --------------------------------------
            # Single-word sign
            # --------------------------------------

            word = (
                words[i]
                .replace(".", "")
                .replace(",", "")
                .replace("!", "")
                .replace("?", "")
            )

            if word in self.sign_vocabulary:

                signs.append(
                    self.sign_vocabulary[word]
                )

            else:

                print(
                    f"⚠ No sign video for: {word}"
                )

            i += 1

        return signs


# ==============================================
# MAIN TEST
# ==============================================

if __name__ == "__main__":

    system = SpeechToSign()

    text = system.listen()

    if text:

        signs = system.find_signs(text)

        print()
        print("================================")
        print("SIGN VIDEOS REQUIRED")
        print("================================")

        if signs:

            for sign in signs:

                print(
                    f"▶ {sign}.mp4"
                )

        else:

            print(
                "No matching sign videos found."
            )

    else:

        print()
        print(
            "No text was recognized."
        )