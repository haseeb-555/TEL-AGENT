from google.adk.agents.loop_agent import LoopAgent
from google.adk.agents.llm_agent import LlmAgent
from google.genai import types
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import google_search

# Load environment variables
from dotenv import load_dotenv
load_dotenv()

MODEL = "gemini-2.0-flash-exp"

# Constants
APP_NAME = "travel_info_app"
USER_ID = "user_01"
SESSION_ID = "session_travel_01"


DEST_KEY = "travel_dest"
WEATHER_KEY = "weather_info"
NEWS_KEY = "local_news"

# --- Subagents ---

# 1. Destination Extractor Agent
destination_agent = LlmAgent(
    name="DestinationExtractor",
    model=MODEL,
    instruction=f"""
    You are a Travel Destination Extractor AI.
    The input is a user email or message related to travel (e.g., booking confirmations, ticket details, travel plans).
    Your task is to extract the final travel destination *city or place* from the email-like content .
    
    Be precise: ignore source/boarding locations, and focus only on the destination city or location.
    
    Example Inputs:
    - "Flight from Delhi to Goa on 5th May" → Output: Goa
    - "IRCTC confirms your train from Lucknow to Dehradun" → Output: Dehradun
    - "Confirmation of ticket to Kashmir" → Output: Kashmir

    Output only the name of the destination (e.g., "Goa", "Dehradun").
    """,
    description="Extracts destination from travel-related emails or messages.",
    output_key=DEST_KEY
)

# 2. Weather Info Agent
weather_agent = LlmAgent(
    name="WeatherInfoAgent",
    model=MODEL,
    instruction=f"""
    You are a Weather Info Agent.
    Use the travel destination in session state key '{DEST_KEY}'.
    Provide a brief weather update for that destination using Google Search if necessary.
    
    Include:
    - Current weather
    - 2–3 day forecast

   
    """,
    description="Fetches weather for the travel destination.",
    tools=[google_search],
    output_key=WEATHER_KEY
)

# 3. Local News Agent
news_agent = LlmAgent(
    name="LocalNewsAgent",
    model=MODEL,
    instruction=f"""
    You are a Local News Fetcher AI.
    Check the destination city/place in session key '{DEST_KEY}'.
    Search the web using Google Search to find 1–2 latest headlines, events, or alerts related to this destination.


    Only include news summaries. No URLs required.
    """,
    description="Fetches recent local news for the destination.",
    tools=[google_search],
    output_key=NEWS_KEY
)

# Loop Agent: Travel Planner
travel_root_agent = LoopAgent(
    name="TravelLoopAgent",
    sub_agents=[destination_agent, weather_agent, news_agent],
    max_iterations=1
)

# Setup Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=travel_root_agent, app_name=APP_NAME, session_service=session_service)

# Agent Trigger Function
def call_travel_agent(query: str):
    content = types.Content(role='user', parts=[types.Part(text=query)])
    events = runner.run(user_id=USER_ID, session_id=SESSION_ID, new_message=content)

    for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            if final_response:
             print("Agent Response: ", final_response)
            session = session_service.get_session(
                    app_name=APP_NAME,
                    user_id=USER_ID,
                    session_id=SESSION_ID
                )
            print(f"State after agent run: {session.state}")
            print("Agent responded.") 

# Example Run
# if __main__=="agent"
# call_travel_agent("Confirmation of your SpiceJet flight ticket from Delhi to Srinagar on April 30.")
