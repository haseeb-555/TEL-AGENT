import os
import json
import asyncio
from pathlib import Path
from dotenv import load_dotenv
from fastapi import FastAPI, WebSocket, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google.genai.types import Part, Content
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agents.subagents.company.agent import root_agent
from google.genai import types
import math
import random
import string
import httpx
import base64
import pytz
from datetime import datetime, timedelta
from utils.processed_ids import load_processed_ids, save_processed_ids


load_dotenv()

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"
USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")


app = FastAPI()

APP_NAME = "deadline_extractor_app"
session_service = InMemorySessionService()

class BodyInput(BaseModel):
    body: str

origins = [
    "http://localhost",  
    "http://localhost:3000",  
    "http://127.0.0.1:3000",  
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

STATIC_DIR = Path("static")
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

def start_agent_session(session_id: str):
    """Starts an agent session"""
    # Create a session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    if not session:
        print(f"Error: Session creation failed for session_id {session_id}")
        return None, None

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality
    run_config = RunConfig(response_modalities=["TEXT"])

    # LiveRequestQueue and events
    live_request_queue = LiveRequestQueue()
    live_events = runner.run_live(
        session=session,
        live_request_queue=live_request_queue,
        run_config=run_config,
    )

    return live_events, live_request_queue


async def call_agent_async(query: str, runner, app_name: str, session_id: str):
    content = Content(role='user', parts=[Part(text=query)])

    async for event in runner.run_async(user_id=session_id, session_id=session_id, new_message=content):
        if event.is_final_response():
            session = session_service.get_session(
                app_name=app_name,
                user_id=session_id,
                session_id=session_id
            )
            print(f"State after agent run: {session.state}")

            # Clean the agent output to get the actual JSON string
            cleaned_output = (
                session.state['final_response']
                .strip()
                .replace("```json", "")
                .replace("```", "")
            )


            # Check if the cleaned output is valid JSON
            try:
                parsed_data = json.loads(cleaned_output)
                print(parsed_data)
            except json.JSONDecodeError as e:
                print(f"Skipping email due to JSON decode error: {e}")
                return {"deadline": "No deadline extracted."}

            # Map to the new key-value format
            converted_data = {
                "name": parsed_data.get("Name"),
                "event": parsed_data.get("Event Title"),
                "deadline": parsed_data.get("Deadline"),
                "description": parsed_data.get("Description")
            }

            print("Converted data:", converted_data)

            return {
                'deadline': converted_data.get('deadline', 'No deadline available')
            }

    return {
        "deadline": "No deadline extracted."
    }


@app.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: int):
    """Client websocket endpoint"""
    # Wait for client connection
    await websocket.accept()
    print(f"Client #{session_id} connected")

    # Start agent session
    session_id = str(session_id)
    live_events, live_request_queue = start_agent_session(session_id)

    if not live_events or not live_request_queue:
        await websocket.send_text(json.dumps({"error": "Session creation failed."}))
        await websocket.close()
        return

    # Start tasks for communication
    agent_to_client_task = asyncio.create_task(
        agent_to_client_messaging(websocket, live_events, session_id)
    )
    client_to_agent_task = asyncio.create_task(
        client_to_agent_messaging(websocket, live_request_queue, session_id)
    )
    await asyncio.gather(agent_to_client_task, client_to_agent_task)

    # Disconnected
    print(f"Client #{session_id} disconnected")

@app.post('/deadline')
async def get_deadline(body_input: BodyInput):
    try:
        body = body_input.body

        # Generate a random session_id
        session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        #print(f"Generated session_id: {session_id}")

        # Start agent session
        session = start_agent_session(session_id)
        if not session:
            return JSONResponse(status_code=400, content={"error": f"Session creation failed for session_id {session_id}"})

        # Create a Runner
        runner = Runner(
            agent=root_agent,  # Assuming root_agent is defined
            app_name=APP_NAME,
            session_service=session_service
        )

        # Call the agent asynchronously to process the query
        agent_res = await call_agent_async(body, runner, APP_NAME, session_id)
        deadline = agent_res['deadline']
        print("deadline we got is", deadline)

        return agent_res

    except Exception as e:
        return JSONResponse(status_code=400, content={"error": str(e)})

@app.post("/userinfo")
async def get_userinfo(request: Request):
    data = await request.json()
    code = data.get("code")

    token_payload = {
        "code": code,
        "client_id": client_id,
        "client_secret": client_secret,
        "redirect_uri": redirect_uri,
        "grant_type": "authorization_code"
    }

    async with httpx.AsyncClient() as client:
        token_res = await client.post(GOOGLE_TOKEN_URL, data=token_payload)
        token_data = token_res.json()

        access_token = token_data.get("access_token")
        refresh_token = token_data.get("refresh_token") 

        if not access_token:
            return {"error": "Token exchange failed", "details": token_data}

        # Get user's email
        profile_res = await client.get(
            f"{GMAIL_API_BASE}/users/me/profile",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        email = profile_res.json().get("emailAddress")

        # Get user's name
        userinfo_res = await client.get(
            USERINFO_URL,
            headers={"Authorization": f"Bearer {access_token}"}
        )
        name = userinfo_res.json().get("name")

        return {
            "access_token": access_token,
            "refresh_token": refresh_token, 
            "email": email,
            "name": name,
        }

@app.post('/getemails')
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
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults={count}",
            headers={"Authorization": f"Bearer {access_token}"}
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


processed_ids = load_processed_ids()
@app.post('/createEvents')
async def createEvents(request: Request):
    data = await request.json()
    refresh_token = data.get("refresh_token")

    if not refresh_token:
        return {"success": False, "error": "Refresh token missing"}

    # Step 1: Get a new access token using the refresh token
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
            return {"success": False, "error": "Failed to refresh access token", "details": token_data}

        emails = []

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

            if message_id in processed_ids:
                continue

            processed_ids.add(message_id)

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
            deadline_response = await get_deadline(body_input)

            if isinstance(deadline_response, dict) and "deadline" in deadline_response:
                raw_response = deadline_response.get("deadline", "")
                event_info = deadline_response
            else:
                continue

            if not raw_response:
                print("No deadline returned from agent.")
                continue

            try:
                parsed_deadline = datetime.strptime(raw_response, "%Y-%m-%dT%H:%M:%S")
                end_time = (parsed_deadline + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError as e:
                print(f"Skipping email due to deadline parsing error: {e}")
                continue

            def to_rfc3339(dt_str: str) -> str:
                return datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S").isoformat()

            event = {
                "summary": event_info.get("event", "Event from Email"),
                "description": event_info.get("description", "Auto-created from Gmail deadline."),
                "start": {
                    "dateTime": to_rfc3339(raw_response),
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

            print(event)

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
