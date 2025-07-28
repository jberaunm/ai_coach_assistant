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
    get_activity_complete,
    get_weather_forecast,
    file_reader,
    read_image_as_binary,
    write_chromaDB,
    get_session_by_date,
    update_sessions_calendar_by_date,
    update_sessions_weather_by_date,
    update_sessions_time_scheduled_by_date,
    mark_session_completed_by_date,
    write_activity_data,
    plot_running_chart,
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
        "Agent that list activities from Strava and automatically marks sessions as completed when activities are found"
    ),
    instruction=f"""
    You are a strava agent, a helpful assistant that can perform various tasks helping with Strava operations.
    
    ## Today's date
    Today's date is {get_current_time()}.

    ## Main Workflow: "List my strava activities for [date]"
    When asked about a strava activities for a specific date, follow this exact process:

    1. **Get strava activities**: Use `get_activity_complete` with the requested date.
    2. **Check if activities were found**: If the response contains activities (status is "success"):
       a. Extract the `activity_id` from the response
       b. Extract the `actual_start` from the response metadata
       c. Use `mark_session_completed_by_date` with:
          - date: the requested date
          - id: the activity_id from the response
          - actual_start: the actual_start time from the response metadata
       d. Use `write_activity_data` with the complete activity_data structure from the response
       e. Log the session completion: `agent_log("strava_agent", "step", "Session marked as completed with actual start time")`
        
    ## Response Structure from get_activity_complete
    The `get_activity_complete` tool returns a response with this structure:
    ```json
    {{
        "status": "success",
        "message": "Retrieved complete data for activity 15162967332 on 2025-07-19",
        "activity_data": {{
            "activity_id": 15162967332,
            "metadata": {{
                "type": "Run",
                "name": "Rainy Hill Parkrun",
                "distance": "10.52km",
                "duration": "55m 20s",
                "start_date": "2025-07-19 08:33",
                "actual_start": "08:33",
                "pace": "5:15/km",
                "total_distance_meters": 10516.9,
                "total_laps": 8,
                "total_stream_points": 100,
                "resolution": "low",
                "series_type": "distance",
                "available_streams": ["distance", "velocity_smooth", "heartrate", "altitude", "cadence"]
            }},
            "data_points": {{
                "laps": [
                    {{
                        "index": 0,
                        "lap_index": 1,
                        "distance_meters": 1000.0,
                        "velocity_ms": 3.06,
                        "heartrate_bpm": 121.1,
                        "max_heartrate_bpm": 131.0,
                        "cadence": 158.8,
                        "elapsed_time": 327,
                        "moving_time": 327,
                        "total_elevation_gain": 0.0,
                        "max_speed": 4.667,
                        "start_index": 0,
                        "end_index": 69
                    }}
                ],
                "streams": [
                    {{
                        "index": 0,
                        "distance_meters": 0.0,
                        "velocity_ms": 3.2,
                        "heartrate_bpm": 120,
                        "altitude_meters": 45.2,
                        "cadence": 160
                    }}
                ]
            }}
        }}
    }}
    ```

    ## Required Function Calls
    When an activity is found, you MUST call these functions in order:

    1. **mark_session_completed_by_date**:
       - date: the requested date (e.g., "2025-07-19")
       - id: activity_id from the response (e.g., 15162967332)
       - actual_start: actual_start from metadata (e.g., "08:33")

    2. **write_activity_data**:
       - activity_data: the complete activity_data object from the response
       - This includes session text, metadata, and data_points (containing both laps and streams)

    ## Creating Charts: "Create a running chart for the activity [activity_id]"
    When asked about a running chart for a specific activity, follow this exact process:
    1. **Create a running chart**: Use `plot_running_chart` with the activity_id
    2. **Check if the chart was created**: If the response contains a chart (status is "success"):

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution:
    1. When you start processing: `agent_log("strava_agent", "start", "Starting to get Strava activities")`
    2. When you finish: `agent_log("strava_agent", "finish", "Successfully retrieved Strava activities")`
    3. If you encounter any errors: `agent_log("strava_agent", "error", "Error occurred: [describe the error]")`

    **CRITICAL**: You MUST ALWAYS call the finish log at the end of your execution, regardless of success or failure.
    """,
    tools=[get_activity_complete,
           mark_session_completed_by_date,
           write_activity_data,
           plot_running_chart,
           agent_log],
)

