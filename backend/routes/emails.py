from fastapi import APIRouter,HTTPException,Request
from models.user import User
from config.database import users
from schema.schema import individual_serial
from bson import ObjectId
import httpx,os
from dotenv import load_dotenv
from config.config import GOOGLE_TOKEN_URL, GMAIL_API_BASE, USERINFO_URL
import base64
from google.genai.types import Part, Content
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agents.subagents.company.agent import root_agent
from agents.subagents.chatbot.agent import chat_bot_root
from agents.subagents.classifier.agent import classifier_root


from google.genai import types
import os,asyncio
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import random, string, json
from config.config import BodyInput
from pydantic import BaseModel


load_dotenv()




# Define a Pydantic model for email request
class ClassifyEmailRequest(BaseModel):
    email_id: str


email_router = APIRouter()


client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

APP_NAME = "email_application_agent"
session_service = InMemorySessionService()

agent_router = APIRouter()


STATIC_DIR = Path("static")
agent_router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


@email_router.post('/getemails')
async def get_emails(request: Request):
    data = await request.json()
    refresh_token = data.get("refresh_token")
    count = int(data.get("count", 5))

    # Step 1: Use refresh_token to get a new access_token
    token_payload = {
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token"
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(GOOGLE_TOKEN_URL, data=token_payload)
        token_data = token_res.json()
        access_token = token_data.get("access_token")

        if not access_token:
            return {"error": "Failed to refresh access token", "details": token_data}

        # Step 2: Fetch emails
        emails = []

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






async def create_session_runner(main_agent):
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    session = session_service.create_session(app_name=APP_NAME, user_id=session_id, session_id=session_id)
    runner = Runner(app_name=APP_NAME, agent=main_agent, session_service=session_service)
    return runner, session_id

async def classify_email_content(body: str, runner, session_id: str):
    content = Content(role='user', parts=[Part(text=body)])

    async for event in runner.run_async(user_id=session_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            session = session_service.get_session(app_name=APP_NAME, user_id=session_id, session_id=session_id)
            print(f"State after agent run: {session.state}")
            return session.state["mail_class"]
            
            
            
    
    

@email_router.post("/classify_email/{email_id}")
async def classify_email(email_id: str, request: ClassifyEmailRequest):
    # Retrieve email body by email_id (You need to implement this part)
    email_body = "Sample email body for classification"  # Placeholder, retrieve actual email body from DB
    
    # Create a session runner for the classifier
    runner, session_id = await create_session_runner(classifier_root)

    # Classify the email content
    classification = await classify_email_content(email_body, runner, session_id)

    return {"classification": classification}

