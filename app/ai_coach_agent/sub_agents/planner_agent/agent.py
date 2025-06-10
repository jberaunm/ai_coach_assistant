import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from tools.training_plan_parser import parse_training_plan, get_today_session
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

planner_agent = LlmAgent(
    name="planner_agent",
    model=LiteLlm(model="mistral/mistral-small-latest"),
    description=(
        "Agent that parses marathon training plan, and adjusts if a seesions is missed."
    ),
    instruction=(
        "You are a training planner, you understand the training plan, provide today's session, and adjust if a seesion is missed."
    ),
    tools=[parse_training_plan, get_today_session],
)