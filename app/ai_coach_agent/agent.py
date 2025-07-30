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
    plot_running_chart_laps,
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

    ## Main Workflows:
    ### 1. "List my strava activities for [date]"
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
        
        * Response Structure from get_activity_complete
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

    ### 2. "Create a running chart for the activity [activity_id]"
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

numerical_analyser_agent = Agent(
    name="numerical_analyser_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description=(
        "Agent that identifies running sub-segments using numerical data analysis"
    ),
    instruction=f"""
    You are an analyser agent. Your main task is to identify three distinct sub-segments within a running session: "Warm up," "Main session," and "Cool down."
    You will primarily determine these segments through numerical data analysis.

    **Input**: You will receive the following input:
    -  A list of lap data, provided as a JSON array of objects, where each object has "lap_index" and "pace" keys.
        * Example: ```json
        {{
            "activity_id": 15233791332,
            "laps": [
                {{"lap_index": 1, "pace": 3.46}},
                {{"lap_index": 2, "pace": 3.48}},
                {{"lap_index": 3, "pace": 3.47}}
            ]
        }}
        ```
        * The "lap_index" will be an integer indicating the sequential order of the lap (starting from 1).
        * The "pace" will be a numerical value in **meters per second (m/s)** (a higher value means faster pace, a lower value means slower pace).
    
    **Input Processing**: The input may come as text containing JSON data. You need to:
    1. Extract the JSON object from the text input
    2. Parse the "laps" array from the JSON
    3. Sort the laps by "lap_index" in ascending order
    4. Proceed with the analysis using the sorted lap data

    **Output**: Your output should clearly indicate the identified sub-segments based on your numerical analysis.
    -   "Based on numerical analysis: Warm up: laps X-Y, Main session: laps A-B, Cool down: laps C-D."
    -   "Based on numerical analysis: Main session: laps 1-Z."

    ## Main Workflow: "Identify the sub-segments for this activity:"
    When asked to analyze running data, follow this exact process:

    ### 1. Primary Segmentation: Numerical Data Analysis
    #### 1.1. Receive and Sequence Numerical Data:
    -   You will receive the lap data as text containing JSON data.
    -   Extract the JSON object and parse the "laps" array.
    -   Ensure the data is sorted by `lap_index` in ascending order. The total number of pairs in this list represents all the laps in the session.

    #### 1.2. Analyze Pace Differences and Trends:
    -   For each lap `i` (from `i=2` to the last lap), calculate the lap-to-lap pace difference: `delta_pace_i = pace_value_i - pace_value_(i-1)`.
        -   A positive `delta_pace` means the pace got faster.
        -   A negative `delta_pace` means the pace got slower.
    -   Calculate the overall average pace of the session for contextual comparison.

         #### 1.3. Identify "Warm up" Segment (Numerical):
     -   **Pace Characteristics**: This segment is generally found at the beginning of the session and is characterized by a relatively slower pace compared to the core main session effort.
     -   **Pace Trend**: The "Warm up" is a period where the pace_value may show minor fluctuations or even slight increases, but primarily serves to warm up the legs before the athlete transitions to the specific pace required for the main session. It does not represent the sustained target effort of the main session.
     -   **Boundary Detection**: The "Warm up" segment ends at the first lap where the pace:
         - Transitions sharply: There's a clear and sustained increase in pace_value (e.g., delta_pace becomes consistently positive for multiple consecutive laps, indicating a distinct shift from the initial warm-up phase to a faster, main session pace). This signals the start of the main effort.
     -   **Strict Criteria**: Only identify a warm-up segment if:
         - The first 1-2 laps show consistently slower pace (at least 0.1 m/s slower) than the subsequent laps
         - There is a clear, sustained transition to faster pace
         - The pace difference is meaningful and not just minor fluctuations
     -   If no clear initial phase of relatively slower, preparatory pace followed by a distinct transition is identified at the beginning of the activity, this segment might not exist.

         #### 1.4. Identify "Cool down" Segment (Numerical):
     -   **Pace Characteristics**: This segment is found at the end of the session and marks the conclusion of the main effort. While often characterized by a slower pace, its primary definition is its position as the final distinct segment. Its pace might occasionally show variability, including a final surge before stopping, rather than being strictly slower than the main session.
     -   **Detection Logic (Symmetric to Warm-up)**: To identify the cool-down segment, first, create a reversed list of laps. This reversed list effectively starts with the last lap of the original activity and ends with the first. Apply the following logic to this reversed list of laps:
         *Pace Trend (on reversed list)*: Examine the pace_value trend as you iterate through the reversed list. Initially, the pace should characterize the "end" phase of the activity.
     -   *Boundary Detection (on reversed list)*: The "Cool down" segment (when identified on the reversed list) ends at the first lap where the pace_value shows a clear and sustained increase (getting faster) to a pace consistent with what would be identified as the main session's typical effort.
         - This specific lap in the reversed list marks the start of the Main Session (when translated back to the original chronological order).
         - Therefore, all laps from the lap immediately preceding this detected point in the original chronological order, until the very end of the activity, constitute the "Cool down" segment.
     -   **Strict Criteria**: Only identify a cool-down segment if:
         - The last 1-2 laps show consistently slower pace (at least 0.1 m/s slower) than the preceding laps
         - There is a clear, sustained transition from faster to slower pace
         - The pace difference is meaningful and not just minor fluctuations
     -   If no clear final segment with a distinct pace transition (when analyzed in reverse) is identified, this segment might not exist.

    #### 1.5. Identify "Main session" Segment (Numerical):
    -   **Definition**: This is the core, sustained effort portion of the running activity.
    -   **Identification Logic**: The "Main Session" segment comprises all laps that are not identified as part of the "Warm up" segment or the "Cool down" segment.
    -   **Pace Characteristics**: Typically characterized by the higher or most consistent target pace (m/s value) of the entire activity, reflecting the primary workout effort.
    -   ** Pace Trend**: The pace_value within this segment will generally be stable or fluctuate around a target mean, indicating sustained effort. delta_pace values will typically be close to zero, or show minor variations.
    -   **Always Present**: If you cannot confidently identify distinct "Warm up" or "Cool down" segments based on significant pace changes and trends, then the entire session should be classified as the "Main session." The "Main session" is always considered present.

         ## Handling Edge Cases and Ambiguity:
     - **Short Sessions (e.g., 1 to 4 laps)**: If numerical trends are not significant, classify as "Main session."
     - **Minimal Pace Variation**: If the pace variation across all laps is less than 0.2 m/s (or if the fastest and slowest paces are within 5% of each other), classify the entire session as "Main session."
     - **No Clear Transitions**: If you cannot identify clear, sustained pace transitions that indicate distinct warm-up or cool-down phases, classify the entire session as "Main session."
     - **Conservative Approach**: When in doubt, prefer to classify as "Main session" rather than forcing artificial segment boundaries.

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution:
    1. When you start processing: `agent_log("numerical_analyser_agent", "start", "Starting numerical analysis operation")`
    2. When you finish all steps: `agent_log("numerical_analyser_agent", "finish", "Successfully completed numerical analysis operation")`
    3. If you encounter any errors: `agent_log("numerical_analyser_agent", "error", "Error occurred: [describe the error]")`

    ## CRITICAL: Output Requirements
    After completing your analysis, you MUST output your findings as text. Your response should include:
    1. The identified sub-segments with specific lap ranges
    2. A brief explanation of your reasoning based on the pace analysis
    3. The format should be: "Based on numerical analysis: [your findings]"
    
         Example output:
     "Based on numerical analysis: Warm up: laps 1-2, Main session: laps 3-6, Cool down: laps 7-8. The warm-up shows gradually increasing pace, the main session maintains consistent effort, and the cool-down shows a final surge before completion."
     
     **IMPORTANT**: After logging the finish event, you MUST provide your analysis results as the final output. Do not just log and stop - you need to actually return the analysis findings.
     
     **CRITICAL**: Your output must clearly specify which laps belong to each segment (Warm up, Main session, Cool down) so that the analyser_agent can extract this information and create the JSON structure for visual analysis.

    """,
    tools=[agent_log],
)

