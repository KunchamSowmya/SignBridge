from flask import (
    Flask,
    render_template,
    send_from_directory,
    request,
    jsonify
)

import os
import re
import cv2
import numpy as np
import speech_recognition as sr

from vision.hand_detector import HandDetector
from vision.feature_extractor import extract_landmarks
from vision.predictor import SignPredictor

from language.telugu import (
    translate_to_telugu,
    create_telugu_audio
)


# ============================================================
# FLASK APPLICATION
# ============================================================

app = Flask(__name__)


# ============================================================
# INITIALIZE SIGN LANGUAGE COMPONENTS
# ============================================================

print("Loading SignBridge AI components...")

try:
    detector = HandDetector(
        max_num_hands=1,
        detection_confidence=0.5,
        tracking_confidence=0.5
    )

    predictor = SignPredictor()

    print("✅ Sign language model loaded successfully.")

except Exception as e:

    print("❌ Error loading sign language components:")
    print(e)

    detector = None
    predictor = None


# ============================================================
# SPEECH RECOGNITION
# ============================================================

def recognize_speech_from_microphone():

    recognizer = sr.Recognizer()

    try:

        with sr.Microphone() as source:

            print()
            print("====================================")
            print("🎤 SPEAK NOW")
            print("====================================")

            print("Adjusting for background noise...")

            recognizer.adjust_for_ambient_noise(
                source,
                duration=1
            )

            print("Listening...")

            audio = recognizer.listen(
                source,
                timeout=10,
                phrase_time_limit=10
            )

        print("Recognizing speech...")

        text = recognizer.recognize_google(
            audio,
            language="en-IN"
        )

        print("You said:", text)

        return text

    except sr.WaitTimeoutError:

        print("❌ No speech detected.")

        return ""

    except sr.UnknownValueError:

        print("❌ Could not understand speech.")

        return ""

    except sr.RequestError as e:

        print("❌ Speech recognition service error:")
        print(e)

        return ""

    except Exception as e:

        print("❌ Speech recognition error:")
        print(e)

        return ""


# ============================================================
# HOME
# ============================================================

@app.route("/")
def home():

    return render_template("index.html")


# ============================================================
# DASHBOARD
# ============================================================

@app.route("/dashboard")
def dashboard():

    return render_template("dashboard.html")


# ============================================================
# ABOUT
# ============================================================

@app.route("/about")
def about():

    return render_template("about.html")


# ============================================================
# COMMUNICATION
# ============================================================

@app.route("/communication")
def communication():

    return render_template("communication.html")


# ============================================================
# CAMERA / SIGN RECOGNITION
# ============================================================

@app.route("/camera")
def camera():

    return render_template("camera.html")


# ============================================================
# SPEECH TO SIGN PAGE
# ============================================================

@app.route("/speech-to-sign")
def speech_to_sign():

    return render_template("speech_to_sign.html")


# ============================================================
# SERVE SIGN VIDEOS
# ============================================================

@app.route("/sign_videos/<path:filename>")
def sign_video(filename):

    return send_from_directory(
        os.path.join(
            app.root_path,
            "sign_videos"
        ),
        filename
    )


# ============================================================
# PYTHON SPEECH RECOGNITION API
# ============================================================

@app.route(
    "/recognize-speech",
    methods=["POST"]
)
def recognize_speech():

    try:

        print()
        print("====================================")
        print("Speech recognition request received")
        print("====================================")

        text = recognize_speech_from_microphone()

        if not text:

            return jsonify({
                "success": False,
                "error": "Could not understand speech."
            }), 400

        return jsonify({

            "success": True,

            "text": text

        })

    except Exception as e:

        print("❌ Speech API error:")
        print(e)

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# SPEECH TO SIGN API
# ============================================================

@app.route(
    "/speech-to-sign-api",
    methods=["POST"]
)
def speech_to_sign_api():

    try:

        data = request.get_json()

        if not data:

            return jsonify({

                "success": False,

                "error": "No JSON data received."

            }), 400


        text = data.get(
            "text",
            ""
        ).strip().lower()


        if not text:

            return jsonify({

                "success": False,

                "error": "No speech text received."

            }), 400


        # ----------------------------------------------------
        # Remove punctuation
        # ----------------------------------------------------

        text = re.sub(
            r"[^\w\s]",
            "",
            text
        )


        words = text.split()

        results = []

        i = 0


        # ----------------------------------------------------
        # Convert words into sign videos
        # ----------------------------------------------------

        while i < len(words):


            # ----------------------------------------------
            # Special case: "I am"
            # ----------------------------------------------

            if (
                i + 1 < len(words)
                and words[i] == "i"
                and words[i + 1] == "am"
            ):

                word = "i am"

                filename = "i_am.mp4"

                i += 2


            else:

                word = words[i]

                filename = f"{word}.mp4"

                i += 1


            # ----------------------------------------------
            # Check video
            # ----------------------------------------------

            filepath = os.path.join(

                app.root_path,

                "sign_videos",

                filename

            )


            if os.path.exists(filepath):

                results.append({

                    "word": word,

                    "video": f"/sign_videos/{filename}"

                })

            else:

                print(
                    f"⚠ Sign video not found: {filename}"
                )


        return jsonify({

            "success": True,

            "text": text,

            "results": results

        })


    except Exception as e:

        print(
            "❌ Speech to sign error:"
        )

        print(e)

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# SIGN LANGUAGE IMAGE PREDICTION
# ============================================================

