from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from google.adk.agents.loop_agent import LoopAgent
from .prompts import CHAT_BOT_PROMPT


MODEL = "gemini-2.0-flash-exp"
chat_bot_root=LlmAgent(
  name="chat_bot_agent",
  description="extract the latest news about technology",
  instruction=CHAT_BOT_PROMPT,
  model=MODEL,
  tools=[google_search],
  output_key="chat_bot_reply"
)