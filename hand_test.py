import cv2
import mediapipe as mp


# ============================================================
# MEDIAPIPE SETUP
# ============================================================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles


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


camera.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
camera.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)


print()
print("======================================")
print("       MEDIAPIPE HAND TEST")
print("======================================")
print()
print("Show your hand clearly to the camera.")
print("Press Q to quit.")
print()


# ============================================================
# MAIN LOOP
# ============================================================

while True:

    success, frame = camera.read()

    if not success:

        print("ERROR: Cannot read camera.")
        break


    # Mirror camera
    frame = cv2.flip(frame, 1)


    # --------------------------------------------------------
    # Convert BGR to RGB
    # --------------------------------------------------------

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )


    # --------------------------------------------------------
    # MediaPipe hand detection
    # --------------------------------------------------------

    results = hands.process(rgb_frame)


    # --------------------------------------------------------
    # Check hand
    # --------------------------------------------------------

    if results.multi_hand_landmarks:

        hand_count = len(
            results.multi_hand_landmarks
        )

        print(
            f"Hand detected! Count: {hand_count}",
            end="\r"
        )


        # Draw landmarks

        for hand_landmarks in results.multi_hand_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style()
            )


        # Display status

        cv2.putText(
            frame,
            "HAND DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 255, 0),
            3
        )


    else:

        cv2.putText(
            frame,
            "NO HAND DETECTED",
            (30, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (0, 0, 255),
            3
        )


    # --------------------------------------------------------
    # Show camera
    # --------------------------------------------------------

    cv2.imshow(
        "MediaPipe Hand Test",
        frame
    )


    # --------------------------------------------------------
    # Keyboard
    # --------------------------------------------------------

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
print("Test finished.")