from fastapi import APIRouter,WebSocket,Request
from fastapi.responses import FileResponse, JSONResponse
from dotenv import load_dotenv
from config.config import GOOGLE_TOKEN_URL, GMAIL_API_BASE, USERINFO_URL, BodyInput
from google.genai.types import Part, Content
from google.adk.runners import Runner
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from pydantic import BaseModel


from agents.subagents.company.agent import root_agent
from agents.subagents.chatbot.agent import chat_bot_root
from agents.subagents.classifier.agent import classifier_root
from agents.subagents.travel.agent import travel_root_agent


from google.genai import types
import os,asyncio
from pathlib import Path
from fastapi.staticfiles import StaticFiles
import random, string, json
from config.config import BodyInput


load_dotenv()

client_id = os.getenv("GOOGLE_CLIENT_ID")
client_secret = os.getenv("GOOGLE_CLIENT_SECRET")
redirect_uri = os.getenv("REDIRECT_URI")

APP_NAME = "email_application_agent"
session_service = InMemorySessionService()

agent_router = APIRouter()


STATIC_DIR = Path("static")
agent_router.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")



def start_agent_session(session_id: str):
    """Starts an agent session"""

    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality = TEXT
    run_config = RunConfig(response_modalities=["TEXT"])

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    # Start agent session
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
                'deadline': converted_data.get('deadline', 'No deadline available'),
                'event_name':converted_data.get('event','no event'),
                'description':converted_data.get('description','no description')
            }

    return {
        "deadline": "No deadline extracted."
    }


def create_session_runner(main_agent):
    session_id = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
    
    # Create a Session
    session = session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=main_agent,
        session_service=session_service,
    )
    
    return runner,session_id


async def extract_deadline_from_body(body: str) -> dict:
    
    
    print("body mai kya hai",body)
    
    runner,session_id=await create_session_runner(root_agent)
    


    agent_res = await call_agent_async(body, runner, APP_NAME, session_id)
    
    deadline = agent_res['deadline']
        # description = agent_res['description']
    print("deadline we got is", deadline)

    return agent_res

def call_chatbot_agent(query,runner,app_name,session_id):
    content = Content(role='user', parts=[Part(text=query)])
    
    events =runner.run(user_id=session_id, session_id=session_id, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            if final_response:
             print("Agent Response: ", final_response)
            session = session_service.get_session(
                    app_name=APP_NAME,
                    user_id=session_id,
                    session_id=session_id
                )
            print(f"State after agent run: {session.state}")

    return session.state.get("local_news", "Sorry, I didn't get that.")
    
    



def chatbot_response(body:str)->str:
    
    runner,session_id=create_session_runner(travel_root_agent)
    agent_res=call_chatbot_agent(body,runner,APP_NAME,session_id)
    
    print("agent_res:",agent_res)
    
    return agent_res

@agent_router.post("/chatbot")
async def chatbot_handler(request: BodyInput):
    response = chatbot_response(request.body)
    return {"reply": response}




@agent_router.get("/chatbot")
async def chatbot_ui():
    return FileResponse("static/chatbot.html")  # or wherever your HTML file is




