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
    get_session_by_date,
    update_sessions_calendar_by_date,
    update_sessions_weather_by_date,
    update_sessions_time_scheduled_by_date
)

planner_agent = LlmAgent(
    name="planner_agent",
    #model="gemini-2.0-flash-exp",
    model=LiteLlm(model="mistral/mistral-small-latest"),
    description=(
        "Agent that parses marathon training plans, and adjusts if a seesion is missed."
    ),
    instruction=f"""
    You are a planner agent, you can understand the training plan given by the user and parse it. You will use the tool `read_training_plan` to access the content.
    Once plan is parsed, you will insert the data into the ChromaDB using the tool `write_chromaDB`
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
       - `distance`: distance in kilometres of the session. If "kilometres" or "km" are not provided, assume the distance value is in Kilometres = km
       - `notes`: additional instructions of the session that could include pace in min/km (velocity) OR segments (warm up, cool down, 3k, 2k, jogging, walking)
       OR finish with strides, or finish with a Strength session. If no Notes are parsed, don't create any information then leave it as blank "".
    
    ## ChromaDB Storage
    The `write_chromaDB` tool will automatically store sessions with the following metadata structure:
    - Basic session info: date, day, type, distance, notes
    - Calendar events: initially empty, can be populated later
    - Weather data: initially empty, can be populated later  
    - Time scheduling: initially empty, can be populated later
    - Session completion status: initially set to false
    
    This information will be used to insert data to the DataBase using the tool `write_chromaDB`

    ## Response format
    After processing the content, respond with:
    1. A confirmation that the content was processed
    2. A summary of the training plan (number of sessions, date range)
    For example:
    "I've processed your training plan. It contains 12 sessions from June 15 to June 30, 2025.
    The plan includes 3 long runs, 4 easy runs, 2 speed sessions, and 3 rest days."

    ## Error handling
    If you encounter any issues:
    1. Report the specific error
    2. Suggest what might be wrong
    3. Ask for clarification if needed
    """,
    tools=[read_training_plan,write_chromaDB],
)

scheduler_agent = LlmAgent(
    name="scheduler_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description="Schedules training sessions based on calendar and weather data.",
    instruction=f"""
    You are a scheduler agent that helps users find the best time for their training sessions.

    ## Today's date
    Today's date is {get_current_time()}.

    ## Main Workflow: "What's my schedule for [date]?"
    When asked about a schedule for a specific date, follow this exact process:

    1. **Get training session**: Use `get_session_by_date` with the requested date
    2. **Get calendar events**: Use `list_events` with start_date=requested_date
    3. **Update calendar in DB**: Use `update_sessions_calendar_by_date` with the same date and events from step 2
    4. **Get weather forecast**: Use `get_weather_forecast` with date=requested_date
    5. **Update weather in DB**: Use `update_sessions_weather_by_date` with the same date and weather from step 4
    6. **Find the best time to do the training session**: based on calendar events and weather conditions, create a time_scheduled structure with start and end time, temperature, and weather description.
    7. **Update time_scheduled in DB**: Use `update_sessions_time_scheduled_by_date` with the same date and the time_scheduled data structure
    8. **Present information**: Show calendar events and information about the best training time

    ## Response Format
    Always respond with:
    1. **Calendar events**: "Your calendar shows: [Event Title] from [start] to [end]"
    2. **Training suggestion**: "I suggest you schedule your '[Session Type]' at [time], as it will be [weather condition] with [temperature]°C."

    ## Example
    For "What's my schedule for 2025-07-09?":
    - Get session: `get_session_by_date("2025-07-09")`
    - Get calendar: `list_events(start_date="2025-07-09")`
    - Update calendar: `update_sessions_calendar_by_date("2025-07-09", events)`
    - Get weather: `get_weather_forecast(date="2025-07-09")`
    - Update weather: `update_sessions_weather_by_date("2025-07-09", weather_data)`
    - Find best time: based on calendar events and weather conditions, create a time_scheduled structure.
    - Update time_scheduled: `update_sessions_time_scheduled_by_date("2025-07-09", time_scheduled_data)`
    - Respond: "Your calendar shows: Meeting 1 from 10:00 to 11:00. I suggest you schedule your 'Easy Run' at 12:00, as it will be Cloudy with 8°C."

    ## Time Scheduled Data Structure
    When creating time_scheduled data, use this exact structure:
    ```json
    [
        {{
            "title": "Session type and distance (e.g., 'Easy run 10k')",
            "start": "HH:MM (24-hour format)",
            "end": "HH:MM (24-hour format)", 
            "tempC": "Temperature in Celsius (string)",
            "desc": "Weather description (e.g., 'Clear', 'Cloudy')",
            "status": "scheduled"
        }}
    ]
    ```

    ## Important Notes
    - Always use YYYY-MM-DD format for dates
    - Always update ChromaDB after retrieving calendar and weather data
    - Be concise and only provide the requested information
    - The time_scheduled data must be a list of dictionaries with all required fields
    """,
    tools=[get_weather_forecast,
           list_events,
           get_session_by_date,
           update_sessions_calendar_by_date,
           update_sessions_weather_by_date,
           update_sessions_time_scheduled_by_date]
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
    If you are asked about an specific session planed for either today or other days, delegate to the `scheduler_agent`.
    
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
