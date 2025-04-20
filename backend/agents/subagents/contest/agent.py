# from google.adk.agents.llm_agent import LlmAgent
# from google.adk.tools import google_search
# from google.adk.agents.loop_agent import LoopAgent
# from .prompts import START_TIME_PROMPT,CONTEST_CHATBOT_PROMPT

# MODEL = "gemini-2.0-flash-exp"

# contest_time_extract=LlmAgent(
#   name="contest_starttime_agent",
#   model=MODEL,
#   description="extract the start time of contest",
#   instruction=START_TIME_PROMPT,
#   output_key="contest_start_time"
# )

# contest_chatbot=LlmAgent(
#   name="contest_chatbot_agent",
#   model=MODEL,
#   description="answer the question of contest related to the coding contest of leetcode,codeforces,gfg,codechef ",
#   instruction=CONTEST_CHATBOT_PROMPT,
#   output_key="contest_bot_respone",
#   tools=[google_search]
# )

# test_bot=LlmAgent(
#   name="student_assitance",
#   model=MODEL,
#   description="provide the past OA and interview questions of the company name ",
#   instruction="""user provides the company name , u provide the past coding and cs fundamnetal questions asked in OA'S AND INTERVIEWS related to topics which are about software and computer science related topics""",
#   tools=[google_search],
#   output_key="extracted_url_info"
#    )

from google.adk.agents.llm_agent import LlmAgent
from google.adk.agents.parallel_agent import ParallelAgent
from .prompts import (
    CONTEST_NAME_PROMPT,
    CONTEST_TYPE_PROMPT,
    PLATFORM_PROMPT,
    START_TIME_PROMPT,
    DESCRIPTION_PROMPT
)

MODEL = "gemini-2.0-flash-exp"

contest_name_agent = LlmAgent(
    name="contest_name_agent",
    model=MODEL,
    instruction=CONTEST_NAME_PROMPT,
    description="Extracts the name of the contest.",
    output_key="contest_name"
)

contest_type_agent = LlmAgent(
    name="contest_type_agent",
    model=MODEL,
    instruction=CONTEST_TYPE_PROMPT,
    description="Classifies the type of contest (e.g., Coding, Hackathon).",
    output_key="contest_type"
)

platform_agent = LlmAgent(
    name="platform_agent",
    model=MODEL,
    instruction=PLATFORM_PROMPT,
    description="Identifies the platform hosting the contest.",
    output_key="platform"
)

start_time_agent = LlmAgent(
    name="start_time_agent",
    model=MODEL,
    instruction=START_TIME_PROMPT,
    description="Extracts the start time in calendar-friendly format.",
    output_key="start_time"
)

description_agent = LlmAgent(
    name="contest_description_agent",
    model=MODEL,
    instruction=DESCRIPTION_PROMPT,
    description="Generates a short overview and useful link.",
    output_key="description"
)

contest_agent = ParallelAgent(
    name="root_contest_agent",
    sub_agents=[
        contest_name_agent,
        contest_type_agent,
        platform_agent,
        start_time_agent,
        description_agent
    ]
)


root_agent = LlmAgent(
    name="root_contest_event_extraction_agent",
    model="gemini-2.0-flash-exp",
    instruction="""
You are an assistant that reads contest-related email messages and returns the following key details in a structured dictionary format:

1. **Contest Name**: Extract the full name of the contest (e.g., Codeforces Round 937, TCS CodeVita 2024).
2. **Contest Type**: Classify the type of contest (e.g., Coding Contest, MCQ Assessment, Hackathon, Quiz).
3. **Platform**: Extract the platform or website where the contest is being hosted (e.g., Codeforces, HackerRank, TCS iON).
4. **Start Time**: Extract the exact start time of the contest in this format: YYYY-MM-DDTHH:MM:SS (24-hour format). Include only if clearly mentioned.
5. **Description**: Provide a short overview of the contest: what it is about, who can participate, and include a registration or info link if available.

🧾 Examples:
Message: "Register now for Codeforces Round 937 (Div. 2) starting on 25th May 2024 at 6:00 PM on Codeforces."
→
{
  "Contest Name": "Codeforces Round 937",
  "Contest Type": "Coding Contest",
  "Platform": "Codeforces",
  "Start Time": "2024-05-25T18:00:00",
  "Description": "Codeforces Round 937 is a competitive programming contest hosted on Codeforces. It is open for Div. 2 participants. Register at: https://codeforces.com/contests"
}

ONLY return a single dictionary in JSON format with the five keys: Contest Name, Contest Type, Platform, Start Time, Description.
""",
    description="Extracts structured contest event details from emails.",
    output_key="final_response"
)