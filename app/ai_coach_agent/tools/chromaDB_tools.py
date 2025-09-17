import json
from db.chroma_service import chroma_service
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class CalendarEvent(BaseModel):
    title: str
    start: str
    end: str

class WeatherHour(BaseModel):
    time: str
    tempC: str
    desc: str

class TimeScheduled(BaseModel):
    title: str
    start: str
    end: str
    tempC: str
    desc: str
    status: str
    actual_start: Optional[str] = None  # "14:30" - when session actually started (time only)

class Metadata(BaseModel):
    date: str                    # "2025-06-17"
    day: str                     # "Tuesday"
    type: str                    # "Easy Run"
    distance: Optional[float] = None
    notes: Optional[str] = None
    calendar: Optional[Dict[str, List[CalendarEvent]]] = None
    weather: Optional[Dict[str, List[WeatherHour]]] = None
    time_scheduled: Optional[List[TimeScheduled]] = None
    session_completed: bool = False

class SessionData(BaseModel):
    id: str
    document: str
    embedding: List[float]
    metadata: Metadata

# New models for activity data with streams
class ActivityDataPoint(BaseModel):
    index: int
    distance_meters: Optional[float] = None
    velocity_ms: Optional[float] = None
    heartrate_bpm: Optional[int] = None
    altitude_meters: Optional[float] = None
    cadence: Optional[int] = None

class ActivityMetadata(BaseModel):
    activity_id: int
    calendar: Optional[Dict[str, List[CalendarEvent]]] = None
    date: str
    day: str
    distance: str
    notes: str = ""
    session_completed: bool = False
    time_scheduled: Optional[List[TimeScheduled]] = None
    type: str
    weather: Optional[Dict[str, List[WeatherHour]]] = None

class ActivityData(BaseModel):
    session: str
    metadata: ActivityMetadata
    data_points: Optional[List[ActivityDataPoint]] = None

def write_chromaDB(sessions: List[Dict[str, Any]]):
    """Store training plan sessions in ChromaDB.
    
    Args:
        sessions: List of session dictionaries. Each session should have:
            - date: str
            - day: str
            - type: str
            - distance: float
            - notes: Optional[str]
            - calendar: Optional[Dict] (will be initialized empty)
            - weather: Optional[Dict] (will be initialized empty)
            - time_scheduled: Optional[List] (will be initialized empty)
        
    Returns:
        Dict with status and message
    """
    try:
        # Use the store_training_plan method from ChromaService
        result = chroma_service.store_training_plan(
            sessions=sessions,
            metadata={"source": "training_plan_parser"}
        )
        
        if result == "success":
            return {
                "status": "success",
                "message": f"Successfully stored {len(sessions)} sessions with new metadata structure",
                "plan_id": "plan_001"  # You might want to generate a unique ID
            }
        else:
            return {
                "status": "error",
                "message": f"Error storing sessions: {result}",
                "plan_id": None
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error storing sessions: {str(e)}",
            "plan_id": None
        }

def get_session_by_date(date: str):
    """
    Retrieves today's training session from the database.
    Returns:
        dict: The session for today in YYYY-MM-DD format, or a message if none found.
    """
    print(f"[chromaDB_tools] Getting session by date: {date}")
    session = chroma_service.get_session_by_date(date)
    if session:
        return {"session": session}
    else:
        return {"session": "No session found for today."}

def update_sessions_calendar_by_date(date: str, calendar_events: list):
    """Update calendar events for all sessions on a specific date.
    
    Args:
        date: The date in YYYY-MM-DD format
        calendar_events: Calendar events data (will extract events array from different possible structures)
        
    Returns:
        Dict with status and message
    """
    try:
        # Get all sessions for the specified date
        results = chroma_service.collection.get(where={"date": date})
        
        if not results['ids']:
            return {
                "status": "error",
                "message": f"No sessions found for date: {date}"
            }
        
        # Extract the events array from the calendar data
        # Handle different possible structures from calendar APIs
        events_data = []
        if isinstance(calendar_events, dict):
            # If calendar_events has a nested "calendar" key with "events"
            if "calendar" in calendar_events and isinstance(calendar_events["calendar"], dict):
                events_data = calendar_events["calendar"].get("events", [])
            # If calendar_events directly has "events"
            elif "events" in calendar_events:
                events_data = calendar_events["events"]
            # If calendar_events is already the events array
            elif isinstance(calendar_events, list):
                events_data = calendar_events
        elif isinstance(calendar_events, list):
            # If calendar_events is already the events array
            events_data = calendar_events
        
        # Create the expected calendar structure
        calendar_structure = {
            "events": events_data
        }
        
        # Update each session's calendar metadata
        for i, session_id in enumerate(results['ids']):
            current_metadata = results['metadatas'][i]
            
            # Update calendar events with the simplified structure
            current_metadata['calendar'] = json.dumps(calendar_structure)
            
            # Update the session
            chroma_service.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
        
        return {
            "status": "success",
            "message": f"Successfully updated calendar for {len(results['ids'])} sessions on {date}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating sessions calendar by date: {str(e)}"
        }

