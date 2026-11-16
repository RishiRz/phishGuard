
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

INPUT = BASE_DIR / "dataset" / "three_class_emails_validated.csv"
OUTPUT = BASE_DIR / "dataset" / "quality_review.csv"

df = pd.read_csv(INPUT)

class_names = {
    0: "Legitimate",
    1: "Spam",
    2: "Phishing"
}

samples = []

for label, name in class_names.items():
    class_df = df[df["label"] == label]

    selected = class_df.sample(
        n=min(50, len(class_df)),
        random_state=42
    ).copy()

    selected["class_name"] = name
    selected["review_label"] = ""
    selected["review_notes"] = ""

    samples.append(selected)

review_df = pd.concat(samples, ignore_index=True)

review_df.to_csv(OUTPUT, index=False)

print("Quality review file created!")
print("Total samples:", len(review_df))
print("Output:", OUTPUT)

print("\nSamples per class:")
print(review_df["class_name"].value_counts())
