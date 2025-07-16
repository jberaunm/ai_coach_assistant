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
    file_reader,
    write_chromaDB,
    get_session_by_date,
    update_sessions_calendar_by_date,
    update_sessions_weather_by_date,
    update_sessions_time_scheduled_by_date,
    agent_log
)

planner_agent = LlmAgent(
    name="planner_agent",
    #model="gemini-2.0-flash-exp",
    model=LiteLlm(model="mistral/mistral-small-latest"),
    description=(
        "Agent that parses marathon training plans, and adjusts if a seesion is missed."
    ),
    instruction=f"""
    You are a planner agent, you can understand the training plan given by the user and parse it. You will use the tool `file_reader` to access the content.
    Once plan is parsed, you will insert the data into the ChromaDB using the tool `write_chromaDB`
    You can also provide Session query operations to the ChromaDB.

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution:
    1. When you start processing: `agent_log("planner_agent", "start", "Starting to process training plan")`
    2. When you finish: `agent_log("planner_agent", "finish", "Successfully processed training plan")`
    3. If you encounter any errors: `agent_log("planner_agent", "error", "Error occurred: [describe the error]")`
    
    **CRITICAL**: You MUST ALWAYS call the finish log at the end of your execution, regardless of success or failure.

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
    
    ## File path handling
    When you receive a file path:
    1. Use the exact path provided by the user
    2. If the path contains backslashes (\), they will be automatically converted to forward slashes (/)
    3. The path should point to a file in the uploads directory
    4. If you cannot read the file, report the specific error and ask the user to try uploading again
    """,
    tools=[file_reader, write_chromaDB, agent_log],
)

scheduler_agent = LlmAgent(
    name="scheduler_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description="Schedules training sessions based on calendar and weather data.",
    instruction=f"""
    You are a scheduler agent that helps users find the best time for their training sessions.

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution when starting and finishing:
    1. When you start processing: `agent_log("scheduler_agent", "start", "Starting to schedule training session")`
    2. When you finish: `agent_log("scheduler_agent", "finish", "Successfully scheduled training session")`
    3. If you encounter any errors: `agent_log("scheduler_agent", "error", "Error occurred: [describe the error]")`
    
    **CRITICAL**: You MUST ALWAYS call the finish log at the end of your execution, regardless of success or failure.

    ## Today's date
    Today's date is {get_current_time()}.

    ## Main Workflow: "What's my schedule for [date]?"
    When asked about a schedule for a specific date, follow this exact process:

    1. **Get training session**: Use `get_session_by_date` with the requested date
    2. **Get calendar events**: Use `list_events` with start_date=requested_date
    3. **Check for existing AI training session**: Look through the calendar events from step 2. If any event has a title ending with "AI Coach Session", then a training session has already been scheduled for this date.
    4. **If AI session exists**: Inform the user that the session has already been scheduled and proceed to step 6.
    5. **If no AI session exists**: Continue with the following steps:
       a. **Get weather forecast**: Use `get_weather_forecast` with date=requested_date
       b. **Find the best time to do the training session**: based on calendar events and weather conditions, create a time_scheduled structure with start and end time, temperature, and weather description.
       c. **Create training session event**: Use `create_event` to add the suggested training session to the calendar with:
          - date: the requested date
          - start_time: from the time_scheduled structure
          - end_time: from the time_scheduled structure  
          - title: "[Session Type] [distance] - AI Coach Session" (e.g., "Easy Run 10k - AI Coach Session")
       d. **Update calendar in DB**: Use `update_sessions_calendar_by_date` with the same date and events from step 2, including the newly created event in step 5c, using start_time, end_time and title.
       e. **Update weather in DB**: Use `update_sessions_weather_by_date` with the same date and weather from step 5a
       f. **Update time_scheduled in DB**: Use `update_sessions_time_scheduled_by_date` with the same date and the time_scheduled data structure
    6. **Present information**: Show calendar events and information about the training session

    **IMPORTANT**: You MUST execute ALL steps in order. If an AI training session already exists, skip the creation steps but still inform the user and complete the workflow.

    ## Response Format
    Always respond with:
    1. **Calendar events**: "Your calendar shows: [Event Title] from [start] to [end]"
    2. **If AI session already exists**: "Your training session has already been scheduled for this date. You can see it in your calendar above."
    3. **If new session created**: "I've scheduled your '[Session Type] [distance]' from [start_time] to [end_time], as it will be [weather condition] with [temperature]°C."

    ## Example
    For "What's my schedule for 2025-07-09?":
    - Get session: `get_session_by_date("2025-07-09")`
    - Get calendar: `list_events(start_date="2025-07-09")`
    - Check for AI session: Look for events ending with "AI Coach Session"
    - If AI session exists: Respond with "Your training session has already been scheduled for this date. You can see it in your calendar above."
    - If no AI session exists:
      - Get weather: `get_weather_forecast(date="2025-07-09")`
      - Find best time: based on calendar events and weather conditions, create a time_scheduled structure.
      - Create event: `create_event("2025-07-09", "12:00", "13:00", "Easy Run 10k - AI Coach Session")`
      - Update calendar: `update_sessions_calendar_by_date("2025-07-09", events)` (including the new event)
      - Update weather: `update_sessions_weather_by_date("2025-07-09", weather_data)`
      - Update time_scheduled: `update_sessions_time_scheduled_by_date("2025-07-09", time_scheduled_data)`
      - Respond: "Your calendar shows: Meeting 1 from 10:00 to 11:00. I've scheduled your 'Easy Run 10k' from 12:00 to 13:00, as it will be Cloudy with 8°C."
    - In both cases, complete the workflow and provide the response.

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
           create_event,
           get_session_by_date,
           update_sessions_calendar_by_date,
           update_sessions_weather_by_date,
           update_sessions_time_scheduled_by_date,
           agent_log]
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
        
        "## Logging Instructions"
        "You MUST use the `agent_log` tool to log your execution:"
        "1. When you start processing: `agent_log(\"strava_agent\", \"start\", \"Starting to get Strava activities\")`"
        "2. When you finish: `agent_log(\"strava_agent\", \"finish\", \"Successfully retrieved Strava activities\")`"
        "3. If you encounter any errors: `agent_log(\"strava_agent\", \"error\", \"Error occurred: [describe the error]\")`"
        
        "**CRITICAL**: You MUST ALWAYS call the finish log at the end of your execution, regardless of success or failure."
    ),
    tools=[list_activities, agent_log],
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
