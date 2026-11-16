
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
DATASET_DIR = BASE_DIR / "dataset"

VALIDATED_FILE = DATASET_DIR / "three_class_emails_validated.csv"
REVIEW_FILE = DATASET_DIR / "quality_review.csv"

OUTPUT_FILE = DATASET_DIR / "three_class_emails_final.csv"


def normalize(value):
    """Normalize text for reliable matching."""
    if pd.isna(value):
        return ""

    return " ".join(str(value).lower().split())


def main():

    print("Loading datasets...")

    original = pd.read_csv(VALIDATED_FILE).fillna("")
    review = pd.read_csv(REVIEW_FILE).fillna("")

    original["label"] = pd.to_numeric(
        original["label"],
        errors="raise"
    ).astype(int)

    # Ignore completely blank review rows.
    review = review[
        review["text"].astype(str).str.strip() != ""
    ].copy()

    # Validate review decisions.
    valid_labels = {"0", "1", "2", "exclude"}

    review["review_label"] = (
        review["review_label"].astype(str).str.strip()
    )

    invalid = review[
        ~review["review_label"].isin(valid_labels)
    ]

    if not invalid.empty:
        raise ValueError(
            "Invalid or missing review labels found."
        )

    # Create matching keys.
    original["_match_key"] = (
        original["source"].map(normalize)
        + "||"
        + original["text"].map(normalize)
    )

    review["_match_key"] = (
        review["source"].map(normalize)
        + "||"
        + review["text"].map(normalize)
    )

    # Ensure review records match exactly one dataset record.
    original_counts = original["_match_key"].value_counts()

    review_counts = review["_match_key"].value_counts()

    duplicates = review_counts[review_counts > 1]

    if not duplicates.empty:
        raise ValueError(
            "Duplicate review matching keys found. "
            "Resolve them before applying corrections."
        )

    unmatched = review[
        ~review["_match_key"].isin(original_counts.index)
    ]

    if not unmatched.empty:
        raise ValueError(
            f"{len(unmatched)} reviewed emails could not be matched. "
            "No output dataset was created."
        )

    ambiguous = review[
        review["_match_key"].map(original_counts) != 1
    ]

    if not ambiguous.empty:
        raise ValueError(
            f"{len(ambiguous)} reviewed emails match multiple "
            "dataset records. No output dataset was created."
        )

    # Apply reviewed labels.
    corrections = dict(
        zip(
            review["_match_key"],
            review["review_label"]
        )
    )

    final = original.copy()

    final["_review_decision"] = (
        final["_match_key"].map(corrections)
    )

    # Remove records explicitly marked for exclusion.
    excluded = final[
        final["_review_decision"] == "exclude"
    ]

    final = final[
        final["_review_decision"] != "exclude"
    ].copy()

    # Apply the reviewed numeric labels.
    reviewed_mask = final["_review_decision"].isin(
        ["0", "1", "2"]
    )

    final.loc[reviewed_mask, "label"] = (
        final.loc[reviewed_mask, "_review_decision"]
        .astype(int)
    )

    # Remove temporary columns.
    final.drop(
        columns=["_match_key", "_review_decision"],
        inplace=True
    )

    # Save separately; do not overwrite the original.
    final.to_csv(OUTPUT_FILE, index=False)

    print("\nDataset preparation successful.")

    print("Original records:", len(original))
    print("Reviewed records:", len(review))
    print("Excluded records:", len(excluded))
    print("Final records:", len(final))

    print("\nFinal class distribution:")

    print(
        final["label"]
        .value_counts()
        .sort_index()
        .rename(index={
            0: "Legitimate",
            1: "Spam",
            2: "Phishing"
        })
    )

    print("\nSaved to:", OUTPUT_FILE)


if __name__ == "__main__":
    main()