def update_sessions_weather_by_date(date: str, weather_data: dict):
    """Update weather data for all sessions on a specific date.
    
    Args:
        date: The date in YYYY-MM-DD format
        weather_data: Weather data from API (will extract hours array from nested structure)
        
    Returns:
        Dict with status and message
    """
    try:
        # Get all sessions for the specified date
        results = chroma_service.collection.get(where={"date": date})
        
        if not results['ids']:
            return {
                "status": "error",
                "message": f"No sessions found for date: {date}"
            }
        
        # Extract the hours array from the weather data
        # Handle different possible structures from the weather API
        hours_data = []
        if isinstance(weather_data, dict):
            # If weather_data has a nested "weather" key with "hours"
            if "weather" in weather_data and isinstance(weather_data["weather"], dict):
                hours_data = weather_data["weather"].get("hours", [])
            # If weather_data directly has "hours"
            elif "hours" in weather_data:
                hours_data = weather_data["hours"]
            # If weather_data is already the hours array
            elif isinstance(weather_data, list):
                hours_data = weather_data
        
        # Filter hours to only include specific times: 06:00, 09:00, 12:00, 15:00, 18:00
        target_hours = ["06:00", "09:00", "12:00", "15:00", "18:00"]
        filtered_hours = []
        
        for hour_data in hours_data:
            if isinstance(hour_data, dict) and "time" in hour_data:
                # Check if the time matches any of our target hours
                if hour_data["time"] in target_hours:
                    filtered_hours.append(hour_data)
        
        # Create the expected weather structure with filtered hours
        weather_structure = {
            "hours": filtered_hours
        }
        
        # Update each session's weather metadata
        for i, session_id in enumerate(results['ids']):
            current_metadata = results['metadatas'][i]
            
            # Update weather data with the filtered structure
            current_metadata['weather'] = json.dumps(weather_structure)
            
            # Update the session
            chroma_service.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
        
        return {
            "status": "success",
            "message": f"Successfully updated weather for {len(results['ids'])} sessions on {date} with {len(filtered_hours)} filtered hours"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating sessions weather by date: {str(e)}"
        }

def update_sessions_time_scheduled_by_date(date: str, time_scheduled_data: list):
    """Update time_scheduled data for all sessions on a specific date.
    
    Args:
        date: The date in YYYY-MM-DD format
        time_scheduled_data: List of time scheduled items with structure:
            [
                {
                    "title": str,
                    "start": str,
                    "end": str,
                    "tempC": str,
                    "desc": str,
                    "status": str
                }
            ]
        
    Returns:
        Dict with status and message
    """
    try:
        # Get all sessions for the specified date
        results = chroma_service.collection.get(where={"date": date})
        
        if not results['ids']:
            return {
                "status": "error",
                "message": f"No sessions found for date: {date}"
            }
        
        # Validate and prepare time_scheduled data
        validated_time_scheduled = []
        if isinstance(time_scheduled_data, list):
            for item in time_scheduled_data:
                if isinstance(item, dict):
                    # Ensure all required fields are present
                    required_fields = ["title", "start", "end", "tempC", "desc", "status"]
                    if all(field in item for field in required_fields):
                        validated_time_scheduled.append(item)
        
        # Update each session's time_scheduled metadata
        for i, session_id in enumerate(results['ids']):
            current_metadata = results['metadatas'][i]
            
            # Update time_scheduled data
            current_metadata['time_scheduled'] = json.dumps(validated_time_scheduled)
            
            # Update the session
            chroma_service.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
        
        return {
            "status": "success",
            "message": f"Successfully updated time_scheduled for {len(results['ids'])} sessions on {date}"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating sessions time_scheduled by date: {str(e)}"
        }