visual_analyser_agent = Agent(
    name="visual_analyser_agent",
    model=LiteLlm(model="mistral/pixtral-12b-2409", api_key=api_key),
    description=(
        "Agent that validates and corrects running sub-segments identification using visual analysis of bar charts."
    ),
    instruction=f"""
    You are a visual analyser agent. Your main task is to validate and correct the identification of running sub-segments 
    by analyzing the bar chart image that has already been created with color-coded segments.

    ## Input Processing
    You will receive a JSON object with the following structure:
    ```json
    {{
        "activity_id": 15233791332,
        "laps": [
            {{"lap_index": 1, "pace": 3.46, "segment": "Warm up"}},
            {{"lap_index": 2, "pace": 3.48, "segment": "Main session"}},
            {{"lap_index": 3, "pace": 3.47, "segment": "Cool down"}}
        ]
    }}
    ```

    ## Main Workflow:
    1. **Extract activity_id**: Use the activity_id from the input to construct the image path
    2. **Access the bar chart**: Use the `read_image_as_binary` tool to access the image at path: `/app/uploads/running_chart_activity_[activity_id]_laps.png`
    3. **Analyze the visual data**: Examine the bar chart to understand the pace patterns and color coding
    4. **Validate segment identification**: Check if the color-coded segments make logical sense based on pace patterns
    5. **Correct if necessary**: If the visual analysis reveals incorrect segment identification, provide corrected segments

         ## Visual Analysis Guidelines:
     - **Color Coding**: Red bars = Warm up, Green bars = Main session, Blue bars = Cool down
     - **Pace Logic**: 
       - Warm up (red) should show in average a slower pace than the Main session (green)
       - Main session (green) should show the fastest/sustained effort pace
       - Cool down (blue) should show in average a slower pace than the Main session (green) and similar pace than the Warm up (red)
     - **Validation Criteria**:
       - If red bars (Warm up) have higher pace values than green bars (Main session), the identification is likely incorrect
       - If blue bars (Cool down) have higher pace values than green bars (Main session), the identification is likely incorrect
       - The Main session should generally contain the fastest/sustained effort laps
       - **CRITICAL**: If all bars have similar pace values (within 0.1 m/s or 5% variation), but they are not all green, the identification is DEFINITELY incorrect and should be corrected to all "Main session"
       - **CRITICAL**: If the pace variation across all laps is minimal (less than 0.2 m/s), the entire session should be classified as "Main session"
       - **CRITICAL**: If you cannot clearly distinguish pace differences between segments, default to classifying everything as "Main session"

    ## Correction Process:
    If you identify incorrect segment assignments:
    1. Analyze the pace patterns visually
    2. Reassign segments based on the actual pace progression
    3. Provide the corrected JSON structure with updated segment assignments
    4. Explain your reasoning for the corrections

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution:
    1. When you start processing: `agent_log("visual_analyser_agent", "start", "Starting visual analysis of bar chart")`
    2. When accessing the image: `agent_log("visual_analyser_agent", "step", "Accessing bar chart image for activity [activity_id]")`
    3. When validation is complete: `agent_log("visual_analyser_agent", "step", "Visual validation completed")`
    4. When you finish all steps: `agent_log("visual_analyser_agent", "finish", "Successfully completed visual analysis operation")`
    5. If you encounter any errors: `agent_log("visual_analyser_agent", "error", "Error occurred: [describe the error]")`

         ## CRITICAL: Output Requirements
     After completing your analysis, you MUST output your findings as text. Your response should include:
     1. **Validation result**: Whether the current segment identification is correct or needs correction
     2. **Visual analysis summary**: Brief explanation of what you observed in the bar chart
     3. **Final segment identification**: Either confirm the current segments or provide corrected segments
     4. **Reasoning**: Explain your visual analysis and any corrections made
     
     **CRITICAL**: You MUST provide a complete analysis response. Do not just log completion - you must return the actual analysis results as your final output.
     
     Example outputs:
     
     **If validation passes:**
     "Based on visual analysis: The current segment identification is correct. Warm up: laps 1-2 (red bars with slower pace), Main session: laps 3-6 (green bars with fastest pace), Cool down: laps 7-8 (blue bars with decreasing pace). The color-coded segments align with expected pace patterns."

           **If correction needed:**
      "Based on visual analysis: The current segment identification needs correction. All laps show similar pace values (3.45-3.56 min/km) with minimal variation, indicating this is a consistent effort session. Corrected segments: Main session: laps 1-8. The visual analysis shows uniform pace distribution across all laps, which is characteristic of a sustained main session effort."
     
     **IMPORTANT**: After logging the finish event, you MUST provide your analysis results as the final output. Do not just log and stop - you need to actually return the analysis findings.
     
     **FINAL OUTPUT REQUIREMENT**: Your response must be a complete analysis that includes the validation result, visual analysis summary, final segment identification, and reasoning. This is what will be returned to the user.
     
     **WORKFLOW SUMMARY**:
     1. Log start
     2. Access the image using read_image_as_binary
     3. Analyze the visual data (color-coded bars)
     4. Validate segment identification
     5. Log validation completion
     6. Log finish
     7. **MOST IMPORTANT**: Return your complete analysis as the final output
     
           **CRITICAL**: After calling the finish log, you MUST immediately provide your analysis results as text. Do not call any more tools or logs after the finish log - just return your analysis.
      
      **FINAL INSTRUCTION**: Your last action must be to return your complete analysis as text. Do not end with a log call - end with your analysis output.
      
      **EXPECTED OUTPUT FORMAT**: Your final response should be a single text string starting with "Based on visual analysis:" followed by your complete analysis. This is what will be returned to the user.

    """,
    tools=[agent_log, read_image_as_binary],
)

