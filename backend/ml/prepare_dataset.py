import re

import pandas as pd

from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
RAW_DATASET_PATH = BASE_DIR / "dataset" / "emails.csv"
CLEAN_DATASET_PATH = BASE_DIR / "dataset" / "cleaned_emails.csv"


# Columns required to build a usable training record
REQUIRED_COLUMNS = ["subject", "body", "label"]

# Records shorter than this are not informative for training
MIN_TEXT_LENGTH = 20


HTML_TAG_PATTERN = re.compile(r"<[^>]+>")
WHITESPACE_PATTERN = re.compile(r"\s+")


def clean_text(value: object) -> str:
    """
    Normalize a raw text value into a single clean line.

    1. Coerce to string
    2. Strip HTML tags
    3. Collapse all whitespace

    URLs are intentionally preserved: links are one of the
    strongest phishing signals and are used by the model,
    the URL analyzer and the rule engine.
    """

    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""

    text = str(value)

    text = HTML_TAG_PATTERN.sub(" ", text)
    text = WHITESPACE_PATTERN.sub(" ", text)

    return text.strip()


def clean_dataset(df: pd.DataFrame) -> pd.DataFrame:
    """
    Clean the raw email dataset and return a training-ready frame
    with the columns: subject, body, text, label.
    """ 
    missing = [
        column
        for column in REQUIRED_COLUMNS
        if column not in df.columns
    ]

    if missing:
        raise ValueError(
            "Dataset is missing required columns: "
            f"{', '.join(missing)}"
        )

    print(f"Rows in raw dataset: {len(df)}")

    # -----------------------------------------
    # 1. Drop rows without the required fields
    # -----------------------------------------

    df = df.dropna(subset=REQUIRED_COLUMNS)

    print(f"Rows after dropping missing values: {len(df)}")

    # -----------------------------------------
    # 2. Clean subject and body text
    # -----------------------------------------

    df = df.copy()

    df["subject"] = df["subject"].map(clean_text)
    df["body"] = df["body"].map(clean_text)

    # -----------------------------------------
    # 3. Drop rows with empty subject and body
    # -----------------------------------------

    empty_rows = (df["subject"] == "") & (df["body"] == "")

    df = df[~empty_rows]

    print(f"Rows after dropping empty emails: {len(df)}")

    # -----------------------------------------
    # 4. Combine subject and body into one field
    # -----------------------------------------

    df["text"] = (
        df["subject"] + " " + df["body"]
    ).map(lambda text: WHITESPACE_PATTERN.sub(" ", text).strip())

    # -----------------------------------------
    # 5. Drop short / non-informative records
    # -----------------------------------------

    df = df[df["text"].str.len() >= MIN_TEXT_LENGTH]

    print(
        "Rows after dropping records shorter than "
        f"{MIN_TEXT_LENGTH} characters: {len(df)}"
    )

    # -----------------------------------------
    # 6. Drop duplicated emails
    # -----------------------------------------

    df = df.drop_duplicates(subset=["text"])

    print(f"Rows after removing duplicates: {len(df)}")

    # -----------------------------------------
    # 7. Normalize the label column
    # -----------------------------------------

    df["label"] = pd.to_numeric(
        df["label"],
        errors="coerce",
    )

    df = df.dropna(subset=["label"])

    df["label"] = df["label"].astype(int)

    # Keep only the binary classes 0 and 1
    df = df[df["label"].isin([0, 1])]

    print(f"Rows after label cleanup: {len(df)}")

    return df


def main() -> None:

    if not RAW_DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Raw dataset not found: {RAW_DATASET_PATH}"
        )

    df = pd.read_csv(RAW_DATASET_PATH)

    cleaned = clean_dataset(df)

    # -----------------------------------------
    # Class distribution
    # -----------------------------------------

    legitimate = int((cleaned["label"] == 0).sum())
    spam = int((cleaned["label"] == 1).sum())

    # -----------------------------------------
    # Save cleaned dataset
    # -----------------------------------------

    cleaned = cleaned[
        ["subject", "body", "text", "label"]
    ]

    cleaned.to_csv(
        CLEAN_DATASET_PATH,
        index=False,
    )

    # -----------------------------------------
    # Report
    # -----------------------------------------

    print("\n==============================")
    print("PhishGuard Dataset Preparation")
    print("==============================")

    print(f"\nFinal rows: {len(cleaned)}")
    print(f"Legitimate (0): {legitimate}")
    print(f"Spam (1): {spam}")

    print("\nSaved cleaned dataset:")
    print(CLEAN_DATASET_PATH)


if __name__ == "__main__":
    main()
