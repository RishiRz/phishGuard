
import pandas as pd
from pathlib import Path

DATASET_PATH = (
    Path(__file__).resolve().parent
    / "dataset"
    / "three_class_emails.csv"
)

df = pd.read_csv(DATASET_PATH)

class_names = {
    0: "Legitimate",
    1: "Spam",
    2: "Phishing"
}

print("\n========== DATASET INSPECTION ==========")

print("\nDataset shape:")
print(df.shape)

print("\nClass distribution:")
print(df["label"].value_counts().sort_index())

print("\nSource distribution:")
print(pd.crosstab(df["source"], df["label"]))

print("\nMissing values:")
print(df[["subject", "body", "text", "label"]].isnull().sum())

print("\nText length statistics:")
print(df["text"].str.len().describe())

print("\n========== SAMPLE EMAILS ==========")

for label, name in class_names.items():
    samples = df[df["label"] == label].sample(
        min(3, len(df[df["label"] == label])),
        random_state=42
    )

    print(f"\n--- {name} ---")

    for _, row in samples.iterrows():
        print("Subject:", row["subject"])
        print("Source:", row["source"])
        print("Body:", str(row["body"])[:300])
        print("-" * 50)

print("\n========== MISSING BODY ANALYSIS ==========")

df["body_missing"] = (
    df["body"].isna()
    | df["body"].astype(str).str.strip().isin(["", "nan", "None"])
)

print(
    df.groupby("source")["body_missing"]
    .agg(["sum", "count"])
    .to_string()
)

print("\nMissing body count by class:")
print(df.groupby("label")["body_missing"].sum())