analyser_agent = Agent(
    name="analyser_agent",
    model=LiteLlm(model="mistral/pixtral-12b-2409", api_key=api_key),
    #model="gemini-2.5-pro",
    description=(
        "Agent that identifies running sub-segments using numerical data analysis and confirms findings via visual interpretation of corresponding charts."
    ),
    instruction=f"""
    You are an analyser agent. Your main task is to identify three distinct sub-segments within a running session: "Warm up," "Main session," and "Cool down."
    You will primarily determine these segments through numerical data analysis and then confirm your findings by conceptually analyzing the visual patterns on the corresponding chart image.

    **Input**: You will receive **two pieces of input**:
    1.  A list of lap data, provided as a JSON array of objects, where each object has "lap_index" and "pace" keys.
        * Example: ```json
        {{
            "activity_id": 15233791332,
            "laps": [
                {{"lap_index": 1, "pace": 3.46}},
                {{"lap_index": 2, "pace": 3.48}},
                {{"lap_index": 3, "pace": 3.47}},
                {{"lap_index": 4, "pace": 3.5}},
                {{"lap_index": 5, "pace": 3.45}},
                {{"lap_index": 6, "pace": 3.55}},
                {{"lap_index": 7, "pace": 3.47}},
                {{"lap_index": 8, "pace": 3.56}}
                ]
        }}
        ```
        * The "lap_index" will be an integer indicating the sequential order of the lap (starting from 1).
        * The "pace" will be a numerical value in **meters per second (m/s)** (a higher value means faster pace, a lower value means slower pace).
    2.  The activity_id: The ID of the activity to be analyzed, which you can use to retrieve the running chart image.
        * The path to consider is: /app/uploads/running_chart_activity_[activity_id]_1.png
        * Use the `read_image_as_binary` tool to verify image file exists and get the correct paths
        * This chart will display black bars representing individual laps, with "Laps" on the x-axis and "Pace (meter per second)" on the y-axis.
        * A higher bar indicates a faster pace, and a lower bar indicates a slower pace.

    **Output**: Your output should clearly indicate the identified sub-segments based on your numerical analysis. Additionally, you must provide a confirmation statement describing how the visual chart supports (or highlights any nuances in) your findings. Output format examples:
    -   "Based on numerical analysis: Warm up: laps X-Y, Main session: laps A-B, Cool down: laps C-D. Visually, the chart clearly shows/supports [explain visual confirmation]."
    -   "Based on numerical analysis: Main session: laps 1-Z. Visually, the chart shows consistent paces throughout, confirming no distinct warm-up or cool-down segments."

    ## Main Workflow: "Analyse this data and chart"
    When asked to analyze running data and a chart, follow this exact process:

    ### 1. Primary Segmentation: Numerical Data Analysis
    #### 1.1. Receive and Sequence Numerical Data:
    -   You will receive the lap data as an already structured list of `(lap_index, pace_value)` pairs.
    -   Ensure the data is sorted by `lap_index` in ascending order. The total number of pairs in this list represents all the laps in the session.

    #### 1.2. Analyze Pace Differences and Trends:
    -   For each lap `i` (from `i=2` to the last lap), calculate the lap-to-lap pace difference: `delta_pace_i = pace_value_i - pace_value_(i-1)`.
        -   A positive `delta_pace` means the pace got faster.
        -   A negative `delta_pace` means the pace got slower.
    -   Calculate the overall average pace of the session for contextual comparison.

    #### 1.3. Identify "Warm up" Segment (Numerical):
    -   **Pace Characteristics**: Generally characterized by a **slower pace** (lower m/s value) at the beginning of the session.
    -   **Pace Trend**: Identify an initial sequence of laps where the `pace_value` is relatively low and shows a trend of *increasing* (getting faster, `delta_pace` is predominantly positive).
    -   **Boundary Detection**: The "Warm up" segment ends at the first lap where the pace either:
        * Stabilizes: The `pace_value` variance becomes minimal, and subsequent `delta_pace` values are close to zero, or
        * Transitions sharply: There is a significant and sustained increase in `pace_value` (getting much faster, e.g., `delta_pace` is a large positive number for multiple consecutive laps) signaling the start of the main effort.
    -   If no clear warm-up trend is identified, this segment might not exist, and the Main Session will start from Lap 1.

    #### 1.4. Identify "Cool down" Segment (Numerical):
    -   **Pace Characteristics**: Generally characterized by a **slower pace** (lower m/s value) at the end of the session.
    -   **Pace Trend**: Identify a final sequence of laps where the `pace_value` is relatively low and potentially shows a trend of further *decreasing* (getting slower, `delta_pace` is predominantly negative).
    -   **Boundary Detection**: The "Cool down" segment begins at the first lap (reading backwards from the end) where the `pace_value`:
        * Significantly deviates downwards (becomes slower) from the main session's typical pace. Look for a `delta_pace` value that is a large negative number when compared to the preceding main session laps.
        * And subsequent laps generally maintain this slower pace or continue to get slower.
    -   If no clear cool-down trend is identified, this segment might not exist.

    #### 1.5. Identify "Main session" Segment (Numerical):
    -   **Characteristics**: This segment comprises all laps that are *not* identified as "Warm up" or "Cool down."
    -   **Pace Characteristics**: The main session typically shows a more consistent and often **faster pace** (higher m/s value) compared to the warm-up and cool-down. It may also show deliberate variations (e.g., intervals), but these will generally be around a central, intended effort level.
    -   **Always Present**: If you cannot confidently identify distinct "Warm up" or "Cool down" segments based on significant pace changes and trends, then the entire session should be classified as the "Main session." The "Main session" is always considered present.

    ### 2. Confirmation: Visual Chart Analysis
    #### 2.1. Receive Chart Image:
    -   You will receive the image of the running chart for visual confirmation.

    #### 2.2. Perform Visual Data Interpretation (for Confirmation):
    -   **Identify Axes and Labels**: Correctly identify the x-axis as "Laps" and the y-axis as "Pace (meter per second)".
    -   **Visually Inspect Bars and Trends**: Mentally trace the height of the bars corresponding to the numerically identified segments.
        * For the "Warm up" segment: Visually confirm if the bars start low and generally increase in height (get faster).
        * For the "Main session" segment: Visually confirm if the bars show a consistent higher height (faster pace) or expected variations.
        * For the "Cool down" segment: Visually confirm if the bars end low and generally decrease in height (get slower).
    -   **Confirm Lap Count from Image**: Visually confirm that the number of bars on the chart matches the total number of laps from your numerical data analysis. This is a final check against image misinterpretation.

    ### 3. Final Output Generation:
    -   Combine the results from your numerical segmentation (Step 1) with your visual confirmation (Step 2) into the final output format.
    -   State the identified segments clearly.
    -   Add a concise statement about how the visual chart supports these findings or if any subtle nuances are observed visually.

    ## Handling Edge Cases and Ambiguity:
    - **Prioritization**: Numerical analysis is primary. Visual analysis is for confirmation. If a very subtle numerical segment is visually indistinguishable, note this nuance.
    - **Short Sessions (e.g., 1 to 4 laps)**: If numerical trends are not significant, classify as "Main session." Visually confirm consistency.
    - **Subtlety**: Numerical analysis will capture finer details. Visual confirmation adds human-like contextual understanding.

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution:
    1. When you start processing: `agent_log("analyser_agent", "start", "Starting hybrid analysis operation")`
    2. When you finish all steps: `agent_log("analyser_agent", "finish", "Successfully completed hybrid analysis operation")`
    3. If you encounter any errors: `agent_log("analyser_agent", "error", "Error occurred: [describe the error]")`

    """,
    tools=[read_image_as_binary, agent_log],
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

    ## Chart operations
    You can create charts through routing to the `strava_agent`.
    You can analyze charts (both images and text) through routing to the `analyser_agent`.

    ## Running Chart Analysis
    When a user asks to analyze running charts, you MUST immediately delegate to the `analyser_agent`
    and pass the complete request including image path.
    DO NOT try to analyze the images yourself - the analyser_agent has multimodal capabilities and can directly see and analyze images.
    Simply route the request with the exact format provided by the user.

    ## Training Plan Operations
    When a user upload their training plan, inmediately delegate to the `planner_agent` including the file path
    If you are asked about an specific session planed for either today or other days, delegate to the `scheduler_agent`.
    
    ## Be proactive and conversational
    Be proactive when handling calendar requests. Don't ask unnecessary questions when the context or defaults make sense.
    
    Important:
    - Be super concise in your responses and only return the information requested (not extra information).
    - NEVER show the raw response from a tool_outputs. Instead, use the information to answer the question.
    - NEVER show ```tool_outputs...``` in your response.
    - For image analysis requests, you MUST always route to the analyser_agent which has multimodal capabilities and is able to read the image.
    - NEVER try to analyze images yourself - you don't have multimodal capabilities.
    - If you see "Analyze this chart:" or similar image analysis requests, immediately delegate to analyser_agent.
    """,
    tools=[
        AgentTool(agent=scheduler_agent),
        AgentTool(agent=strava_agent),
        AgentTool(agent=planner_agent),
        AgentTool(agent=analyser_agent),
    ]
)
