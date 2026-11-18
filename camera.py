import cv2
from collections import deque, Counter

from vision.hand_detector import HandDetector
from vision.feature_extractor import extract_landmarks
from vision.predictor import SignPredictor

from language.sentence_generator import SentenceGenerator
from language.speech import SpeechManager


# ============================================================
# SETTINGS
# ============================================================

CONFIDENCE_THRESHOLD = 0.70
SMOOTHING_FRAMES = 7
STABLE_FRAMES = 6


# ============================================================
# START CAMERA
# ============================================================

def start_camera():

    print()
    print("==============================================")
    print("              SIGNBRIDGE AI")
    print("       REAL-TIME SIGN RECOGNITION")
    print("==============================================")
    print()

    # --------------------------------------------------------
    # HAND DETECTOR
    # --------------------------------------------------------

    detector = HandDetector(
        max_num_hands=1,
        detection_confidence=0.5,
        tracking_confidence=0.5
    )

    # --------------------------------------------------------
    # LOAD MODEL
    # --------------------------------------------------------

    predictor = SignPredictor()

    # --------------------------------------------------------
    # SENTENCE GENERATOR
    # --------------------------------------------------------

    sentence_generator = SentenceGenerator()

    # --------------------------------------------------------
    # SPEECH MANAGER
    # --------------------------------------------------------

    speech_manager = SpeechManager()

    # --------------------------------------------------------
    # OPEN WEBCAM
    # --------------------------------------------------------

    camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

    if not camera.isOpened():

        print("ERROR: Webcam could not be opened.")
        return

    camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    # --------------------------------------------------------
    # PREDICTION HISTORY
    # --------------------------------------------------------

    prediction_history = deque(
        maxlen=SMOOTHING_FRAMES
    )

    # --------------------------------------------------------
    # STABILITY
    # --------------------------------------------------------

    last_stable_prediction = None
    last_added_sign = None

    stable_count = 0

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    current_prediction = "NO HAND"
    current_confidence = 0.0

    sentence = ""

    print("Camera started successfully.")
    print()
    print("Controls:")
    print("Q = Quit")
    print("C = Clear sentence")
    print("B = Remove last word")
    print("E = English speech")
    print("T = Telugu speech")
    print()

    # ========================================================
    # MAIN LOOP
    # ========================================================

    while True:

        # ----------------------------------------------------
        # READ FRAME
        # ----------------------------------------------------

        success, frame = camera.read()

        if not success:

            print("ERROR: Cannot read webcam frame.")
            break

        # ----------------------------------------------------
        # MIRROR
        # ----------------------------------------------------

        frame = cv2.flip(frame, 1)

        height, width = frame.shape[:2]

        # ----------------------------------------------------
        # DETECT HAND
        # ----------------------------------------------------

        results = detector.detect(frame)

        # ----------------------------------------------------
        # DRAW LANDMARKS
        # ----------------------------------------------------

        frame = detector.draw_landmarks(
            frame,
            results
        )

        # ----------------------------------------------------
        # HAND COUNT
        # ----------------------------------------------------

        hand_count = 0

        if results.multi_hand_landmarks:

            hand_count = len(
                results.multi_hand_landmarks
            )

        raw_prediction = None
        raw_confidence = 0.0

        # ====================================================
        # HAND FOUND
        # ====================================================

        if hand_count > 0:

            hand_landmarks = (
                results.multi_hand_landmarks[0]
            )

            # ------------------------------------------------
            # EXTRACT LANDMARKS
            # ------------------------------------------------

            features = extract_landmarks(
                hand_landmarks
            )

            # ------------------------------------------------
            # CHECK FEATURES
            # ------------------------------------------------

            if len(features) != 63:

                current_prediction = "FEATURE ERROR"
                current_confidence = 0.0

            else:

                # ------------------------------------------------
                # MODEL PREDICTION
                # ------------------------------------------------

                prediction, confidence = predictor.predict(
                    features
                )

                raw_prediction = prediction
                raw_confidence = confidence

                current_confidence = confidence

                # ------------------------------------------------
                # CONFIDENCE FILTER
                # ------------------------------------------------

                if confidence >= CONFIDENCE_THRESHOLD:

                    prediction_history.append(
                        prediction
                    )

                else:

                    prediction_history.append(
                        "uncertain"
                    )

                # ------------------------------------------------
                # SMOOTH PREDICTION
                # ------------------------------------------------

                if len(prediction_history) > 0:

                    stable_prediction = Counter(
                        prediction_history
                    ).most_common(1)[0][0]

                    # ==========================================
                    # LOW CONFIDENCE
                    # ==========================================

                    if stable_prediction == "uncertain":

                        current_prediction = "LOW CONFIDENCE"

                        stable_count = 0

                    # ==========================================
                    # VALID SIGN
                    # ==========================================

                    else:

                        current_prediction = (
                            stable_prediction.upper()
                        )

                        # --------------------------------------
                        # STABILITY
                        # --------------------------------------

                        if (
                            stable_prediction
                            == last_stable_prediction
                        ):

                            stable_count += 1

                        else:

                            last_stable_prediction = (
                                stable_prediction
                            )

                            stable_count = 1

                        # --------------------------------------
                        # ACCEPT SIGN
                        # --------------------------------------

                        if stable_count >= STABLE_FRAMES:

                            # IMPORTANT:
                            # Do not repeatedly add the same
                            # sign while the hand is held.

                            if (
                                stable_prediction
                                != last_added_sign
                            ):

                                sentence_generator.add_word(
                                    stable_prediction
                                )

                                sentence = (
                                    sentence_generator
                                    .generate_sentence()
                                )

                                last_added_sign = (
                                    stable_prediction
                                )

                                print()
                                print(
                                    "================================"
                                )
                                print(
                                    "Recognized:",
                                    stable_prediction
                                )
                                print(
                                    "Confidence:",
                                    f"{confidence * 100:.2f}%"
                                )
                                print(
                                    "Sentence:",
                                    sentence
                                )
                                print(
                                    "================================"
                                )

                            # Reset stability counter
                            stable_count = 0

        # ====================================================
        # NO HAND
        # ====================================================

        else:

            prediction_history.clear()

            last_stable_prediction = None

            # IMPORTANT:
            # Reset this when hand disappears.
            # This allows the user to show the same sign
            # again later.

            last_added_sign = None

            stable_count = 0

            current_prediction = "NO HAND"
            current_confidence = 0.0

        # ====================================================
        # PROFESSIONAL HEADER
        # ====================================================

        cv2.rectangle(
            frame,
            (0, 0),
            (width, 70),
            (15, 15, 15),
            -1
        )

        cv2.putText(
            frame,
            "SIGNBRIDGE AI",
            (20, 32),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.78,
            (255, 255, 255),
            2
        )

        cv2.putText(
            frame,
            "Real-Time Sign Language Recognition",
            (20, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.42,
            (180, 180, 180),
            1
        )

        # ====================================================
        # RECOGNITION PANEL
        # ====================================================

        panel_x1 = width - 300
        panel_y1 = 15

        panel_x2 = width - 15
        panel_y2 = 105

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (panel_x1, panel_y1),
            (panel_x2, panel_y2),
            (20, 20, 20),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.75,
            frame,
            0.25,
            0,
            frame
        )

        cv2.putText(
            frame,
            "SIGN",
            (
                panel_x1 + 15,
                panel_y1 + 25
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (170, 170, 170),
            1
        )

        cv2.putText(
            frame,
            current_prediction,
            (
                panel_x1 + 15,
                panel_y1 + 55
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.65,
            (0, 255, 0),
            2
        )

        cv2.putText(
            frame,
            f"{current_confidence * 100:.0f}%",
            (
                panel_x1 + 200,
                panel_y1 + 55
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.50,
            (255, 255, 255),
            1
        )

        cv2.putText(
            frame,
            f"Hands: {hand_count}/1",
            (
                panel_x1 + 15,
                panel_y1 + 78
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (0, 255, 255),
            1
        )

        cv2.putText(
            frame,
            f"Stable: {stable_count}/{STABLE_FRAMES}",
            (
                panel_x1 + 120,
                panel_y1 + 78
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.35,
            (200, 200, 200),
            1
        )

        # ====================================================
        # SENTENCE BAR
        # ====================================================

        sentence_y1 = height - 85
        sentence_y2 = height - 10

        overlay = frame.copy()

        cv2.rectangle(
            overlay,
            (15, sentence_y1),
            (width - 15, sentence_y2),
            (15, 15, 15),
            -1
        )

        cv2.addWeighted(
            overlay,
            0.82,
            frame,
            0.18,
            0,
            frame
        )

        cv2.putText(
            frame,
            "Sentence:",
            (
                30,
                sentence_y1 + 27
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.40,
            (160, 160, 160),
            1
        )

        if sentence:

            display_sentence = sentence

        else:

            display_sentence = "Show a sign..."

        if len(display_sentence) > 75:

            display_sentence = (
                display_sentence[-75:]
            )

        cv2.putText(
            frame,
            display_sentence,
            (
                115,
                sentence_y1 + 28
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.48,
            (255, 255, 255),
            1
        )

        # ====================================================
        # CONTROLS
        # ====================================================

        cv2.putText(
            frame,
            "Q Quit",
            (
                width - 285,
                sentence_y1 + 55
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.32,
            (180, 180, 180),
            1
        )

        cv2.putText(
            frame,
            "C Clear",
            (
                width - 220,
                sentence_y1 + 55
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.32,
            (180, 180, 180),
            1
        )

        cv2.putText(
            frame,
            "B Back",
            (
                width - 150,
                sentence_y1 + 55
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.32,
            (180, 180, 180),
            1
        )

        cv2.putText(
            frame,
            "E English",
            (
                width - 85,
                sentence_y1 + 55
            ),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.32,
            (180, 180, 180),
            1
        )

        # ====================================================
        # SHOW CAMERA
        # ====================================================

        cv2.imshow(
            "SignBridge AI - Live Recognition",
            frame
        )

        # ====================================================
        # KEYBOARD
        # ====================================================

        key = cv2.waitKey(1) & 0xFF

        # ----------------------------------------------------
        # Q - QUIT
        # ----------------------------------------------------

        if key == ord("q"):

            break

        # ----------------------------------------------------
        # C - CLEAR
        # ----------------------------------------------------

        elif key == ord("c"):

            sentence_generator.clear()

            sentence = ""

            prediction_history.clear()

            last_stable_prediction = None

            last_added_sign = None

            stable_count = 0

            print("Sentence cleared.")

        # ----------------------------------------------------
        # B - BACKSPACE
        # ----------------------------------------------------

        elif key == ord("b"):

            sentence_generator.remove_last_word()

            sentence = (
                sentence_generator
                .generate_sentence()
            )

            print("Last word removed.")

        # ----------------------------------------------------
        # E - ENGLISH
        # ----------------------------------------------------

        elif key == ord("e"):

            print()
            print("E pressed")

            if sentence:

                print("Speaking English...")

                try:

                    speech_manager.speak_english(
                        sentence
                    )

                    print(
                        "English speech completed."
                    )

                except Exception as e:

                    print(
                        "English speech error:",
                        e
                    )

            else:

                print(
                    "No sentence available."
                )

        # ----------------------------------------------------
        # T - TELUGU
        # ----------------------------------------------------

        elif key == ord("t"):

            print()
            print("T pressed")

            if sentence:

                print(
                    "Translating to Telugu..."
                )

                try:

                    speech_manager.speak_translated_telugu(
                        sentence
                    )

                    print(
                        "Telugu speech completed."
                    )

                except Exception as e:

                    print(
                        "Telugu speech error:",
                        e
                    )

            else:

                print(
                    "No sentence available."
                )

    # ========================================================
    # CLEANUP
    # ========================================================

    camera.release()

    cv2.destroyAllWindows()

    print()
    print("==============================================")
    print("Camera stopped.")
    print("Final sentence:")
    print(sentence)
    print("==============================================")
    print()


# ============================================================
# PROGRAM ENTRY POINT
# ============================================================

if __name__ == "__main__":

    start_camera()