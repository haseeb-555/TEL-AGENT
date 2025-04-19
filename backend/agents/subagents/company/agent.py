from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from .prompts import STRUCTURE_PROMPT, CRITIC_PROMPT, FORMATTER_PROMPT
from google.adk.agents.loop_agent import LoopAgent

# --- State Keys ---
STATE_STRUCTURED_INFO = "structured_deadline_data"
STATE_CRITIC_FEEDBACK = "critic_feedback"
STATE_FINAL_FORMAT = "formatted_company_info"

MODEL = "gemini-2.0-flash-exp"

# --- Agent 1: Extract Structured Data from Company Email ---
company_structure_agent = LlmAgent(
    name="CompanyStructureAgent",
    model=MODEL,
    instruction=STRUCTURE_PROMPT,
    output_key=STATE_STRUCTURED_INFO,
    tools=[google_search],
)

# --- Agent 2: Critic Agent to verify Company Info ---
company_critic_agent = LlmAgent(
    name="CompanyCriticAgent",
    model=MODEL,
    instruction=CRITIC_PROMPT,
    output_key=STATE_CRITIC_FEEDBACK,
    tools=[google_search],
)

# --- Agent 3: Formatter Agent to output final Company JSON ---
company_formatter_agent = LlmAgent(
    name="CompanyFormatterAgent",
    model=MODEL,
    instruction=FORMATTER_PROMPT,
    output_key=STATE_STRUCTURED_INFO,  # Rewrites the same key with formatted JSON
)

# Define the root agent using Loop
root_agent1 = LoopAgent(
    name="MainCompanyloopAgent",
    max_iterations=3,
    sub_agents=[company_structure_agent,company_critic_agent,company_formatter_agent]
    
)

# root_agent=LlmAgent(
#     name="MainCompanyRootAgent",
#     instruction="the input must be passed to agent call `MainCompanyloopAgent`",
#     output_key=STATE_FINAL_FORMAT,
#     model=MODEL,
#     sub_agents=[root_agent1]
# )

root_agent=LlmAgent(
    name="extract_deadline_agent",
    description="extracts the deadline",
    model=MODEL,
    instruction="extract the deadline from the input in the standard time format",
    output_key="deadline"
)