from google.adk.agents import Agent
from google.adk.tools.agent_tool import AgentTool

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm

import os
from dotenv import load_dotenv
load_dotenv()
api_key = os.getenv("MISTRAL_API_KEY")

from datetime import datetime

def get_current_time():
    return datetime.now().strftime("%Y-%m-%d")

# from google.adk.tools import google_search  # Import the search tool
from .tools import (
    create_event,
    delete_event,
    edit_event,
    get_current_time,
    list_events,
    list_activities,
    get_weather_forecast,
    read_training_plan,
    write_chromaDB,
    get_session_by_date
)

planner_agent = LlmAgent(
    name="planner_agent",
    model="gemini-2.0-flash-exp",
    #model=LiteLlm(model="mistral/mistral-small-latest"),
    description=(
        "Agent that parses marathon training plans, and adjusts if a seesion is missed."
    ),
    instruction=f"""
    You are a planner agent, you can understand the training plan given by the user and parse it. You will use the tool `read_training_plan` to access the content.
    Once plan is parsed, you will insert the data into the ChromaDB using the tool `write_ChromaDB`
    You can also provide Session query operations to the ChromaDB.

    ## Today's date
    Today's date is {get_current_time()}.

    ## Date format
    When storing or querying dates in ChromaDB, always use the format YYYY-MM-DD.

    ## Parsing instructions
    When you receive file, analyze it and extract the following information:
       - `date`: date of the session planned.
       - `day`: day of the week.
       - `type`: type of session, including `Easy Run`, `Long Run`, `Speed Session`, `Hill Session`, `Tempo` or `Rest` when no session is planned
       - `distance`: distance in kilometres of the session. If "kilometres" or "km" are not provided, asume the distance value is in Kilometres = km
       - `notes`: additional instructions of the session that could include pace in min/km (velocity) OR segments (warm up, cool down, 3k, 2k, jogging, walking)
       OR finish with strides, or finish with a Strength session. If no Notes are parsed, don't create any informatkonthen leave it as blank "".
    This information will be used to insert data to the DataBase using the tool `write_chromaDB`

    ## Response format
    After processing the content, respond with:
    1. A confirmation that the content was processed
    2. A summary of the training plan (number of sessions, date range)
    For example:
    "I've processed your training plan. It contains 12 sessions from June 15 to June 30, 2025.
    The plan includes 3 long runs, 4 easy runs, 2 speed sessions, and 3 rest days.

    ## Session Query operations 
    To provide session information for an specific date, use the tool `get_session_by_date`, which expects the argument `date` in YYYY-MM-DD format.

    ## Error handling
    If you encounter any issues:
    1. Report the specific error
    2. Suggest what might be wrong
    3. Ask for clarification if needed
    """,
    tools=[read_training_plan,write_chromaDB,get_session_by_date],
)

scheduler_agent = LlmAgent(
    name="scheduler_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description="Schedules the ideal time for today's run.",
    instruction=f"""
    
    You are a scheduler agent, a helpful assistant that can peform various tasks
    helping with scheduling and calendar operations and weather forecast.

    ## Today's date
    Today's date is {get_current_time()}.
    If the user asks relative dates such as today, tomorrow, next tuesday, etc, use today's date and then add the relative date.

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
    
    ## Event listing guidelines
    For listing events:
    - If no date is mentioned, use today's date for start_date, which will default to today
    - If a specific date is mentioned, format it as YYYY-MM-DD
    - Always pass "primary" as the calendar_id
    - Always pass 100 for max_results (the function internally handles this)
    - For days, use 1 for today only, 7 for a week, 30 for a month, etc.
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
    helping with scheduling and calendar operations, Strava operations, weather forecast and Training Plan Operations.

    ## Today's date
    Today's date is {get_current_time()}.
    If the user asks relative dates such as today, tomorrow, next tuesday, etc, use today's date and then add the relative date.

    ## Calendar operations
    You can perform calendar operations directly routing to the `scheduler_agent`.

    ## Weather forecast
    You can retrieve weather forecast by routing to the `scheduler_agent`.

    ## Strava operations
    You can perform Strava operations through routing to the `strava_agent`.

    ## Training Plan Operations
    When a user upload their training plan, inmediately delegate to the `planner_agent` including the file path
    If you are asked about an specific session planed for either today or other days, delegate to the `planner_agent`.
    
    ## Be proactive and conversational
    Be proactive when handling calendar requests. Don't ask unnecessary questions when the context or defaults make sense.
    
    Important:
    - Be super concise in your responses and only return the information requested (not extra information).
    - NEVER show the raw response from a tool_outputs. Instead, use the information to answer the question.
    - NEVER show ```tool_outputs...``` in your response.
    """,
    tools=[
        AgentTool(agent=scheduler_agent),
        AgentTool(agent=strava_agent),
        AgentTool(agent=planner_agent),
    ]
)
