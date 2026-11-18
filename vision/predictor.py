import os
import joblib


class SignPredictor:

    def __init__(self):

        model_path = "models/sign_model.pkl"
        labels_path = "models/labels.pkl"

        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Model not found: {model_path}"
            )

        if not os.path.exists(labels_path):
            raise FileNotFoundError(
                f"Labels not found: {labels_path}"
            )

        self.model = joblib.load(model_path)
        self.labels = joblib.load(labels_path)

    def predict(self, features):

        # Convert to 2D input
        data = [features]

        prediction = self.model.predict(data)[0]

        probabilities = self.model.predict_proba(data)[0]

        confidence = max(probabilities)

        return prediction, confidence