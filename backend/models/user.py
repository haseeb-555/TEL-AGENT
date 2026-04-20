from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class User(BaseModel):
    name: str
    email: EmailStr
    access_token: str
    refresh_token: str
    processed_email_ids: Optional[List[str]] = []