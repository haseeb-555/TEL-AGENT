from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.adk.agents.loop_agent import LoopAgent
from .prompts import START_TIME_PROMPT,CONTEST_CHATBOT_PROMPT

MODEL = "gemini-2.0-flash-exp"

contest_time_extract=LlmAgent(
  name="contest_starttime_agent",
  model=MODEL,
  description="extract the start time of contest",
  instruction=START_TIME_PROMPT,
  output_key="contest_start_time"
)

contest_chatbot=LlmAgent(
  name="contest_chatbot_agent",
  model=MODEL,
  description="answer the question of contest related to the coding contest of leetcode,codeforces,gfg,codechef ",
  instruction=CONTEST_CHATBOT_PROMPT,
  output_key="contest_bot_respone",
  tools=[google_search]
)

test_bot=LlmAgent(
  name="student_assitance",
  model=MODEL,
  description="provide the past OA and interview questions of the company name ",
  instruction="""user provides the company name , u provide the past coding and cs fundamnetal questions asked in OA'S AND INTERVIEWS related to topics which are about software and computer science related topics""",
  tools=[google_search],
  output_key="extracted_url_info"
   )