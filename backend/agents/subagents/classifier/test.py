from google.adk.agents.parallel_agent import ParallelAgent
from google.adk.agents.llm_agent import LlmAgent
from google.adk.sessions import InMemorySessionService
from google.adk.runners import Runner
from google.adk.tools import google_search
from google.genai import types

APP_NAME = "classifer"
USER_ID = "user_01"
SESSION_ID = "session_01"
GEMINI_MODEL = "gemini-2.0-flash"

from agent import classifier_root


# Load environment variables
from dotenv import load_dotenv
load_dotenv()



# Session and Runner
session_service = InMemorySessionService()
session = session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)
runner = Runner(agent=classifier_root, app_name=APP_NAME, session_service=session_service)


# Agent Interaction
def call_agent(query):
    '''
    Helper function to call the agent with a query.
    '''
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
            print(f"State after agent run: {session.state['mail_class']}")
            print("Agent responded.") 

call_agent("Dear student, you are shortlisted for an interview at Microsoft scheduled for next Friday.")

call_agent("Participate in our upcoming coding competition on HackerRank with exciting prizes.")

call_agent("Your lab test reports are now available. Please consult your physician for further guidance.")

call_agent("Congratulations! You've won a $1000 gift card. Click here to claim now.")

call_agent("Your ticket to Delhi on 10th May via Indigo Airlines has been confirmed. Enjoy your trip!")
