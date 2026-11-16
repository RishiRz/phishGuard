
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "cleaned_emails.csv"

if not DATASET_PATH.exists():
    raise FileNotFoundError(f"Dataset not found: {DATASET_PATH}")

df = pd.read_csv(DATASET_PATH)

print("\n========== DATASET AUDIT ==========")
print("\nColumns:", df.columns.tolist())
print("\nDataset shape:", df.shape)

print("\nMissing values:")
print(df.isnull().sum())

print("\nLabel distribution:")
print(df["label"].value_counts(dropna=False))

print("\nUnique labels:")
print(sorted(df["label"].dropna().unique()))

print("\nDuplicate emails:")
print(df.duplicated(subset=["text"]).sum())

print("\nEmail length statistics:")
print(df["text"].astype(str).str.len().describe())

print("\nSample emails:")
for label, group in df.groupby("label"):
    print(f"\nLabel {label}:")
    for sample in group["text"].head(2):
        print(str(sample)[:300])
        print("-" * 40)

print("\n========== AUDIT COMPLETE ==========")
