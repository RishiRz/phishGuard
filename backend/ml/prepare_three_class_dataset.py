
from pathlib import Path
import mailbox
import hashlib
import json
import pandas as pd

from email import policy
from email.parser import BytesParser

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "dataset" / "raw"

OUTPUT_PATH = BASE_DIR / "dataset" / "three_class_emails.csv"
REPORT_PATH = BASE_DIR / "dataset" / "three_class_report.json"

SPAMASSASSIN_LABELS = {
    "20030228_easy_ham": 0,
    "20030228_easy_ham_2": 0,
    "20030228_spam": 1,
    "20050311_spam_2": 1,
}

LABEL_NAMES = {
    0: "Legitimate",
    1: "Spam",
    2: "Phishing",
}


def extract_body(message):
    parsed = BytesParser(policy=policy.default).parsebytes(
        message.as_bytes()
    )

    parts = []

    if parsed.is_multipart():
        for part in parsed.walk():
            if part.get_content_maintype() == "multipart":
                continue

            if part.get_content_disposition() == "attachment":
                continue

            if part.get_content_type() in (
                "text/plain",
                "text/html"
            ):
                try:
                    content = part.get_content()
                    if content:
                        parts.append(str(content))
                except Exception:
                    continue
    else:
        try:
            content = parsed.get_content()
            if content:
                parts.append(str(content))
        except Exception:
            pass

    return "\n".join(parts).strip()


def make_record(message, label, source):
    subject = str(message.get("Subject", "") or "").strip()
    body = extract_body(message)

    text = f"{subject}\n{body}".strip()

    if len(text) < 20:
        return None

    return {
        "subject": subject,
        "body": body,
        "text": text,
        "label": label,
        "source": source,
    }


def record_hash(record):
    normalized = record["text"].lower().strip()
    return hashlib.sha256(
        normalized.encode("utf-8", errors="ignore")
    ).hexdigest()


def parse_spamassassin():
    records = []
    spam_dir = RAW_DIR / "spamassassin"

    for folder_name, label in SPAMASSASSIN_LABELS.items():
        folder = spam_dir / folder_name

        if not folder.exists():
            print(f"Missing folder: {folder}")
            continue

        files = [
            file for file in folder.rglob("*")
            if file.is_file()
        ]

        successful = 0
        failed = 0

        for file in files:
            try:
                with file.open("rb") as f:
                    message = BytesParser(
                        policy=policy.default
                    ).parse(f)

                record = make_record(
                    message, label, f"SpamAssassin/{folder_name}"
                )

                if record:
                    records.append(record)
                    successful += 1

            except Exception:
                failed += 1

        print(
            f"{folder_name}: "
            f"{successful} parsed, {failed} failed"
        )

    return records


def parse_nazario():
    records = []
    nazario_dir = RAW_DIR / "nazario"

    for file in sorted(nazario_dir.glob("*.mbox")):
        mbox = None
        successful = 0
        failed = 0

        try:
            mbox = mailbox.mbox(str(file))

            for message in mbox:
                try:
                    record = make_record(
                        message, 2, f"Nazario/{file.name}"
                    )

                    if record:
                        records.append(record)
                        successful += 1

                except Exception:
                    failed += 1

        except Exception as error:
            print(f"Error reading {file.name}: {error}")

        finally:
            if mbox is not None:
                mbox.close()

        print(
            f"{file.name}: "
            f"{successful} parsed, {failed} failed"
        )

    return records


def main():
    print("\nParsing SpamAssassin...")
    spam_records = parse_spamassassin()

    print("\nParsing Nazario...")
    phishing_records = parse_nazario()

    records = spam_records + phishing_records

    if not records:
        raise RuntimeError("No valid emails were extracted.")

    df = pd.DataFrame(records)

    before = len(df)

    df["dedup_hash"] = df.apply(
        lambda row: record_hash(row), axis=1
    )

    # Keep one copy of duplicate email text.
    # Conflicting labels are excluded for manual investigation.
    label_counts = df.groupby("dedup_hash")["label"].nunique()
    conflicting_hashes = set(
        label_counts[label_counts > 1].index
    )

    conflicts = df[
        df["dedup_hash"].isin(conflicting_hashes)
    ].copy()

    df = df[
        ~df["dedup_hash"].isin(conflicting_hashes)
    ].drop_duplicates(
        subset="dedup_hash", keep="first"
    )

    duplicates_removed = before - len(df) - len(conflicts)

    df = df.drop(columns=["dedup_hash"])
    df = df.sample(frac=1, random_state=42).reset_index(drop=True)

    df.to_csv(OUTPUT_PATH, index=False)

    report = {
        "raw_records": before,
        "usable_unique_records": len(df),
        "duplicates_removed": duplicates_removed,
        "conflicting_records_excluded": len(conflicts),
        "class_distribution": {
            LABEL_NAMES[int(label)]: int(count)
            for label, count in df["label"].value_counts().items()
        },
        "sources": {
            str(source): int(count)
            for source, count in df["source"].value_counts().items()
        },
    }

    REPORT_PATH.write_text(
        json.dumps(report, indent=4),
        encoding="utf-8"
    )

    if not conflicts.empty:
        conflicts.to_csv(
            BASE_DIR / "dataset" / "conflicting_emails.csv",
            index=False
        )

    print("\n========== DATASET SUMMARY ==========")
    print(df["label"].value_counts().sort_index())
    print(f"\nTotal unique emails: {len(df)}")
    print(f"Output: {OUTPUT_PATH}")
    print(f"Report: {REPORT_PATH}")
    print("=====================================")


if __name__ == "__main__":
    main()
