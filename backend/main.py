# import os
# import json
# import asyncio
# from pathlib import Path
# from dotenv import load_dotenv
# from fastapi import FastAPI, WebSocket, Request
# from fastapi.staticfiles import StaticFiles
# from fastapi.responses import FileResponse, JSONResponse
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from google.genai.types import Part, Content
# from google.adk.runners import Runner
# from google.adk.agents import LiveRequestQueue
# from google.adk.agents.run_config import RunConfig
# from google.adk.sessions.in_memory_session_service import InMemorySessionService
# from agents.subagents.company.agent import company_agent
# import httpx
# import base64
# from datetime import datetime, timedelta

# load_dotenv()

# GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
# GMAIL_API_BASE = "https://gmail.googleapis.com/gmail/v1"
# USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

# client_id = os.getenv("GOOGLE_CLIENT_ID")
# client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
# redirect_uri = os.getenv("REDIRECT_URI")

# app = FastAPI()

# APP_NAME = "deadline_extractor_app"
# session_service = InMemorySessionService()

# class BodyInput(BaseModel):
#     body: str

# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# STATIC_DIR = Path("static")
# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# processed_ids = set()

# # Utilities and core logic
# def start_agent_session(session_id: str):
#     session = session_service.create_session(APP_NAME, session_id, session_id)
#     if not session:
#         return None, None

#     runner = Runner(app_name=APP_NAME, agent=company_agent, session_service=session_service)
#     run_config = RunConfig(response_modalities=["TEXT"])
#     live_request_queue = LiveRequestQueue()
#     live_events = runner.run_live(session=session, live_request_queue=live_request_queue, run_config=run_config)
#     return live_events, live_request_queue

# def call_agent_async(query: str, runner, app_name: str, session_id: str):
#     content = Content(role='user', parts=[Part(text=query)])
#     for event in runner.run(user_id=session_id, session_id=session_id, new_message=content):
#         if event.is_final_response():
#             session = session_service.get_session(app_name, session_id, session_id)
#             return {'deadline': session.state.get('deadline', '').strip()}
#     return {'deadline': ''}

# # Routes
# @app.get("/")
# async def root():
#     return FileResponse(os.path.join(STATIC_DIR, "index.html"))

# @app.websocket("/ws/{session_id}")
# async def websocket_endpoint(websocket: WebSocket, session_id: int):
#     await websocket.accept()
#     session_id = str(session_id)
#     live_events, live_request_queue = start_agent_session(session_id)
#     if not live_events or not live_request_queue:
#         await websocket.send_text(json.dumps({"error": "Session creation failed."}))
#         await websocket.close()
#         return

#     async def agent_to_client_messaging(websocket, live_events, session_id):
#         async for event in live_events:
#             await websocket.send_text(json.dumps({"event": event.text}))

#     async def client_to_agent_messaging(websocket, live_request_queue, session_id):
#         while True:
#             data = await websocket.receive_text()
#             await live_request_queue.put(Content(role='user', parts=[Part(text=data)]))

#     await asyncio.gather(
#         agent_to_client_messaging(websocket, live_events, session_id),
#         client_to_agent_messaging(websocket, live_request_queue, session_id)
#     )

# @app.post('/deadline')
# def get_deadline(body_input: BodyInput):
#     try:
#         body = body_input.body
#         session_id = os.urandom(8).hex()
#         start_agent_session(session_id)
#         runner = Runner(agent=company_agent, app_name=APP_NAME, session_service=session_service)
#         return call_agent_async(body, runner, APP_NAME, session_id)
#     except Exception as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})

# @app.post("/userinfo")
# async def get_userinfo(request: Request):
#     data = await request.json()
#     code = data.get("code")

#     token_payload = {
#         "code": code,
#         "client_id": client_id,
#         "client_secret": client_secret,
#         "redirect_uri": redirect_uri,
#         "grant_type": "authorization_code"
#     }

#     async with httpx.AsyncClient() as client:
#         token_res = await client.post(GOOGLE_TOKEN_URL, data=token_payload)
#         token_data = token_res.json()
#         access_token = token_data.get("access_token")
#         if not access_token:
#             return {"error": "Token exchange failed", "details": token_data}

