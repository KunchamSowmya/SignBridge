import cv2
import csv
import os
import mediapipe as mp


# ==========================================
# CONFIGURATION
# ==========================================

DATASET_FILE = "dataset/sign_landmarks.csv"

MAX_SAMPLES = 500

# ==========================================
# CREATE DATASET DIRECTORY
# ==========================================

os.makedirs("dataset", exist_ok=True)


# ==========================================
# GET SIGN NAME
# ==========================================

sign_name = input("Enter the sign name: ").strip().lower()

if not sign_name:
    print("ERROR: Sign name cannot be empty.")
    exit()


# ==========================================
# MEDIAPIPE INITIALIZATION
# ==========================================

mp_hands = mp.solutions.hands
mp_drawing = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    static_image_mode=False,
    max_num_hands=1,
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)


# ==========================================
# CREATE CSV FILE
# ==========================================

file_exists = os.path.exists(DATASET_FILE)

file = open(
    DATASET_FILE,
    mode="a",
    newline=""
)

writer = csv.writer(file)


# ==========================================
# CSV HEADER
# ==========================================

if not file_exists:

    header = []

    for i in range(21):
        header.append(f"x{i}")
        header.append(f"y{i}")
        header.append(f"z{i}")

    header.append("label")

    writer.writerow(header)


# ==========================================
# OPEN CAMERA
# ==========================================

camera = cv2.VideoCapture(0)

if not camera.isOpened():

    print("ERROR: Could not open webcam.")

    file.close()

    exit()


print()
print("======================================")
print("       SIGN DATA COLLECTION")
print("======================================")
print()
print("Sign:", sign_name)
print("Target samples:", MAX_SAMPLES)
print()
print("Press SPACE to start collecting.")
print("Press Q to quit.")
print()


# ==========================================
# WAIT FOR SPACE
# ==========================================

started = False

sample_count = 0


while True:

    success, frame = camera.read()

    if not success:
        print("ERROR: Could not read camera.")
        break

    frame = cv2.flip(frame, 1)

    rgb_frame = cv2.cvtColor(
        frame,
        cv2.COLOR_BGR2RGB
    )

    results = hands.process(rgb_frame)


    # ======================================
    # DRAW HAND LANDMARKS
    # ======================================

    if results.multi_hand_landmarks:

        for hand_landmarks in results.multi_hand_landmarks:

            mp_drawing.draw_landmarks(
                frame,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS
            )


    # ======================================
    # INFORMATION DISPLAY
    # ======================================

    cv2.putText(
        frame,
        f"Sign: {sign_name.upper()}",
        (20, 40),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.8,
        (255, 255, 255),
        2
    )

    cv2.putText(
        frame,
        f"Samples: {sample_count}/{MAX_SAMPLES}",
        (20, 80),
        cv2.FONT_HERSHEY_SIMPLEX,
        0.7,
        (0, 255, 0),
        2
    )


    if not started:

        cv2.putText(
            frame,
            "Press SPACE to start",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 255),
            2
        )

    else:

        cv2.putText(
            frame,
            "COLLECTING...",
            (20, 120),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )


    # ======================================
    # START COLLECTION
    # ======================================

    key = cv2.waitKey(1) & 0xFF


    if key == ord(" "):

        started = True

        print("Collection started...")


    # ======================================
    # COLLECT LANDMARK DATA
    # ======================================

    if started and results.multi_hand_landmarks:

        hand_landmarks = results.multi_hand_landmarks[0]

        row = []


        # ----------------------------------
        # Extract 21 landmarks
        # ----------------------------------

        for landmark in hand_landmarks.landmark:

            row.append(landmark.x)
            row.append(landmark.y)
            row.append(landmark.z)


        # ----------------------------------
        # Add label
        # ----------------------------------

        row.append(sign_name)


        writer.writerow(row)

        file.flush()

        sample_count += 1


        # ----------------------------------
        # Small delay between samples
        # ----------------------------------

        cv2.waitKey(30)


    # ======================================
    # COMPLETED
    # ======================================

    if sample_count >= MAX_SAMPLES:

        print()
        print("======================================")
        print("Dataset collection completed!")
        print("Sign:", sign_name)
        print("Samples:", sample_count)
        print("======================================")

        break


    # ======================================
    # QUIT
    # ======================================

    if key == ord("q"):

        print("Collection stopped.")

        break


    # ======================================
    # DISPLAY
    # ======================================

    cv2.imshow(
        "SignBridge AI - Dataset Collector",
        frame
    )


# ==========================================
# CLEANUP
# ==========================================

camera.release()

file.close()

cv2.destroyAllWindows()

hands.close()