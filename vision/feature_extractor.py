def extract_landmarks(hand_landmarks):
    """
    Extract x, y, z coordinates from
    MediaPipe hand landmarks.
    """

    features = []

    for landmark in hand_landmarks.landmark:
        features.append(landmark.x)
        features.append(landmark.y)
        features.append(landmark.z)

    return features