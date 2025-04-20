from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.adk.agents.loop_agent import LoopAgent
from .prompts import COMPANY_NAME_PROMPT,EVENT_TITLE_PROMPT,DEADLINE_PROMPT,RESEARCH_PROMPT

from google.adk.agents.parallel_agent import ParallelAgent

MODEL = "gemini-2.0-flash-exp"

company_name_agent=LlmAgent(
    name="company_name_extraction_agent",
    model=MODEL,
    instruction=COMPANY_NAME_PROMPT,
    description="extract the company name",
    output_key="company_name"
)

event_title_agent=LlmAgent(
    name="event_agent",
    model=MODEL,
    description="extracts the event title for creating the event in google remainder",
    instruction=EVENT_TITLE_PROMPT,
    output_key="event_title"
    
)


deadline_agent = LlmAgent(
    name="deadline_agent",
    model=MODEL,
    instruction=DEADLINE_PROMPT,
    description="Extracts the deadline time from the message",
    output_key="deadline"
)

from google.adk.agents.llm_agent import LlmAgent

research_agent = LlmAgent(
    name="company_research_agent",
    model=MODEL,
    instruction=RESEARCH_PROMPT,
    description="Provides brief research on the given company",
    output_key="company_research"
)

company_agent = ParallelAgent(
    name="root_agent_of_company",
    sub_agents=[
        research_agent,
        company_name_agent,
        event_title_agent,
        deadline_agent
    ]
)




root_agent = LlmAgent(
    name="root_event_extraction_agent",
    model=MODEL,
    instruction="""
You are an assistant that reads placement-related email messages and returns the following key details in a structured dictionary format:

1. **Name**: Extract ONLY the name of the company. Do NOT include extra words like "interview", "hiring", "drive", etc. Just the proper company name (e.g., Google, Microsoft, Infosys).
2. **Event Title**: Provide a short, informative calendar reminder title (e.g., GOOGLE ONLINE ASSESSMENT, TCS NINJA HIRING CHALLENGE).
3. **Deadline**: Extract exact deadline time in format YYYY-MM-DD HH:MM:SS (24-hour format). Only include if clearly mentioned.
4. **Description**: Give a short research-based overview of the company including what it does, headquarters, recent news (if any), and a link to official/careers page.

🧾 Examples:
Message: "Google is conducting an online assessment. Register before 13th July 2024 at 5:00 PM."
→
{
  "Name": "Google",
  "Event Title": "GOOGLE ONLINE ASSESSMENT",
  "Deadline": "2024-07-13 17:00:00",
  "Description": "Google is a multinational technology company headquartered in Mountain View, California. It specializes in internet-related services and products. Recent initiatives include developments in AI and Search. Careers: https://careers.google.com"
}

ONLY return a single dictionary in JSON format with the four keys: Name, Event Title, Deadline, Description.
""",
    description="Extracts all relevant placement event information in one response.",
    output_key="final_response"
)

# company_root_agent = LlmAgent(
#     name="company_wrapper_agent",
#     description="Wrapper agent to run parallel agent via run_live",
#     agent=ParallelAgent(
#         name="company_parallel_agent",
#         description="Runs all info extractors in parallel",
#         sub_agents=[company_name_agent, deadline_agent, research_agent]
#     ),
#     model="gemini-1.5-pro"  # Just needed so LlmAgent is valid
# )