def mark_session_completed_by_date(date: str, id: int, actual_distance: int, actual_start: str, data_points: dict):
    """Mark the session as completed and optionally update the actual start time in time_scheduled and actual distance.
    
    Args:
        date: The date in YYYY-MM-DD format
        id: id of the session
        actual_distance: Actual distance in kilometers
        actual_start: Actual start time in HH:MM format (e.g., "14:30")
        data_points: List of laps data points from the activity with structure:
            {
                "data_points": {
                    "laps": [
                    {
                        "lap_index": 1,
                        "distance_meters": 1000.0,
                        "pace_ms": 2.59,
                        "pace_min_km": "6:26/km",
                        "heartrate_bpm": 112.7,
                        "cadence": 160.4,
                        "elapsed_time": 440
                    },
                    // ... more laps
                    ]
                }
            }
        
    Returns:
        Dict with status and message
    """
    try:
        # Get the session for the specified date (only one session per day)
        results = chroma_service.collection.get(where={"date": date})
        if not results['ids']:
            return {
                "status": "error",
                "message": f"No session found for date: {date}"
            }
        
        # Get the single session (there's only one per day)
        session_id = results['ids'][0]
        current_metadata = results['metadatas'][0]
        
        # Mark session as completed
        current_metadata['session_completed'] = True

        # Link the session to the activity
        current_metadata['activity_id'] = id

        # Update the actual distance
        current_metadata['actual_distance'] = actual_distance

        current_metadata['data_points'] = json.dumps(data_points)
        
        # Update actual start time in time_scheduled if provided
        if actual_start and 'time_scheduled' in current_metadata:
            try:
                time_scheduled_data = json.loads(current_metadata['time_scheduled'])
                if isinstance(time_scheduled_data, list) and len(time_scheduled_data) > 0:
                    # Update the first time_scheduled item with actual_start
                    time_scheduled_data[0]['actual_start'] = actual_start
                    current_metadata['time_scheduled'] = json.dumps(time_scheduled_data)
            except (json.JSONDecodeError, KeyError, IndexError) as e:
                print(f"Warning: Could not update time_scheduled with actual_start: {e}")
        
        # Update the session
        chroma_service.collection.update(
            ids=[session_id],
            metadatas=[current_metadata]
        )
        
        print(f"Updated successfully session status for {date} and linking to activity {id}")
        return {
            "status": "success",
            "message": f"Successfully marked session as completed on {date}" + 
                      (f" with actual start time: {actual_start}" if actual_start else "")
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error marking session as completed: {str(e)}"
        }

def write_activity_data(activity_data: Dict[str, Any]):
    """Store activity data with combined laps and streams in ChromaDB.
    
    Args:
        activity_data: Dictionary containing activity data with structure:
            {
                "activity_id": int,
                "metadata": {
                    "type": str,
                    "name": str,
                    "actual_distance": str,
                    "duration": str,
                    "start_date": str,
                    "actual_start": str,
                    "pace": str,
                    "total_distance_meters": float,
                    "total_laps": int,
                    "total_stream_points": int,
                    "resolution": str,
                    "series_type": str,
                    "available_streams": list,
                    "has_laps": bool,
                    "has_streams": bool
                },
                "data_points": {
                    "laps": list,
                    "streams": list
                }
            }
        
    Returns:
        Dict with status and message
    """
    try:
        # Extract activity_id for unique identification
        activity_id = activity_data.get("activity_id")
        print(f"Writing activity data: {activity_id}")
        if not activity_id:
            return {
                "status": "error",
                "message": "activity_id is required",
                "activity_id": None
            }
        
        # Convert activity_id to string for ChromaDB
        activity_id_str = str(activity_id)
        
        # Prepare the document content (use activity name as document)
        metadata = activity_data.get("metadata", {})
        document_text = metadata.get("name", f"Activity {activity_id}")
        
        # Prepare metadata for ChromaDB - convert complex types to JSON strings
        # BUT exclude data_points from metadata to avoid duplication
        metadata_for_storage = {}
        for key, value in metadata.items():
            if key == "data_points":
                # Skip data_points - it will be stored separately
                continue
            elif isinstance(value, (list, dict)):
                # Convert lists and dicts to JSON strings for ChromaDB compatibility
                metadata_for_storage[key] = json.dumps(value)
            else:
                # Keep primitive types as-is
                metadata_for_storage[key] = value
        
        # Add data_points as a separate field (not in metadata)
        data_points = activity_data.get("data_points")
        if data_points:
            # Store the complete data_points structure with both laps and streams
            metadata_for_storage["data_points"] = json.dumps(data_points)
            
            # Also store individual counts for easy access
            if isinstance(data_points, dict):
                metadata_for_storage["laps_count"] = len(data_points.get("laps", []))
                metadata_for_storage["streams_count"] = len(data_points.get("streams", []))
        
        # Store in ChromaDB using the activity_id as the unique identifier
        # Store data_points separately from metadata to avoid duplication
        chroma_service.collection.add(
            documents=[document_text],
            metadatas=[metadata_for_storage],
            ids=[activity_id_str]
        )
        print(f"Successfully stored data for activity_id: {activity_id}")
        return {
            "status": "success",
            "message": f"Successfully stored activity data for activity_id: {activity_id}",
            "activity_id": activity_id
        }
            
    except Exception as e:
        print(f"Error storing activity data: {str(e)}")
        return {
            "status": "error",
            "message": f"Error storing activity data: {str(e)}",
            "activity_id": None
        }

