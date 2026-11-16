
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
INPUT_FILE = BASE_DIR / "dataset" / "three_class_emails.csv"
OUTPUT_FILE = BASE_DIR / "dataset" / "three_class_emails_validated.csv"
QUARANTINE_FILE = BASE_DIR / "dataset" / "emails_without_body.csv"

df = pd.read_csv(INPUT_FILE)

# Normalize missing values
for column in ["subject", "body"]:
    df[column] = df[column].fillna("").astype(str).str.strip()

# Remove records without meaningful body content
missing_body = df[
    df["body"].str.strip().eq("")
    | df["body"].str.strip().str.lower().isin(["nan", "none"])
].copy()

valid_df = df.drop(missing_body.index).copy()

# Rebuild combined text
valid_df["text"] = (
    valid_df["subject"] + " " + valid_df["body"]
).str.strip()

# Remove empty text
valid_df = valid_df[
    valid_df["text"].str.len() >= 20
].copy()

# Save validated dataset and quarantined records
valid_df.to_csv(OUTPUT_FILE, index=False)
missing_body.to_csv(QUARANTINE_FILE, index=False)

print("\n========== VALIDATION SUMMARY ==========")
print("Original records:", len(df))
print("Valid records:", len(valid_df))
print("Quarantined records:", len(missing_body))

print("\nClass distribution:")
print(valid_df["label"].value_counts().sort_index())

print("\nSaved validated dataset:")
print(OUTPUT_FILE)

print("\nSaved quarantined records:")
print(QUARANTINE_FILE)
