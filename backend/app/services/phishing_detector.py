
from .url_analyzer import analyze_urls
from ml.predictor import predict_email


# ==========================================
# Hybrid scoring weights
# ==========================================
# Rule analysis        40%
# URL analysis         20%
# Header analysis      10%
# ML malicious signal  30%
#
# Total                100%

RULE_WEIGHT = 0.40
URL_WEIGHT = 0.20
HEADER_WEIGHT = 0.10
ML_WEIGHT = 0.30


# ==========================================
# Detection keywords
# ==========================================

URGENT_WORDS = [
    "urgent",
    "immediately",
    "action required",
    "account suspended",
    "account locked",
    "verify now",
    "act now",
    "within 24 hours",
    "final warning",
]


CREDENTIAL_WORDS = [
    "password",
    "login",
    "username",
    "credential",
    "verify your account",
    "confirm your identity",
    "enter your password",
]


FINANCIAL_WORDS = [
    "bank account",
    "credit card",
    "debit card",
    "payment",
    "wire transfer",
    "transaction",
    "invoice",
]


# ==========================================
# Rule Analysis
# ==========================================

def analyze_rules(text: str) -> tuple[int, list[str]]:

    score = 0
    reasons = []

    text = text.lower()

    if any(word in text for word in URGENT_WORDS):
        score += 35
        reasons.append(
            "Urgency or pressure tactics detected."
        )

    if any(word in text for word in CREDENTIAL_WORDS):
        score += 40
        reasons.append(
            "Possible credential or account "
            "verification request detected."
        )

    if any(word in text for word in FINANCIAL_WORDS):
        score += 25
        reasons.append(
            "Financial or payment-related content detected."
        )

    return min(score, 100), reasons


# ==========================================
# URL Analysis
# ==========================================

def analyze_url_risk(
    url_results: list[dict],
) -> tuple[int, list[str]]:

    if not url_results:
        return 0, []

    highest = 0
    reasons = []

    for result in url_results:

        risk_score = result.get("risk_score", 0)
        risk_level = result.get("risk_level", "LOW")
        hostname = result.get("hostname", "unknown")

        highest = max(highest, risk_score)

        if risk_level == "HIGH":
            reasons.append(
                f"High-risk URL detected: {hostname}"
            )

        elif risk_level == "MEDIUM":
            reasons.append(
                f"Suspicious URL detected: {hostname}"
            )

    return min(highest, 100), reasons


# ==========================================
# Header Analysis
# ==========================================

def analyze_header_risk(
    header_analysis: dict | None,
) -> tuple[int, list[str]]:

    if not header_analysis:
        return 0, []

    authentication = header_analysis.get(
        "authentication",
        {},
    )

    issues = header_analysis.get(
        "issues",
        {},
    )

    score = 0
    reasons = []

    authentication_rules = [
        ("spf", 30, 10),
        ("dkim", 25, 0),
        ("dmarc", 25, 0),
    ]

    for method, fail_points, softfail_points in authentication_rules:

        status = (
            authentication
            .get(method, {})
            .get("status", "UNKNOWN")
        )

        if status == "FAIL":
            score += fail_points
            reasons.append(
                f"{method.upper()} authentication failed."
            )

        elif status == "SOFTFAIL" and softfail_points:
            score += softfail_points
            reasons.append(
                f"{method.upper()} authentication softfailed."
            )

    if issues.get("reply_to_mismatch"):
        score += 10
        reasons.append(
            "Reply-To domain differs from sender domain."
        )

    if issues.get("return_path_mismatch"):
        score += 10
        reasons.append(
            "Return-Path domain differs from sender domain."
        )

    return min(score, 100), reasons


# ==========================================
# Three-Class ML Analysis
# ==========================================