def get_activity_by_id(activity_id: int):
    """
    Retrieves activity data by activity_id from the database.
    
    Args:
        activity_id: The Strava activity ID
        
    Returns:
        dict: The activity data or a message if none found.
    """
    try:
        print(f"Getting activity data by ID: {activity_id}")
        activity_id_str = str(activity_id)
        results = chroma_service.collection.get(ids=[activity_id_str])
        
        if not results['ids']:
            return {
                "status": "error",
                "message": f"No activity found with ID: {activity_id}",
                "activity_data": None
            }
        
        # Reconstruct the activity data structure
        document = results['documents'][0]
        metadata = results['metadatas'][0]
        
        # Parse JSON strings back to their original types
        parsed_metadata = {}
        data_points = {}
        
        for key, value in metadata.items():
            if key == "data_points" and value:
                # Parse data_points back to dict and store separately
                # DO NOT add to parsed_metadata to avoid duplication
                data_points = json.loads(value)
            elif isinstance(value, str) and (value.startswith('[') or value.startswith('{')):
                # Try to parse other JSON strings (lists and dicts)
                try:
                    parsed_metadata[key] = json.loads(value)
                except json.JSONDecodeError:
                    # If it's not valid JSON, keep as string
                    parsed_metadata[key] = value
            else:
                # Keep primitive types as-is
                parsed_metadata[key] = value
        
        # No need to remove data_points from metadata since we never added it
        # The data_points is already handled separately above
        
        activity_data = {
            "activity_id": activity_id,
            "metadata": parsed_metadata,  # metadata without data_points
            "data_points": data_points    # data_points as separate field
        }
        
        return {
            "status": "success",
            "message": f"Found activity data for ID: {activity_id}",
            "activity_data": activity_data
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error retrieving activity data: {str(e)}",
            "activity_data": None
        }

