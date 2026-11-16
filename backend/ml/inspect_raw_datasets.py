
from pathlib import Path
import mailbox

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "dataset" / "raw"

print("\n========== NAZARIO DATASET ==========")

nazario_dir = RAW_DIR / "nazario"
nazario_total = 0

for file in sorted(nazario_dir.glob("*.mbox")):
    mbox = None

    try:
        mbox = mailbox.mbox(str(file))
        count = len(mbox)

        nazario_total += count
        print(f"{file.name}: {count} emails")

    except Exception as error:
        print(f"{file.name}: ERROR - {error}")

    finally:
        if mbox is not None:
            mbox.close()

print(f"Nazario total: {nazario_total}")

print("\n====== SPAMASSASSIN DATASET ======")

spam_dir = RAW_DIR / "spamassassin"
spam_total = 0

for folder in sorted(spam_dir.iterdir()):
    if folder.is_dir():
        files = [f for f in folder.rglob("*") if f.is_file()]
        count = len(files)

        spam_total += count
        print(f"{folder.name}: {count} files")

print(f"SpamAssassin total: {spam_total}")

print("\n===================================")
