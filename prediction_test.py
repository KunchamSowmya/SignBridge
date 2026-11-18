import cv2
import mediapipe as mp

from vision.feature_extractor import extract_landmarks
from vision.predictor import SignPredictor


# ============================================================
# MEDIAPIPE
# ============================================================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.3,
    min_tracking_confidence=0.3
)


# ============================================================
# LOAD MODEL
# ============================================================

print()
print("==========================================")
print("       RANDOM FOREST PREDICTION TEST")
print("==========================================")
print()

try:

    predictor = SignPredictor()

    print("Model loaded successfully.")

except Exception as error:

    print("MODEL ERROR:")
    print(error)
    exit()


# ============================================================
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():

    print("ERROR: Camera could not be opened.")
    exit()


print()
print("Show one of your trained signs.")
print("Press Q to quit.")
print()


# ============================================================
# LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:

        print("Cannot read camera.")
        break


    frame = cv2.flip(frame, 1)


    # --------------------------------------------------------
    # RGB
    # --------------------------------------------------------

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # MEDIAPIPE
    # --------------------------------------------------------

    results = hands.process(rgb)


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]


        # Draw landmarks

        mp_drawing.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # ====================================================
        # FEATURES
        # ====================================================

        try:

            features = extract_landmarks(hand)


            # =================================================
            # PREDICTION
            # =================================================

            if len(features) == 63:

                prediction, confidence = predictor.predict(
                    features
                )


                print(
                    f"Prediction: {prediction} | "
                    f"Confidence: {confidence * 100:.2f}%",
                    end="\r"
                )


                # ---------------------------------------------
                # DISPLAY SIGN
                # ---------------------------------------------

                cv2.putText(
                    frame,
                    str(prediction),
                    (30, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1.2,
                    (0, 255, 0),
                    3
                )


                # ---------------------------------------------
                # DISPLAY CONFIDENCE
                # ---------------------------------------------

                cv2.putText(
                    frame,
                    f"Confidence: {confidence * 100:.1f}%",
                    (30, 95),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.8,
                    (255, 255, 255),
                    2
                )


            else:

                cv2.putText(
                    frame,
                    "FEATURE ERROR",
                    (30, 55),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    1,
                    (0, 0, 255),
                    3
                )


        except Exception as error:

            print()
            print()
            print("PREDICTION ERROR:")
            print(error)

            cv2.putText(
                frame,
                "PREDICTION ERROR",
                (30, 55),
                cv2.FONT_HERSHEY_SIMPLEX,
                1,
                (0, 0, 255),
                3
            )


    # ========================================================
    # NO HAND
    # ========================================================

    else:

        cv2.putText(
            frame,
            "NO HAND",
            (30, 55),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Random Forest Prediction Test",
        frame
    )


    key = cv2.waitKey(1) & 0xFF


    if key == ord("q"):

        break


# ============================================================
# CLEANUP
# ============================================================

camera.release()

cv2.destroyAllWindows()

hands.close()

print()
print()
print("Prediction test finished.")