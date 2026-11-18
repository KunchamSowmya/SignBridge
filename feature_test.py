import cv2
import mediapipe as mp

from vision.feature_extractor import extract_landmarks


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
# CAMERA
# ============================================================

camera = cv2.VideoCapture(0, cv2.CAP_DSHOW)

if not camera.isOpened():

    print("ERROR: Camera could not be opened.")
    exit()


print()
print("==========================================")
print("       FEATURE EXTRACTION TEST")
print("==========================================")
print()
print("Show your hand.")
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

    rgb = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb)


    # ========================================================
    # HAND DETECTED
    # ========================================================

    if results.multi_hand_landmarks:

        hand = results.multi_hand_landmarks[0]


        # Draw hand

        mp_drawing.draw_landmarks(
            frame,
            hand,
            mp_hands.HAND_CONNECTIONS
        )


        # ====================================================
        # EXTRACT FEATURES
        # ====================================================

        try:

            features = extract_landmarks(hand)

            print(
                f"Features: {len(features)}",
                end="\r"
            )


            # ------------------------------------------------
            # CHECK FEATURE SIZE
            # ------------------------------------------------

            if len(features) == 63:

                text = "63 FEATURES - OK"

                color = (0, 255, 0)

            else:

                text = f"WRONG FEATURES: {len(features)}"

                color = (0, 0, 255)


            cv2.putText(
                frame,
                text,
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                3
            )


        except Exception as error:

            print()
            print("FEATURE EXTRACTION ERROR:")
            print(error)

            cv2.putText(
                frame,
                "FEATURE ERROR",
                (30, 50),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                (0, 0, 255),
                3
            )


    else:

        cv2.putText(
            frame,
            "NO HAND",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.9,
            (0, 0, 255),
            3
        )


    # ========================================================
    # DISPLAY
    # ========================================================

    cv2.imshow(
        "Feature Extraction Test",
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
print("Feature test finished.")