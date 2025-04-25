from google.adk.agents.llm_agent import LlmAgent
from google.adk.tools import google_search
from .prompts import CLASSIFIER_PROMPT


MODEL = "gemini-2.0-flash-exp"
classifier_root=LlmAgent(
  name="classifier_agent",
  description="classifies the email into company or contest or medical or travel or spam ",
  instruction=CLASSIFIER_PROMPT,
  model=MODEL,
  output_key="mail_class"
)

