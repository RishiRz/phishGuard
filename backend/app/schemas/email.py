from pydantic import BaseModel


class EmailAnalysisRequest(BaseModel):
    sender: str = ""
    subject: str = ""
    body: str