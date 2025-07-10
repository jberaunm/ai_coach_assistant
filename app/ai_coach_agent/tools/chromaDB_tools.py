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

def write_chromaDB(sessions: List[Dict[str, Any]]):
    """Store training plan sessions in ChromaDB.
    
    Args:
        sessions: List of session dictionaries. Each session should have:
            - date: str
            - day: str
            - type: str
            - distance: str or float
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
        
        # Create the expected weather structure
        weather_structure = {
            "hours": hours_data
        }
        
        # Update each session's weather metadata
        for i, session_id in enumerate(results['ids']):
            current_metadata = results['metadatas'][i]
            
            # Update weather data with the simplified structure
            current_metadata['weather'] = json.dumps(weather_structure)
            
            # Update the session
            chroma_service.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
        
        return {
            "status": "success",
            "message": f"Successfully updated weather for {len(results['ids'])} sessions on {date}"
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