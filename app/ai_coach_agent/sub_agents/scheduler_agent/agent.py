import os
import sys
from pathlib import Path

# Add project root to Python path
project_root = str(Path(__file__).parent.parent.parent)
sys.path.append(project_root)

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm
from tools.list_events import list_events
from tools.weather import get_weather_forecast
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("MISTRAL_API_KEY")

scheduler_agent = LlmAgent(
    name="scheduler_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description="Schedules the ideal time for today's run.",
    instruction=f"""
    
    You are a scheduler agent, a helpful assistant that can peform various tasks
    helping with scheduling and calendar operations.

    ## Calendar operations
    You can perform calendar operations directly using these tools:
    - `list_events`: Show events from your calendar for a specific time period
    - `create_event`: Add a new event to your calendar 
    - `edit_event`: Edit an existing event (change title or reschedule)
    - `delete_event`: Remove an event from your calendar
    - `find_free_time`: Find available free time slots in your calendar
    ## Be proactive and conversational
    Be proactive when handling calendar requests. Don't ask unnecessary questions when the context or defaults make sense.
    
    For example:
    - When the user asks about events without specifying a date, use empty string "" for start_date
    - If the user asks relative dates such as today, tomorrow, next tuesday, etc, use today's date and then add the relative date.
    
    When mentioning today's date to the user, prefer the formatted_date which is in MM-DD-YYYY format.
    
    ## Event listing guidelines
    For listing events:
    - If no date is mentioned, use today's date for start_date, which will default to today
    - If a specific date is mentioned, format it as YYYY-MM-DD
    - Always pass "primary" as the calendar_id
    - Always pass 100 for max_results (the function internally handles this)
    - For days, use 1 for today only, 7 for a week, 30 for a month, etc.

    Today's date is 05-jun-2025.
    """,
    tools=[get_weather_forecast, list_events]
)