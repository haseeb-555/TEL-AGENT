from fastapi import APIRouter,WebSocket,Request
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from config.config import GOOGLE_TOKEN_URL, GMAIL_API_BASE, USERINFO_URL, BodyInput
from google.genai.types import Part, Content
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from agents.subagents.company.agent import root_agent
from google.genai import types
import os,asyncio
from pathlib import Path
from fastapi.staticfiles import StaticFiles

load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

APP_NAME = "deadline_extractor_app"
session_service = InMemorySessionService()

agent_router = APIRouter()


STATIC_DIR = Path("static")
agent_router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

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
            #print(f"State after agent run: {session.state}")

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
                #print(parsed_data)
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

            #print("Converted data:", converted_data)

            return {
                'deadline': converted_data.get('deadline', 'No deadline available'),
                'event_name':converted_data.get('event','no event'),
                'description':converted_data.get('description','no description')
            }

    return {
        "deadline": "No deadline extracted."
    }



@agent_router.get("/")
async def root():
    """Serves the index.html"""
    return FileResponse(os.path.join(STATIC_DIR, "index.html"))

@agent_router.websocket("/ws/{session_id}")
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

# @agent_router.post('/deadline')
# async def get_deadline(body_input: BodyInput):
#     try:
#         body = body_input.body

#         # Generate a random session_id
#         session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
#         #print(f"Generated session_id: {session_id}")

#         # Start agent session
#         session = start_agent_session(session_id)
#         if not session:
#             return JSONResponse(status_code=400, content={"error": f"Session creation failed for session_id {session_id}"})

#         # Create a Runner
#         runner = Runner(
#             agent=root_agent,  # Assuming root_agent is defined
#             app_name=APP_NAME,
#             session_service=session_service
#         )

#         # Call the agent asynchronously to process the query
#         agent_res = await call_agent_async(body, runner, APP_NAME, session_id)
#         deadline = agent_res['deadline']
#         # event_name = agent_res['event_name']
#         # description = agent_res['description']
#         print("deadline we got is", deadline)

#         return agent_res

#     except Exception as e:
#         return JSONResponse(status_code=400, content={"error": str(e)})


import random, string, json
from config.config import BodyInput

async def extract_deadline_from_body(body: str) -> dict:
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    session = start_agent_session(session_id)

    if not session:
        return {"error": f"Session creation failed for session_id {session_id}"}

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service
    )

    agent_res = await call_agent_async(body, runner, APP_NAME, session_id)
    
    deadline = agent_res['deadline']
        # description = agent_res['description']
    print("deadline we got is", deadline)

    return agent_res

   