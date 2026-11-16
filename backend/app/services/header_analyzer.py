def get_header_value(
    headers: dict[str, list[str]],
    name: str,
) -> list[str]:
    """
    Find a header case-insensitively.
    """

    target = name.lower()

    for key, values in headers.items():
        if key.lower() == target:
            return values

    return []


def analyze_authentication_headers(
    headers: dict[str, list[str]],
) -> dict:
    """
    Analyze SPF, DKIM and DMARC results from
    Authentication-Results and related headers.
    """

    authentication_results = get_header_value(
        headers,
        "Authentication-Results",
    )

    received_spf = get_header_value(
        headers,
        "Received-SPF",
    )

    auth_text = " ".join(
        authentication_results
    ).lower()

    spf_headers = " ".join(
        received_spf
    ).lower()

    result = {
        "spf": {
            "status": "UNKNOWN",
            "evidence": [],
        },
        "dkim": {
            "status": "UNKNOWN",
            "evidence": [],
        },
        "dmarc": {
            "status": "UNKNOWN",
            "evidence": [],
        },
    }

    # SPF
    if "spf=pass" in auth_text or "pass" in spf_headers:
        result["spf"]["status"] = "PASS"
        result["spf"]["evidence"].append(
            "SPF pass result detected."
        )

    elif "spf=fail" in auth_text or "fail" in spf_headers:
        result["spf"]["status"] = "FAIL"
        result["spf"]["evidence"].append(
            "SPF failure detected."
        )

    elif "spf=softfail" in auth_text:
        result["spf"]["status"] = "SOFTFAIL"
        result["spf"]["evidence"].append(
            "SPF softfail detected."
        )

    # DKIM
    if "dkim=pass" in auth_text:
        result["dkim"]["status"] = "PASS"
        result["dkim"]["evidence"].append(
            "DKIM pass result detected."
        )

    elif "dkim=fail" in auth_text:
        result["dkim"]["status"] = "FAIL"
        result["dkim"]["evidence"].append(
            "DKIM failure detected."
        )

    # DMARC
    if "dmarc=pass" in auth_text:
        result["dmarc"]["status"] = "PASS"
        result["dmarc"]["evidence"].append(
            "DMARC pass result detected."
        )

    elif "dmarc=fail" in auth_text:
        result["dmarc"]["status"] = "FAIL"
        result["dmarc"]["evidence"].append(
            "DMARC failure detected."
        )

    return result


def analyze_headers(
    headers: dict[str, list[str]],
    sender: str,
    reply_to: str,
    return_path: str,
) -> dict:

    authentication = analyze_authentication_headers(
        headers
    )

    warnings = []

    # Structured signals used by the hybrid risk score
    issues = {
        "reply_to_mismatch": False,
        "return_path_mismatch": False,
    }

    # Reply-To mismatch
    if sender and reply_to:
        sender_domain = extract_domain(sender)
        reply_domain = extract_domain(reply_to)

        if (
            sender_domain
            and reply_domain
            and sender_domain != reply_domain
        ):
            issues["reply_to_mismatch"] = True

            warnings.append(
                "Reply-To domain differs from sender domain."
            )

    # Return-Path mismatch
    if sender and return_path:
        sender_domain = extract_domain(sender)
        return_domain = extract_domain(return_path)

        if (
            sender_domain
            and return_domain
            and sender_domain != return_domain
        ):
            issues["return_path_mismatch"] = True

            warnings.append(
                "Return-Path domain differs from sender domain."
            )

    # Authentication failures
    for method in ["spf", "dkim", "dmarc"]:
        status = authentication[method]["status"]

        if status == "FAIL":
            warnings.append(
                f"{method.upper()} authentication failed."
            )

    return {
        "authentication": authentication,
        "warnings": warnings,
        "issues": issues,
    }


def extract_domain(email_address: str) -> str:
    """
    Extract domain from:
    user@example.com
    Name <user@example.com>
    """

    email_address = email_address.strip()

    if "<" in email_address and ">" in email_address:
        email_address = (
            email_address
            .split("<", 1)[1]
            .split(">", 1)[0]
        )

    if "@" not in email_address:
        return ""

    return email_address.rsplit("@", 1)[1].lower()