#         profile_res = await client.get(f"{GMAIL_API_BASE}/users/me/profile", headers={"Authorization": f"Bearer {access_token}"})
#         email = profile_res.json().get("emailAddress")
#         userinfo_res = await client.get(USERINFO_URL, headers={"Authorization": f"Bearer {access_token}"})
#         name = userinfo_res.json().get("name")

#         return {"access_token": access_token, "email": email, "name": name}

# @app.post('/getemails')
# async def get_emails(request: Request):
#     data = await request.json()
#     access_token = data.get("access_token")
#     count = int(data.get("count", 5))
#     emails = []

#     async with httpx.AsyncClient() as client:
#         email_res = await client.get(f"{GMAIL_API_BASE}/users/me/messages?maxResults={count}", headers={"Authorization": f"Bearer {access_token}"})
#         messages = email_res.json().get("messages", [])

#         for message in messages:
#             message_id = message["id"]
#             message_res = await client.get(f"{GMAIL_API_BASE}/users/me/messages/{message_id}?format=full", headers={"Authorization": f"Bearer {access_token}"})
#             message_json = message_res.json()
#             payload = message_json.get("payload", {})
#             headers = payload.get("headers", [])
#             subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)
#             snippet = message_json.get("snippet")

#             body = ""
#             if "parts" in payload:
#                 for part in payload["parts"]:
#                     if part.get("mimeType") == "text/plain":
#                         body_data = part.get("body", {}).get("data")
#                         if body_data:
#                             body = base64.urlsafe_b64decode(body_data.encode()).decode()
#                             break
#             else:
#                 body_data = payload.get("body", {}).get("data")
#                 if body_data:
#                     body = base64.urlsafe_b64decode(body_data.encode()).decode()

#             emails.append({"id": message_id, "subject": subject, "snippet": snippet, "body": body})

#     return {"emails": emails}

# @app.post('/createEvents')
# async def create_events(request: Request):
#     data = await request.json()
#     access_token = data.get("access_token")
#     if not access_token:
#         return {"success": False, "error": "Access token missing"}

#     events = []
#     async with httpx.AsyncClient() as client:
#         email_res = await client.get(f"{GMAIL_API_BASE}/users/me/messages?maxResults=5", headers={"Authorization": f"Bearer {access_token}"})
#         messages = email_res.json().get("messages", [])

#         for message in messages:
#             message_id = message["id"]
#             if message_id in processed_ids:
#                 continue

#             message_res = await client.get(f"{GMAIL_API_BASE}/users/me/messages/{message_id}?format=full", headers={"Authorization": f"Bearer {access_token}"})
#             message_json = message_res.json()
#             payload = message_json.get("payload", {})
#             headers = payload.get("headers", [])
#             subject = next((h["value"] for h in headers if h["name"] == "Subject"), "Event from Email")

#             body = ""
#             if "parts" in payload:
#                 for part in payload["parts"]:
#                     if part.get("mimeType") == "text/plain":
#                         body_data = part.get("body", {}).get("data")
#                         if body_data:
#                             body = base64.urlsafe_b64decode(body_data.encode()).decode()
#                             break
#             else:
#                 body_data = payload.get("body", {}).get("data")
#                 if body_data:
#                     body = base64.urlsafe_b64decode(body_data.encode()).decode()

#             deadline_response = get_deadline(BodyInput(body=body))
#             deadline = deadline_response.get("deadline", "").replace("\n", "").strip()
            

#             try:
#                 parsed_dt = datetime.strptime(deadline, "%Y-%m-%d %H:%M:%S")
#                 start = parsed_dt.isoformat()
#                 end = (parsed_dt + timedelta(hours=1)).isoformat()
#             except ValueError:
#                 continue

#             event = {
#                 "summary": subject,
#                 "description": "Auto-created from Gmail deadline.",
#                 "start": {"dateTime": start, "timeZone": "Asia/Kolkata"},
#                 "end": {"dateTime": end, "timeZone": "Asia/Kolkata"},
#                 "reminders": {"useDefault": False, "overrides": [{"method": "popup", "minutes": 60}]},
#             }

#             calendar_res = await client.post(
#                 "https://www.googleapis.com/calendar/v3/calendars/primary/events",
#                 headers={"Authorization": f"Bearer {access_token}", "Content-Type": "application/json"},
#                 json=event
#             )

