
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET = BASE_DIR / "dataset" / "emails.csv"

df = pd.read_csv(DATASET)

for label in sorted(df["label"].dropna().unique()):
    samples = df[df["label"] == label].sample(
        n=min(10, len(df[df["label"] == label])),
        random_state=42
    )

    print(f"\n{'=' * 60}")
    print(f"LABEL: {label}")
    print(f"{'=' * 60}")

    for index, row in samples.iterrows():
        print("\nSUBJECT:", str(row["subject"])[:150])
        print("BODY:", str(row["body"])[:500])
        print("-" * 60)
