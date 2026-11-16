
from pathlib import Path
import joblib


BASE_DIR = Path(__file__).resolve().parent

MODEL_PATH = BASE_DIR / "models" / "phishing_model.pkl"
VECTORIZER_PATH = BASE_DIR / "models" / "tfidf_vectorizer.pkl"

LABEL_NAMES = {
    0: "Legitimate",
    1: "Spam",
    2: "Phishing",
}

model = joblib.load(MODEL_PATH)
vectorizer = joblib.load(VECTORIZER_PATH)


def predict_email(text: str) -> dict:
    if not text or not text.strip():
        return {
            "prediction": "Unknown",
            "confidence": 0.0,
            "spam_probability": 0.0,
            "phishing_probability": 0.0,
            "malicious_probability": 0.0,
            "probabilities": {
                "Legitimate": 0.0,
                "Spam": 0.0,
                "Phishing": 0.0,
            },
        }

    features = vectorizer.transform([text])

    prediction = int(model.predict(features)[0])
    raw_probabilities = model.predict_proba(features)[0]

    probabilities = {
        LABEL_NAMES[int(class_id)]: round(
            float(probability) * 100, 2
        )
        for class_id, probability in zip(
            model.classes_,
            raw_probabilities,
        )
    }

    spam_probability = probabilities.get("Spam", 0.0)
    phishing_probability = probabilities.get("Phishing", 0.0)

    malicious_probability = (
        spam_probability + phishing_probability
    )

    confidence = probabilities[LABEL_NAMES[prediction]]

    return {
        "prediction": LABEL_NAMES[prediction],
        "confidence": round(confidence, 2),
        "spam_probability": spam_probability,
        "phishing_probability": phishing_probability,
        "malicious_probability": round(
            malicious_probability, 2
        ),
        "probabilities": probabilities,
    }
