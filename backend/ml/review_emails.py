
from pathlib import Path
import pandas as pd

BASE_DIR = Path(__file__).resolve().parent
DATASET_PATH = BASE_DIR / "dataset" / "three_class_review.csv"

CLASSES = {
    "0": "Legitimate",
    "1": "Spam",
    "2": "Phishing"
}


def load_dataset():
    if not DATASET_PATH.exists():
        raise FileNotFoundError(
            f"Dataset not found: {DATASET_PATH}"
        )

    return pd.read_csv(DATASET_PATH)


def save_dataset(df):
    df.to_csv(DATASET_PATH, index=False)


def review_emails():
    df = load_dataset()

    # Find emails that have not been reviewed.
    pending = df[
        df["review_status"].fillna("pending") == "pending"
    ].index.tolist()

    if not pending:
        print("\nAll emails have been reviewed!")
        return

    print("\n===================================")
    print("       PhishGuard Email Review")
    print("===================================")
    print("0 = Legitimate")
    print("1 = Spam")
    print("2 = Phishing")
    print("s = Skip email")
    print("q = Quit review")
    print("===================================\n")

    reviewed_count = len(df) - len(pending)

    for position, index in enumerate(pending, start=1):
        row = df.loc[index]

        print("\n-----------------------------------")
        print(f"Email {position} of {len(pending)} pending")
        print(f"Dataset row: {index + 1}")
        print("-----------------------------------")

        print(f"\nOriginal label: {row['original_label']}")
        print(f"\nSubject:\n{row['subject']}")
        print(f"\nBody:\n{row['body']}")

        while True:
            choice = input(
                "\nClassify [0/1/2], skip [s], quit [q]: "
            ).strip().lower()

            if choice in CLASSES:
                df.at[index, "class_label"] = int(choice)
                df.at[index, "review_status"] = "reviewed"

                save_dataset(df)

                reviewed_count += 1

                print(
                    f"Saved: {CLASSES[choice]} "
                    f"({reviewed_count}/{len(df)})"
                )
                break

            elif choice == "s":
                print("Skipped. You can review this email later.")
                break

            elif choice == "q":
                print("\nReview session stopped.")
                print(f"Total reviewed: {reviewed_count}")
                return

            else:
                print("Invalid choice. Enter 0, 1, 2, s, or q.")

    print("\n===================================")
    print("Review session completed!")
    print(f"Total reviewed: {reviewed_count}")
    print("===================================")


if __name__ == "__main__":
    review_emails()
