
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent

SOURCE_PATH = BASE_DIR / "dataset" / "cleaned_emails.csv"
OUTPUT_PATH = BASE_DIR / "dataset" / "three_class_review.csv"


def main():
    if not SOURCE_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {SOURCE_PATH}"
        )

    df = pd.read_csv(SOURCE_PATH)

    required_columns = {"subject", "body", "label"}

    if not required_columns.issubset(df.columns):
        raise ValueError(
            f"Dataset must contain: {required_columns}"
        )

    # Preserve the original binary label for reference.
    df["original_label"] = df["label"]

    # New three-class label.
    # Leave it blank until the email has been reviewed.
    df["class_label"] = pd.NA

    # Track whether an email has been reviewed.
    df["review_status"] = "pending"

    # Save to a separate file. Never overwrite the original.
    df.to_csv(OUTPUT_PATH, index=False)

    print("\nThree-class review dataset created successfully.")
    print(f"Total emails: {len(df)}")
    print(f"Output: {OUTPUT_PATH}")

    print("\nOriginal binary label distribution:")
    print(df["original_label"].value_counts().sort_index())

    print("\nNew class labels:")
    print("0 = Legitimate")
    print("1 = Spam")
    print("2 = Phishing")

    print("\nAll class labels are currently pending review.")


if __name__ == "__main__":
    main()
