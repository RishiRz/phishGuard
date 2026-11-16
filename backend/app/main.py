from fastapi import (
    FastAPI,
    File,
    UploadFile,
    HTTPException,
)

from fastapi.middleware.cors import CORSMiddleware

from app.schemas.email import EmailAnalysisRequest

from app.services.email_parser import (
    parse_eml,
)

from app.services.header_analyzer import (
    analyze_headers,
)

from app.services.phishing_detector import (
    analyze_email,
)


app = FastAPI(
    title="PhishGuard API",
    description="Phishing Email Detection and Threat Analysis API",
    version="1.0.0",
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {
        "message": "PhishGuard API is running"
    }


@app.get("/api/health")
def health_check():
    return {
        "status": "healthy"
    }


# -----------------------------------------
# Analyze pasted email
# -----------------------------------------

@app.post("/api/analyze")
def analyze_email_endpoint(
    email: EmailAnalysisRequest,
):

    result = analyze_email(
        sender=email.sender,
        subject=email.subject,
        body=email.body,
    )

    return result


# -----------------------------------------
# Analyze .eml file
# -----------------------------------------

@app.post("/api/analyze-eml")
async def analyze_eml(
    file: UploadFile = File(...),
):

    filename = file.filename or ""

    if not filename.lower().endswith(".eml"):
        raise HTTPException(
            status_code=400,
            detail="Only .eml files are supported.",
        )

    file_bytes = await file.read()

    # Basic size protection
    if len(file_bytes) > 10 * 1024 * 1024:
        raise HTTPException(
            status_code=413,
            detail="File is too large. Maximum size is 10 MB.",
        )

    try:

        parsed = parse_eml(
            file_bytes
        )

        header_analysis = analyze_headers(
            headers=parsed["headers"],
            sender=parsed["sender"],
            reply_to=parsed["reply_to"],
            return_path=parsed["return_path"],
        )

        detection = analyze_email(
            sender=parsed["sender"],
            subject=parsed["subject"],
            body=parsed["body"],
            header_analysis=header_analysis,
        )

        return {
            "email": {
                "sender": parsed["sender"],
                "recipient": parsed["recipient"],
                "reply_to": parsed["reply_to"],
                "subject": parsed["subject"],
                "date": parsed["date"],
                "message_id": parsed["message_id"],
                "return_path": parsed["return_path"],
            },
            "headers": header_analysis,
            "attachments": parsed[
                "attachments"
            ],
            "analysis": detection,
        }

    except Exception as error:

        raise HTTPException(
            status_code=400,
            detail=f"Unable to parse email: {str(error)}",
        )