def analyze_ml_risk(
    text: str,
) -> tuple[int, list[str], dict]:

    """
    Three-class ML analysis.

    Classes:
        0 = Legitimate
        1 = Spam
        2 = Phishing

    ML risk score:
        Spam probability + Phishing probability

    This represents the model's combined
    non-legitimate email probability.
    """

    ml_result = predict_email(text)

    spam_probability = float(
        ml_result.get("spam_probability", 0)
    )

    phishing_probability = float(
        ml_result.get("phishing_probability", 0)
    )

    malicious_probability = float(
        ml_result.get(
            "malicious_probability",
            spam_probability + phishing_probability,
        )
    )

    # Combined spam and phishing probability.
    score = int(round(malicious_probability))
    score = max(0, min(score, 100))

    prediction = ml_result.get(
        "prediction",
        "Unknown",
    )

    confidence = ml_result.get(
        "confidence",
        0,
    )

    reasons = []

    if prediction == "Phishing":
        reasons.append(
            "Machine learning model classified "
            f"the email as phishing with {confidence}% confidence."
        )

    elif prediction == "Spam":
        reasons.append(
            "Machine learning model classified "
            f"the email as spam with {confidence}% confidence."
        )

    elif prediction == "Legitimate":
        reasons.append(
            "Machine learning model classified "
            "the email as legitimate."
        )

    else:
        reasons.append(
            "Machine learning model could not classify the email."
        )

    return score, reasons, ml_result


# ==========================================
# Main Email Analysis
# ==========================================

def analyze_email(
    sender: str,
    subject: str,
    body: str,
    header_analysis: dict | None = None,
):

    # ==========================================
    # Combine email content
    # ==========================================

    text = (
        f"Subject: {subject}\n"
        f"Body: {body}"
    )

    normalized_text = text.lower()

    # ==========================================
    # 1. Rule Analysis
    # ==========================================

    rule_score, rule_reasons = analyze_rules(
        normalized_text
    )

    # ==========================================
    # 2. URL Analysis
    # ==========================================

    url_results = analyze_urls(text)

    url_score, url_reasons = analyze_url_risk(
        url_results
    )

    # ==========================================
    # 3. Header Analysis
    # ==========================================

    header_score, header_reasons = analyze_header_risk(
        header_analysis
    )

    # ==========================================
    # 4. ML Analysis
    # ==========================================

    ml_score, ml_reasons, ml_result = analyze_ml_risk(
        normalized_text
    )

    # ==========================================
    # 5. Hybrid Risk Score
    # ==========================================

    weighted_score = (
        rule_score * RULE_WEIGHT
        + url_score * URL_WEIGHT
        + header_score * HEADER_WEIGHT
        + ml_score * ML_WEIGHT
    )

    score = int(
        min(
            round(weighted_score),
            100,
        )
    )

    # ==========================================
    # 6. Classification
    # ==========================================

    if score >= 70:
        classification = "Phishing"
        risk_level = "HIGH"

    elif score >= 40:
        classification = "Suspicious"
        risk_level = "MEDIUM"

    else:
        classification = "Likely Legitimate"
        risk_level = "LOW"

    # ==========================================
    # 7. Combine Reasons
    # ==========================================

    reasons = (
        rule_reasons
        + url_reasons
        + header_reasons
        + ml_reasons
    )

    if not reasons:
        reasons.append(
            "No obvious phishing indicators "
            "were detected."
        )

    reasons = list(dict.fromkeys(reasons))

    # ==========================================
    # 8. Return Result
    # ==========================================

    return {

        "classification": classification,

        "risk_score": score,

        "risk_level": risk_level,

        "reasons": reasons,

        "urls": url_results,

        # -----------------------------
        # Three-class ML result
        # -----------------------------

        "ml_analysis": {

            "prediction": ml_result.get(
                "prediction"
            ),

            "confidence": ml_result.get(
                "confidence"
            ),

            "spam_probability": ml_result.get(
                "spam_probability"
            ),

            "phishing_probability": ml_result.get(
                "phishing_probability"
            ),

            "malicious_probability": ml_result.get(
                "malicious_probability"
            ),

            "probabilities": ml_result.get(
                "probabilities"
            ),
        },

        # -----------------------------
        # Score breakdown
        # -----------------------------

        "score_breakdown": {

            "rules": {
                "score": rule_score,
                "weight": int(RULE_WEIGHT * 100),
                "contribution": round(
                    rule_score * RULE_WEIGHT,
                    2,
                ),
            },

            "urls": {
                "score": url_score,
                "weight": int(URL_WEIGHT * 100),
                "contribution": round(
                    url_score * URL_WEIGHT,
                    2,
                ),
            },

            "headers": {
                "score": header_score,
                "weight": int(HEADER_WEIGHT * 100),
                "contribution": round(
                    header_score * HEADER_WEIGHT,
                    2,
                ),
            },

            "ml": {
                "score": ml_score,
                "weight": int(ML_WEIGHT * 100),
                "contribution": round(
                    ml_score * ML_WEIGHT,
                    2,
                ),
            },
        },
    }