def get_weekly_sessions(start_date: str) -> Dict:
    """Get sessions for a week starting from the given date (Monday).
        
    Args:
        start_date: Start date in YYYY-MM-DD format (should be a Monday)
            
    Returns:
        Dict containing:
            - status: "success" or "error"
            - data: List of daily sessions for the week
            - summary: Weekly summary statistics
            - message: Description of the result
    """
    try:
        from datetime import datetime, timedelta
            
        # Validate start_date format
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except ValueError:
            return {
                "status": "error",
                "data": None,
                "summary": None,
                "message": "Invalid date format. Use YYYY-MM-DD"
            }
            
        days_since_monday = start_dt.weekday()
        # Calculate the Monday of the current week
        monday_dt = start_dt - timedelta(days=days_since_monday)
        # Calculate the Sunday of the current week (6 days after Monday)
        sunday_dt = monday_dt + timedelta(days=6)
        # Format the datetime objects back into 'YYYY-MM-%d' strings
        start_date_of_week = monday_dt.strftime("%Y-%m-%d")
        end_date_of_week = sunday_dt.strftime("%Y-%m-%d")   
        # Get all sessions for the week by querying each day individually
        daily_sessions = {}
      
        for i in range(7):
            current_date = (monday_dt + timedelta(days=i)).strftime("%Y-%m-%d")               
            # Get sessions for this specific date
            results = chroma_service.collection.get(
                    where={"date": current_date}
            )           
            # Check if we have any results for this date
            if (results and 'ids' in results and results['ids'] and 
                len(results['ids']) > 0):
                    
                # Deserialize JSON strings in metadata
                if 'metadatas' in results and results['metadatas'] and len(results['metadatas']) > 0:
                    for j, metadata in enumerate(results['metadatas']):
                        results['metadatas'][j] = chroma_service._deserialize_metadata(metadata)                  
                # Process the results for this date
                for j in range(len(results['ids'])):
                    session_date = results['metadatas'][j].get('date', '')
                    daily_sessions[session_date] = {
                        'id': results['ids'][j],
                        'session': results['documents'][j],
                        'metadata': results['metadatas'][j]
                    }
            
        # Create a complete week structure (Monday to Sunday)
        week_data = []
        total_distance_planned = 0
        total_distance_completed = 0
        total_sessions = 0
        completed_sessions = 0
            
        for i in range(7):
            current_date = (monday_dt + timedelta(days=i)).strftime("%Y-%m-%d")
            day_name = (monday_dt + timedelta(days=i)).strftime("%A")
                
            if current_date in daily_sessions:
                session_data = daily_sessions[current_date]
                metadata = session_data['metadata']               
                # Extract session information
                session_type = metadata.get('type', 'No Session')
                actual_distance = metadata.get('actual_distance', 0)
                planned_distance = metadata.get('distance', 0)
                session_completed = metadata.get('session_completed', False)          
                # Update totals
                if session_type != 'Rest Day' and planned_distance > 0:
                    total_sessions += 1
                    total_distance_planned += planned_distance
                    total_distance_completed += actual_distance            
                if session_completed:
                    completed_sessions += 1     
                week_data.append({
                    'date': current_date,
                    'day_name': day_name,
                    'session_type': session_type,
                    'planned_distance': planned_distance,
                    'actual_distance': actual_distance,
                    'session_completed': session_completed,
                    'has_activity': session_type != 'Rest Day' and actual_distance > 0,
                    'is_today': current_date == datetime.now().strftime("%Y-%m-%d")
                })
            else:
                # No session data for this day
                week_data.append({
                    'date': current_date,
                    'day_name': day_name,
                    'session_type': 'No Session',
                    'planned_distance': 0,
                    'actual_distance': 0,
                    'session_completed': False,
                    'has_activity': False,
                    'is_today': current_date == datetime.now().strftime("%Y-%m-%d")
                })  
        # Create weekly summary
        summary = {
            'total_distance_planned': total_distance_planned,
            'total_distance_completed': total_distance_completed,
            'total_sessions': total_sessions,
            'completed_sessions': completed_sessions,
            'completion_rate': (completed_sessions / total_sessions * 100) if total_sessions > 0 else 0,
            'week_start': start_date_of_week,
            'week_end': end_date_of_week
        }
            
        return {
            "status": "success",
            "data": week_data,
            "summary": summary,
            "message": f"Weekly data retrieved for {start_date_of_week} to {end_date_of_week}"
        }
            
    except Exception as e:
        print(f"Error in get_weekly_sessions: {str(e)}")
        return {
            "status": "error",
            "data": None,
            "summary": None,
            "message": f"Error retrieving weekly sessions: {str(e)}"
        }

def update_session_with_analysis(date: str, coach_feedback: str):
    """Update session data with coach feedback.
    
    Args:
        date: The date in YYYY-MM-DD format
        coach_feedback: String containing the analysis and recommendations
        
    Returns:
        Dict with status and message
    """
    try:
        # Get the session for the specified date
        print(f"[chromaDB_tools] Updating session with coach feedback for {date}")
        results = chroma_service.collection.get(where={"date": date})        
        if not results['ids']:
            return {
                "status": "error",
                "message": f"No session found for date: {date}"
            }
        
        # Get the single session (there's only one per day)
        session_id = results['ids'][0]
        current_metadata = results['metadatas'][0]
        
        # Add coach feedback
        current_metadata['coach_feedback'] = coach_feedback
        
        # Update the session
        chroma_service.collection.update(
            ids=[session_id],
            metadatas=[current_metadata]
        )
        
        print(f"Successfully updated session with coach feedback for {date}")
        return {
            "status": "success",
            "message": f"Successfully updated session with coach feedback for {date}",
            "feedback_length": len(coach_feedback)
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error updating session analysis: {str(e)}"
        }