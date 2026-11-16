from email import policy
from email.parser import BytesParser
from email.message import Message
from typing import Any


def extract_message_body(message: Message) -> str:
    """
    Extract readable text from an email message.

    Preference:
    1. text/plain
    2. text/html converted to text
    """

    plain_parts = []
    html_parts = []

    if message.is_multipart():
        for part in message.walk():
            content_type = part.get_content_type()

            if content_type == "text/plain":
                try:
                    plain_parts.append(part.get_content())
                except Exception:
                    pass

            elif content_type == "text/html":
                try:
                    html_parts.append(part.get_content())
                except Exception:
                    pass

    else:
        content_type = message.get_content_type()

        try:
            content = message.get_content()
        except Exception:
            content = ""

        if content_type == "text/plain":
            plain_parts.append(content)

        elif content_type == "text/html":
            html_parts.append(content)

    if plain_parts:
        return "\n".join(plain_parts).strip()

    if html_parts:
        from bs4 import BeautifulSoup

        soup = BeautifulSoup(
            "\n".join(html_parts),
            "html.parser",
        )

        return soup.get_text(
            separator=" ",
            strip=True,
        )

    return ""


def extract_attachments(message: Message) -> list[dict[str, Any]]:
    attachments = []

    for part in message.walk():
        filename = part.get_filename()

        if filename:
            attachments.append(
                {
                    "filename": filename,
                    "content_type": part.get_content_type(),
                    "size": len(part.get_payload(decode=True) or b""),
                }
            )

    return attachments


def parse_eml(file_bytes: bytes) -> dict[str, Any]:
    """
    Parse an .eml file and extract useful information.
    """

    message = BytesParser(
        policy=policy.default
    ).parsebytes(file_bytes)

    headers = {}

    for key, value in message.items():
        if key not in headers:
            headers[key] = []

        headers[key].append(str(value))

    return {
        "sender": str(message.get("From", "")),
        "recipient": str(message.get("To", "")),
        "reply_to": str(message.get("Reply-To", "")),
        "subject": str(message.get("Subject", "")),
        "date": str(message.get("Date", "")),
        "message_id": str(message.get("Message-ID", "")),
        "return_path": str(message.get("Return-Path", "")),
        "body": extract_message_body(message),
        "attachments": extract_attachments(message),
        "headers": headers,
    }