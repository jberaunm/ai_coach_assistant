from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

# from google.adk.tools import google_search  # Import the search tool
from .tools import (
    create_event,
    delete_event,
    edit_event,
    get_current_time,
    list_events,
    list_activities,
    get_weather_forecast
)

scheduler_agent = LlmAgent(
    name="scheduler_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description="Schedules the ideal time for today's run.",
    instruction=f"""
    
    You are a scheduler agent, a helpful assistant that can peform various tasks
    helping with scheduling and calendar operations and weather forecast.

    ## Calendar operations
    You can perform calendar operations directly using these tools:
    - `list_events`: Show events from your calendar for a specific time period
    - `create_event`: Add a new event to your calendar 
    - `edit_event`: Edit an existing event (change title or reschedule)
    - `delete_event`: Remove an event from your calendar
    - `find_free_time`: Find available free time slots in your calendar

    ## Weather forecast
    You can get weather forecast using the tool `get_weather_forecast`

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

strava_agent = LlmAgent(
    name="strava_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description=(
        "Agent that list activities from Strava"
    ),
    instruction=(
        "You are a strava agent, a helpful assistant that can perform various tasks "
        "helping with Strava operations."
        "## Strava operations"
        "You can perform activities operations directly using these tools:"
        "- `strava_tools3`: Show today's activities from your Strava account"
    ),
    tools=[list_activities],
)

root_agent = Agent(
    name="ai_coach_agent",
    model="gemini-2.0-flash-exp",
    description="Agent to help with scheduling and calendar operations.",
    instruction=f"""
    You are an AI coach assistant, a helpful assistant that can perform various tasks 
    helping with scheduling and calendar operations, Strava operations and weather forecast.
    
    ## Calendar operations
    You can perform calendar operations directly routing to the scheduler_agent

    ## Weather forecast
    You can retrieve weather forecast by routing to the scheduler_agent

    ## Strava operations
    You can perform Strava operations through routing to the strava_agent
    
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

    Important:
    - Be super concise in your responses and only return the information requested (not extra information).
    - NEVER show the raw response from a tool_outputs. Instead, use the information to answer the question.
    - NEVER show ```tool_outputs...``` in your response.

    Today's date is {get_current_time()}.
    """,
    tools=[
        AgentTool(agent=scheduler_agent),
        AgentTool(agent=strava_agent),
    ]
)
