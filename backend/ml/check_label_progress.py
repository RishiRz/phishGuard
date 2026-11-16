
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "three_class_review.csv"

df = pd.read_csv(DATASET_PATH)

print("\n========== PhishGuard Label Progress ==========")

print(f"\nTotal emails: {len(df)}")

print("\nReview status:")
print(df["review_status"].value_counts())

print("\nClass distribution:")

reviewed = df[df["review_status"] == "reviewed"]

if reviewed.empty:
    print("No emails classified yet.")
else:
    counts = (
        reviewed["class_label"]
        .value_counts()
        .reindex([0, 1, 2], fill_value=0)
    )

    print(counts.rename({
        0: "Legitimate",
        1: "Spam",
        2: "Phishing"
    }))

print("\n===============================================")
