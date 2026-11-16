
import json
from datetime import datetime, timezone
from pathlib import Path

import joblib
import pandas as pd

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)
from sklearn.model_selection import train_test_split


BASE_DIR = Path(__file__).resolve().parent

DATASET_PATH = BASE_DIR / "dataset" / "three_class_emails_final.csv"
MODEL_DIR = BASE_DIR / "models"

MODEL_PATH = MODEL_DIR / "phishing_model.pkl"
VECTORIZER_PATH = MODEL_DIR / "tfidf_vectorizer.pkl"
METADATA_PATH = MODEL_DIR / "model_metadata.json"

LABEL_NAMES = {
    0: "Legitimate",
    1: "Spam",
    2: "Phishing",
}

TEST_SIZE = 0.25
RANDOM_STATE = 42


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    print(f"Dataset path: {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH)

    required_columns = {"text", "label"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Dataset must contain columns: {required_columns}"
        )

    original_rows = len(df)

    # Remove rows with missing text or labels.
    df = df.dropna(subset=["text", "label"]).copy()

    df["text"] = df["text"].astype(str).str.strip()

    df["label"] = pd.to_numeric(
        df["label"],
        errors="coerce",
    )

    df = df.dropna(subset=["label"]).copy()
    df["label"] = df["label"].astype(int)

    # Remove empty email text.
    df = df[df["text"] != ""].copy()

    # Validate labels.
    invalid_labels = set(df["label"].unique()) - set(LABEL_NAMES)

    if invalid_labels:
        raise ValueError(
            f"Invalid labels found: {invalid_labels}"
        )

    # Remove exact duplicate text records.
    rows_before_deduplication = len(df)

    df = df.drop_duplicates(
        subset=["text"],
        keep="first",
    ).copy()

    duplicates_removed = (
        rows_before_deduplication - len(df)
    )

    # Validate that all classes are still present.
    missing_classes = (
        set(LABEL_NAMES) - set(df["label"].unique())
    )

    if missing_classes:
        raise ValueError(
            f"Missing classes in dataset after cleaning: "
            f"{missing_classes}"
        )

    print(f"Original rows: {original_rows}")
    print(f"Cleaned rows: {len(df)}")
    print(f"Duplicate rows removed: {duplicates_removed}")

    return df, duplicates_removed


def build_vectorizer():
    return TfidfVectorizer(
        lowercase=True,
        stop_words="english",
        ngram_range=(1, 2),
        max_features=10000,
        sublinear_tf=True,
    )


def build_model():
    return LogisticRegression(
        max_iter=1000,
        class_weight="balanced",
        random_state=RANDOM_STATE,
    )


def main():

    MODEL_DIR.mkdir(parents=True, exist_ok=True)

    # Load dataset.
    print("\nLoading PhishGuard dataset...")

    df, duplicates_removed = load_dataset()

    X = df["text"]
    y = df["label"]

    print("\nDataset distribution:")

    for label, name in LABEL_NAMES.items():
        count = int((y == label).sum())
        print(f"{name}: {count}")

    # Train/test split.
    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=TEST_SIZE,
        random_state=RANDOM_STATE,
        stratify=y,
    )

    print("\nTraining samples:", len(X_train))
    print("Testing samples:", len(X_test))

    # TF-IDF feature extraction.
    print("\nExtracting TF-IDF features...")

    vectorizer = build_vectorizer()

    X_train_vectorized = vectorizer.fit_transform(X_train)
    X_test_vectorized = vectorizer.transform(X_test)

    # Train model.
    print("\nTraining three-class classifier...")

    model = build_model()

    model.fit(
        X_train_vectorized,
        y_train,
    )

    # Predictions.
    predictions = model.predict(X_test_vectorized)

    probabilities = model.predict_proba(
        X_test_vectorized
    )

    # Evaluation metrics.
    accuracy = accuracy_score(
        y_test,
        predictions,
    )

    macro_precision = precision_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    macro_recall = recall_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    macro_f1 = f1_score(
        y_test,
        predictions,
        average="macro",
        zero_division=0,
    )

    weighted_f1 = f1_score(
        y_test,
        predictions,
        average="weighted",
        zero_division=0,
    )

    try:
        roc_auc = roc_auc_score(
            y_test,
            probabilities,
            multi_class="ovr",
            average="macro",
            labels=[0, 1, 2],
        )
    except ValueError:
        roc_auc = None

    metrics = {
        "accuracy": round(float(accuracy), 4),
        "macro_precision": round(float(macro_precision), 4),
        "macro_recall": round(float(macro_recall), 4),
        "macro_f1": round(float(macro_f1), 4),
        "weighted_f1": round(float(weighted_f1), 4),
        "roc_auc_ovr_macro": (
            round(float(roc_auc), 4)
            if roc_auc is not None else None
        ),
    }

    # Confusion matrix.
    matrix = confusion_matrix(
        y_test,
        predictions,
        labels=[0, 1, 2],
    )

    # Classification report.
    report = classification_report(
        y_test,
        predictions,
        labels=[0, 1, 2],
        target_names=[
            LABEL_NAMES[0],
            LABEL_NAMES[1],
            LABEL_NAMES[2],
        ],
        output_dict=True,
        zero_division=0,
    )

    # Per-class metrics.
    per_class_metrics = {
        LABEL_NAMES[label]: {
            "precision": round(
                report[LABEL_NAMES[label]]["precision"], 4
            ),
            "recall": round(
                report[LABEL_NAMES[label]]["recall"], 4
            ),
            "f1_score": round(
                report[LABEL_NAMES[label]]["f1-score"], 4
            ),
            "support": int(
                report[LABEL_NAMES[label]]["support"]
            ),
        }
        for label in LABEL_NAMES
    }

    # Display evaluation results.
    print("\n" + "=" * 55)
    print("PHISHGUARD THREE-CLASS MODEL EVALUATION")
    print("=" * 55)

    print(f"\nAccuracy       : {metrics['accuracy']}")
    print(f"Macro Precision: {metrics['macro_precision']}")
    print(f"Macro Recall   : {metrics['macro_recall']}")
    print(f"Macro F1       : {metrics['macro_f1']}")
    print(f"Weighted F1    : {metrics['weighted_f1']}")
    print(f"Multiclass AUC : {metrics['roc_auc_ovr_macro']}")

    print("\nClassification Report:")

    print(
        classification_report(
            y_test,
            predictions,
            labels=[0, 1, 2],
            target_names=[
                LABEL_NAMES[0],
                LABEL_NAMES[1],
                LABEL_NAMES[2],
            ],
            zero_division=0,
        )
    )

    print("Confusion Matrix:")
    print(matrix)

    print("\nPer-Class Metrics:")

    for class_name, values in per_class_metrics.items():
        print(f"\n{class_name}:")
        print(f"  Precision: {values['precision']}")
        print(f"  Recall   : {values['recall']}")
        print(f"  F1-score : {values['f1_score']}")
        print(f"  Support  : {values['support']}")

    # Save model artifacts.
    joblib.dump(model, MODEL_PATH)
    joblib.dump(vectorizer, VECTORIZER_PATH)

    # Metadata.
    metadata = {
        "model_name": "phishing_model",
        "task": "three-class email classification",
        "trained_at": datetime.now(timezone.utc).isoformat(),

        "dataset": {
            "path": str(DATASET_PATH),
            "rows": len(df),
            "duplicate_rows_removed": duplicates_removed,
            "class_distribution": {
                LABEL_NAMES[label]: int((y == label).sum())
                for label in LABEL_NAMES
            },
            "label_mapping": {
                str(label): name
                for label, name in LABEL_NAMES.items()
            },
            "manual_review": {
                "reviewed_records": 148,
                "excluded_records": 4,
                "review_source": "quality_review.csv",
            },
        },

        "split": {
            "test_size": TEST_SIZE,
            "random_state": RANDOM_STATE,
            "train_rows": len(X_train),
            "test_rows": len(X_test),
            "strategy": "stratified random split",
        },

        "features": {
            "type": "TF-IDF",
            "ngram_range": [1, 2],
            "max_features": 10000,
            "stop_words": "english",
            "sublinear_tf": True,
        },

        "model": {
            "type": "LogisticRegression",
            "parameters": {
                "max_iter": 1000,
                "class_weight": "balanced",
            },
        },

        "metrics": metrics,
        "per_class_metrics": per_class_metrics,
        "classification_report": report,

        "confusion_matrix": {
            "labels": [
                LABEL_NAMES[0],
                LABEL_NAMES[1],
                LABEL_NAMES[2],
            ],
            "matrix": matrix.tolist(),
        },
    }

    METADATA_PATH.write_text(
        json.dumps(metadata, indent=2),
        encoding="utf-8",
    )

    print("\nModel artifacts saved successfully!")

    print("\nSaved files:")
    print(MODEL_PATH)
    print(VECTORIZER_PATH)
    print(METADATA_PATH)


if __name__ == "__main__":
    main()
