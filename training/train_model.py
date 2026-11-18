import os
import joblib
import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix
)


# ==========================================
# CONFIGURATION
# ==========================================

DATASET_PATH = "dataset/sign_landmarks.csv"

MODEL_DIR = "models"

MODEL_PATH = os.path.join(
    MODEL_DIR,
    "sign_model.pkl"
)

LABEL_PATH = os.path.join(
    MODEL_DIR,
    "labels.pkl"
)


# ==========================================
# CREATE MODEL DIRECTORY
# ==========================================

os.makedirs(
    MODEL_DIR,
    exist_ok=True
)


# ==========================================
# LOAD DATASET
# ==========================================

print("\nLoading dataset...")

df = pd.read_csv(
    DATASET_PATH
)

print("Dataset shape:", df.shape)


# ==========================================
# CHECK MISSING VALUES
# ==========================================

missing_values = df.isnull().sum().sum()

print(
    "Missing values:",
    missing_values
)


if missing_values > 0:

    print(
        "ERROR: Dataset contains missing values."
    )

    exit()


# ==========================================
# SEPARATE FEATURES AND LABEL
# ==========================================

X = df.drop(
    columns=["label"]
)

y = df["label"]


# ==========================================
# DISPLAY CLASSES
# ==========================================

labels = sorted(
    y.unique()
)

print("\nClasses:")

for index, label in enumerate(labels):

    print(
        f"{index}: {label}"
    )


print(
    "\nNumber of classes:",
    len(labels)
)


# ==========================================
# TRAIN / TEST SPLIT
# ==========================================

X_train, X_test, y_train, y_test = train_test_split(

    X,
    y,

    test_size=0.20,

    random_state=42,

    stratify=y
)


print("\nTraining samples:", len(X_train))
print("Testing samples:", len(X_test))


# ==========================================
# RANDOM FOREST MODEL
# ==========================================

print("\nTraining Random Forest...")

model = RandomForestClassifier(

    n_estimators=300,

    max_depth=None,

    min_samples_split=2,

    min_samples_leaf=1,

    random_state=42,

    n_jobs=-1
)


model.fit(
    X_train,
    y_train
)


print("Training completed.")


# ==========================================
# PREDICTION
# ==========================================

y_pred = model.predict(
    X_test
)


# ==========================================
# ACCURACY
# ==========================================

accuracy = accuracy_score(
    y_test,
    y_pred
)


print("\n========================================")
print("MODEL PERFORMANCE")
print("========================================")

print(
    f"Accuracy: {accuracy * 100:.2f}%"
)


# ==========================================
# CLASSIFICATION REPORT
# ==========================================

print("\nClassification Report:")

print(
    classification_report(
        y_test,
        y_pred,
        zero_division=0
    )
)


# ==========================================
# CONFUSION MATRIX
# ==========================================

cm = confusion_matrix(
    y_test,
    y_pred,
    labels=labels
)

print("\nConfusion Matrix:")

print(cm)


# ==========================================
# SAVE MODEL
# ==========================================

joblib.dump(
    model,
    MODEL_PATH
)

joblib.dump(
    labels,
    LABEL_PATH
)


print("\n========================================")
print("MODEL SAVED SUCCESSFULLY")
print("========================================")

print(
    "Model:",
    MODEL_PATH
)

print(
    "Labels:",
    LABEL_PATH
)