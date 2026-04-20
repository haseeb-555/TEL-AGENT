from fastapi import APIRouter,HTTPException,Request
from fastapi.responses import FileResponse, JSONResponse
from models.user import User
from config.database import users
from schema.schema import individual_serial
from bson import ObjectId
import httpx,os
from dotenv import load_dotenv
from config.config import GOOGLE_TOKEN_URL, GMAIL_API_BASE, USERINFO_URL, BodyInput
from datetime import datetime, timedelta
from routes.agents import extract_deadline_from_body
import base64
load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")


event_router = APIRouter()


@event_router.post('/createEvents')
async def createEvents(request: Request):
    data = await request.json()
    email = data.get("email")

    user = users.find_one({"email": email})

    refresh_token = user.get("refresh_token")
    access_token = user.get("access_token")


    async with httpx.AsyncClient() as client:

        emails = []

        email_res = await client.get(
            "https://gmail.googleapis.com/gmail/v1/users/me/messages",
            headers={"Authorization": f"Bearer {access_token}"},
            params={
                "maxResults": 3,
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
                return {"success": False, "error": "Failed to refresh access token", "details": token_data}

            users.update_one({"email": email}, {"$set": {"access_token": access_token}})
            
            email_res = await client.get(
                "https://gmail.googleapis.com/gmail/v1/users/me/messages",
                headers={"Authorization": f"Bearer {access_token}"},
                params={
                    "maxResults": 5,
                    "labelIds": "INBOX",
                    "q": "is:inbox -from:me"
                }
            )

        messages = email_res.json().get("messages", [])

        for message in messages:
            message_id = message["id"]
            processed_ids = user.get("processed_email_ids", [])

            if message_id in processed_ids:
                continue

            processed_ids.append(message_id)
            users.update_one({"email": email}, {"$set": {"processed_email_ids": processed_ids}})
            

            message_res = await client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full",
                headers={"Authorization": f"Bearer {access_token}"}
            )

            message_json = message_res.json()
            payload = message_json.get("payload", {})
            headers = payload.get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)

            
            # Extract body
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

            body_input = BodyInput(body=body)
            response = await extract_deadline_from_body(body_input.body)

            if isinstance(response, dict):
                deadline = response.get("deadline")
                event_name = response.get("event_name", "No Title")
                description = response.get("description", "")
            else:
                print("Agent response is not a dict, skipping.")
                continue

            if not deadline:
                print(f"No deadline returned for message ID {message_id}, skipping.")
                continue

            try:
                parsed_deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
                end_time = (parsed_deadline + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError as e:
                print(f"Skipping email due to deadline parsing error: {e}")
                continue

            def to_rfc3339(dt_str: str) -> str:
                return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S").isoformat()

            event = {
                "summary": event_name,
                "description": description,
                "start": {
                    "dateTime": to_rfc3339(deadline),
                    "timeZone": "Asia/Kolkata",
                },
                "end": {
                    "dateTime": to_rfc3339(end_time),
                    "timeZone": "Asia/Kolkata",
                },
                "reminders": {
                    "useDefault": False,
                    "overrides": [
                        {"method": "popup", "minutes": 60}
                    ]
                }
            }

            #print(event)

            res = await client.post(
                "https://www.googleapis.com/calendar/v3/calendars/primary/events",
                headers={
                    "Authorization": f"Bearer {access_token}",
                    "Content-Type": "application/json"
                },
                json=event
            )

            if res.status_code in (200, 201):
                emails.append({"id": message_id, "status": "created"})
                
            else:
                emails.append({"id": message_id, "status": "failed", "error": res.text})

    return {"success": True, "processed": emails}
