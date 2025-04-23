from pydantic import BaseModel

class BodyInput(BaseModel):
    body: str

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"
