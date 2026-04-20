from fastapi import APIRouter,HTTPException,Request
from models.user import User
from config.database import users
from schema.schema import individual_serial
from bson import ObjectId
import httpx,os
from dotenv import load_dotenv
from config.config import GOOGLE_TOKEN_URL, GMAIL_API_BASE, USERINFO_URL
import base64
load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

email_router = APIRouter()


@email_router.post('/getemails')
async def get_emails(request: Request):
    data = await request.json()

    email = data.get("email")
    count = int(data.get("count", 5))

    user = users.find_one({"email": email})
    access_token = user.get("access_token")
    refresh_token = user.get("refresh_token")

    emails = []
    async with httpx.AsyncClient() as client:
        email_res = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "maxResults": count,
                    "labelIds": "INBOX",
                    "q": "is:inbox -from:me"
                }
            )

        if email_res.status_code == 401:

            token_payload = {
                "client_id": client_id,
                "client_secret": client_secret,
                "refresh_token": refresh_token,
                "grant_type": "refresh_token"
            }

            
            token_res = await client.post(GOOGLE_TOKEN_URL, data=token_payload)
                token_data = token_res.json()
                access_token = token_data.get("access_token")

                if not access_token:
                    return {"error": "Failed to refresh access token", "details": token_data}
                
                users.update_one({"email": email}, {"$set": {"access_token": access_token}})

                email_res = await client.get(
                    "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                    headers={"Authorization": f"Bearer {access_token}"},
                    params={
                        "maxResults": count,
                        "labelIds": "INBOX",
                        "q": "is:inbox -from:me"
                    }
                )

        messages = email_res.json().get("messages", [])

        for message in messages:
                message_id = message["id"]

                message_res = await client.get(
                    f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full",
                    headers={"Authorization": f"Bearer {access_token}"}
                )

                message_json = message_res.json()
                payload = message_json.get("payload", {})
                headers = payload.get("headers", [])
                subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)
                snippet = message_json.get("snippet")

                # Extract body (handling plain text inside multipart or direct body)
                body = ""
                if "parts" in payload:
                    for part in payload["parts"]:
                        if part.get("mimeType") == "text/plain":
                            body_data = part.get("body", {}).get("data")
                            if body_data:
                                body = base64.urlsafe_b64decode(body_data.encode("utf-8")).decode("utf-8")
                                break
                else:
                    body_data = payload.get("body", {}).get("data")
                    if body_data:
                        body = base64.urlsafe_b64decode(body_data.encode("utf-8")).decode("utf-8")

                emails.append({
                    "id": message_id,
                    "subject": subject,
                    "snippet": snippet,
                    "body": body
                })        

    return {"emails": emails}


