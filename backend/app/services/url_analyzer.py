import re
from urllib.parse import urlparse

import tldextract


URL_PATTERN = re.compile(
    r"https?://[^\s<>'\"]+",
    re.IGNORECASE,
)


SHORTENERS = {
    "bit.ly",
    "tinyurl.com",
    "t.co",
    "goo.gl",
    "ow.ly",
    "is.gd",
    "buff.ly",
    "cutt.ly",
}


SUSPICIOUS_TLDS = {
    "zip",
    "click",
    "country",
    "gq",
    "tk",
    "top",
    "xyz",
}


def extract_urls(text: str) -> list[str]:
    matches = URL_PATTERN.findall(text)

    cleaned = []

    for url in matches:
        url = url.rstrip(".,!?;:)")

        if url not in cleaned:
            cleaned.append(url)

    return cleaned


def analyze_url(url: str) -> dict:
    parsed = urlparse(url)

    hostname = parsed.hostname or ""

    extracted = tldextract.extract(
        hostname
    )

    domain = extracted.registered_domain
    suffix = extracted.suffix

    score = 0
    reasons = []

    # HTTP
    if parsed.scheme.lower() == "http":
        score += 15

        reasons.append(
            "URL does not use HTTPS."
        )

    # IP address
    ip_pattern = (
        r"^(?:\d{1,3}\.){3}\d{1,3}$"
    )

    if re.match(ip_pattern, hostname):
        score += 30

        reasons.append(
            "URL uses an IP address instead of a domain name."
        )

    # URL shortener
    if domain.lower() in SHORTENERS:
        score += 25

        reasons.append(
            "URL uses a known URL-shortening service."
        )

    # Suspicious TLD
    if suffix.lower() in SUSPICIOUS_TLDS:
        score += 15

        reasons.append(
            f"Domain uses a potentially suspicious TLD: .{suffix}"
        )

    # Very long URL
    if len(url) > 150:
        score += 10

        reasons.append(
            "URL is unusually long."
        )

    # @ symbol
    if "@" in parsed.netloc:
        score += 30

        reasons.append(
            "URL contains an @ symbol that may obscure the destination."
        )

    # Excessive subdomains
    subdomain_parts = [
        part
        for part in extracted.subdomain.split(".")
        if part
    ]

    if len(subdomain_parts) >= 3:
        score += 15

        reasons.append(
            "URL contains an unusually deep subdomain structure."
        )

    # Punycode
    if "xn--" in hostname.lower():
        score += 20

        reasons.append(
            "Internationalized/Punycode domain detected."
        )

    score = min(score, 100)

    if score >= 60:
        risk = "HIGH"

    elif score >= 30:
        risk = "MEDIUM"

    else:
        risk = "LOW"

    return {
        "url": url,
        "hostname": hostname,
        "domain": domain,
        "risk_score": score,
        "risk_level": risk,
        "reasons": reasons,
    }


def analyze_urls(text: str) -> list[dict]:
    urls = extract_urls(text)

    return [
        analyze_url(url)
        for url in urls
    ]