@app.route(
    "/predict",
    methods=["POST"]
)
def predict():

    try:

        # ----------------------------------------------------
        # Check model
        # ----------------------------------------------------

        if detector is None or predictor is None:

            return jsonify({

                "success": False,

                "error": "Sign recognition model is not loaded."

            }), 500


        # ----------------------------------------------------
        # Check image
        # ----------------------------------------------------

        if "image" not in request.files:

            return jsonify({

                "success": False,

                "error": "No image received."

            }), 400


        image_file = request.files["image"]


        if image_file.filename == "":

            return jsonify({

                "success": False,

                "error": "Empty image received."

            }), 400


        # ----------------------------------------------------
        # Read image
        # ----------------------------------------------------

        image_bytes = image_file.read()

        image_array = np.frombuffer(
            image_bytes,
            np.uint8
        )


        frame = cv2.imdecode(
            image_array,
            cv2.IMREAD_COLOR
        )


        if frame is None:

            return jsonify({

                "success": False,

                "error": "Could not decode image."

            }), 400


        # ----------------------------------------------------
        # Detect hand
        # ----------------------------------------------------

        results = detector.detect(frame)


        if not results.multi_hand_landmarks:

            return jsonify({

                "success": True,

                "hand_detected": False,

                "sign": "NO HAND",

                "confidence": 0

            })


        # ----------------------------------------------------
        # Extract landmarks
        # ----------------------------------------------------

        hand_landmarks = (
            results.multi_hand_landmarks[0]
        )


        features = extract_landmarks(
            hand_landmarks
        )


        # ----------------------------------------------------
        # Validate feature size
        # ----------------------------------------------------

        if len(features) != 63:

            return jsonify({

                "success": False,

                "error":
                    f"Expected 63 features, "
                    f"got {len(features)}."

            }), 500


        # ----------------------------------------------------
        # Predict
        # ----------------------------------------------------

        prediction, confidence = (
            predictor.predict(features)
        )


        # ----------------------------------------------------
        # Return result
        # ----------------------------------------------------

        return jsonify({

            "success": True,

            "hand_detected": True,

            "sign": str(prediction),

            "confidence": float(confidence)

        })


    except Exception as e:

        print("❌ Prediction error:")

        print(e)

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# ENGLISH → TELUGU TRANSLATION + TTS
# ============================================================

@app.route(
    "/translate-telugu",
    methods=["POST"]
)
def translate_telugu():

    try:

        data = request.get_json()


        if not data:

            return jsonify({

                "success": False,

                "error": "No JSON data received."

            }), 400


        text = data.get(
            "text",
            ""
        ).strip()


        if not text:

            return jsonify({

                "success": False,

                "error": "No text provided."

            }), 400


        # ----------------------------------------------------
        # Translate
        # ----------------------------------------------------

        telugu_text = translate_to_telugu(
            text
        )


        if not telugu_text:

            return jsonify({

                "success": False,

                "error": "Translation failed."

            }), 500


        # ----------------------------------------------------
        # Telugu audio
        # ----------------------------------------------------

        audio_url = create_telugu_audio(
            telugu_text
        )


        return jsonify({

            "success": True,

            "english": text,

            "telugu": telugu_text,

            "audio_url": audio_url

        })


    except Exception as e:

        print("❌ Telugu translation error:")

        print(e)

        return jsonify({

            "success": False,

            "error": str(e)

        }), 500


# ============================================================
# RUN APPLICATION
# ============================================================

if __name__ == "__main__":

    print()
    print("==========================================")
    print("       SIGNBRIDGE AI")
    print("==========================================")
    print()
    print("🌐 Website:")
    print("   http://127.0.0.1:5000")
    print()
    print("📷 Sign Recognition:")
    print("   http://127.0.0.1:5000/camera")
    print()
    print("🗣️ Speech to Sign:")
    print("   http://127.0.0.1:5000/speech-to-sign")
    print()
    print("==========================================")
    print()

    app.run(
        debug=True
    )