#             if calendar_res.status_code in (200, 201):
#                 processed_ids.add(message_id)
#                 events.append({"id": message_id, "status": "created"})
#             else:
#                 events.append({"id": message_id, "status": "failed", "error": calendar_res.text})

#     return {"success": True, "processed": events}





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
    "http://localhost",  # Allow frontend running locally
    "http://localhost:3000",  # For React app on port 3000 (adjust as needed)
    "http://127.0.0.1:3000",  # If running React on 127.0.0.1
    # You can add more domains as needed
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Specifies which domains can make requests
    allow_credentials=True,
    allow_methods=["*"],  # Allow all HTTP methods
    allow_headers=["*"],  # Allow all headers
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
            cleaned_output = session.state['final_response'].strip().replace('```json\n', '').replace('\n```', '')

            # Check if the cleaned output is valid JSON
            try:
                parsed_data = json.loads(cleaned_output)
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
        deadline = agent_res['deadline'].strip()
        print(deadline)

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
            "email": email,
            "name": name,
        }

      
@app.post('/getemails')
async def get_emails(request: Request):
    data = await request.json()
    access_token = data.get("access_token")
    count = int(data.get("count", 5))

    emails = []

    async with httpx.AsyncClient() as client:
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

processed_ids = set()
@app.post('/createEvents')
async def createEvents(request: Request):
    data = await request.json()
    access_token = data.get("access_token")
    
    if not access_token:
        return {"success": False, "error": "Access token missing"}

    # Fetch the last 5 emails using the get_emails logic
    emails = []

    async with httpx.AsyncClient() as client:
        email_res = await client.get(
            f"https://gmail.googleapis.com/gmail/v1/users/me/messages?maxResults=5",
            headers={"Authorization": f"Bearer {access_token}"}
        )
        messages = email_res.json().get("messages", [])

        for message in messages:
            message_id = message["id"]

            # Skip if already processed
            if message_id in processed_ids:
                continue

            message_res = await client.get(
                f"https://gmail.googleapis.com/gmail/v1/users/me/messages/{message_id}?format=full",
                headers={"Authorization": f"Bearer {access_token}"}
            )
            message_json = message_res.json()
            payload = message_json.get("payload", {})
            headers = payload.get("headers", [])
            subject = next((h["value"] for h in headers if h["name"] == "Subject"), None)

            # Extract plain text body
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

            # Use /deadline logic to extract deadline
            body_input = BodyInput(body=body)

            deadline_response = await get_deadline(body_input)

            # Now handle the deadline_response directly as a dictionary
            if isinstance(deadline_response, dict):
                raw_response = deadline_response.get("deadline", "")
            else:
                raw_response = ""

            cleaned = raw_response.strip("` \n")  # Remove triple backticks and whitespace
            if cleaned.startswith("json"):
                cleaned = cleaned[len("json"):].strip()

            try:
                event_info = json.loads(cleaned)
            except json.JSONDecodeError as e:
                print(f"Skipping email due to JSON decode error: {e}")
                continue

            deadline = event_info.get("Deadline", "").strip()
            if not deadline:
                continue

            try:
                deadline = deadline.strip().replace(" ", "T")
                parsed_deadline = datetime.strptime(deadline, "%Y-%m-%dT%H:%M:%S")
                end_time = (parsed_deadline + timedelta(hours=1)).strftime("%Y-%m-%dT%H:%M:%S")
            except ValueError as e:
                print(f"Skipping email due to deadline parsing error: {e}")
                continue

            def to_rfc3339(dt_str: str) -> str:
                naive = datetime.strptime(dt_str, "%Y-%m-%dT%H:%M:%S")
                return naive.isoformat()

            event = {
                "summary": event_info.get("Event Title", "Event from Email"),
                "description": event_info.get("Description", "Auto-created from Gmail deadline."),
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

            # Create the event
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
                # Store processed ID to prevent duplicates
                processed_ids.add(message_id)
                emails.append({"id": message_id, "status": "created"})
            else:
                emails.append({"id": message_id, "status": "failed", "error": res.text})

    return {"success": True, "processed": emails}