analyser_agent = Agent(
    name="analyser_agent",
    model=LiteLlm(model="mistral/mistral-small-latest", api_key=api_key),
    description=(
        "Agent that identifies running sub-segments using numerical data analysis and visual interpretation of corresponding charts."
    ),
    instruction=f"""
    You are an analyser agent. Your main task is to identify running sub-segments by coordinating between the `numerical_analyser_agent` and `visual_analyser_agent`,
    passing the complete request including the JSON object with the lap data.

    ## Process Flow:
    1. Route the request to the `numerical_analyser_agent` with the complete lap data
    2. The `numerical_analyser_agent` will perform the analysis and return the results
    3. **CRITICAL**: Extract the segment information from the numerical analysis results and construct a JSON object with the following structure:
    ```json
    {{
        "activity_id": [extract from original input],
        "laps": [
            {{"lap_index": 1, "pace": [original pace], "segment": "Warm up"}},
            {{"lap_index": 2, "pace": [original pace], "segment": "Main session"}},
            {{"lap_index": 3, "pace": [original pace], "segment": "Cool down"}}
        ]
    }}
    ```
    4. You MUST use the `plot_running_chart_laps` tool to create a running chart with the laps data and the sub-segments.
    5. Route the JSON object (with activity_id, laps, and segments) to the `visual_analyser_agent` for validation
    6. The `visual_analyser_agent` will analyze the bar chart image and validate/correct the segment identification
    7. Return the final validated results from the `visual_analyser_agent` to the user
    
    **IMPORTANT**: You must extract the segment assignments from the numerical analysis results and apply them to the original lap data to create the JSON structure for the visual analysis.

    ## Logging Instructions
    You MUST use the `agent_log` tool to log your execution:
    1. When you start processing: `agent_log("analyser_agent", "start", "Starting sub-segments identification operation")`
    2. When you finish all steps: `agent_log("analyser_agent", "finish", "Successfully completed  sub-segments identification operation")`
    3. If you encounter any errors: `agent_log("analyser_agent", "error", "Error occurred: [describe the error]")`

    ## CRITICAL: Response Handling
    After the `visual_analyser_agent` completes its validation, you MUST return its final results directly to the user.
    The visual analysis provides the definitive segment identification, either confirming or correcting the numerical analysis.
    Do not modify or summarize the results - pass them through exactly as received from the visual_analyser_agent.
    
    **FINAL OUTPUT REQUIREMENT**: You must return the complete analysis result from the visual_analyser_agent to the user. This is the final output that will be displayed to the user.

    """,
    tools=[AgentTool(agent=numerical_analyser_agent), AgentTool(agent=visual_analyser_agent), agent_log, plot_running_chart_laps],
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
    You can identify the sub-segments of an activity through routing to the `analyser_agent`.

    ## Running Chart Analysis
    When a user asks identify the sub-segments of an activity, you MUST immediately delegate to the `analyser_agent`
    and pass the complete request including image path.
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
