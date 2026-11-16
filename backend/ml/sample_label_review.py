
import pandas as pd
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
DATASET = BASE_DIR / "dataset" / "three_class_emails_validated.csv"

df = pd.read_csv(DATASET)

# Inspect SpamAssassin spam emails
spam = df[df["label"] == 1]

print("\n========== SPAM CLASS REVIEW ==========")

samples = spam.sample(
    min(15, len(spam)),
    random_state=42
)

for index, row in samples.iterrows():
    print("\nSubject:", row["subject"])
    print("Source:", row["source"])
    print("Email preview:", str(row["body"])[:500])
    print("-" * 70)

# Inspect phishing emails
phishing = df[df["label"] == 2]

print("\n========== PHISHING CLASS REVIEW ==========")

samples = phishing.sample(
    min(10, len(phishing)),
    random_state=42
)

for index, row in samples.iterrows():
    print("\nSubject:", row["subject"])
    print("Email preview:", str(row["body"])[:400])
    print("-" * 70)
