"""
List events tool for Google Calendar integration.
"""

import datetime

from .calendar_utils import format_event_time, get_calendar_service


def list_events(
    start_date: str,
    days: int,
) -> dict:
    """
    List upcoming calendar events within a specified date range.

    Args:
        start_date (str): Start date in YYYY-MM-DD format. If empty string, defaults to today.
        days (int): Number of days to look ahead. Use 1 for today only, 7 for a week, 30 for a month, etc.

    Returns:
        dict: Information about upcoming events in structured format:
        {
            "status": "success",
            "message": "Found X event(s).",
            "calendar": {
                "events": [
                    {"title": "Event Title", "start": "10:00", "end": "11:00"},
                    ...
                ]
            }
        }
    """
    try:
        print("Listing events")
        print("Start date: ", start_date)
        print("Days: ", days)
        # Get calendar service
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
                "events": [],
            }

        # Always use a large max_results value to return all events
        max_results = 100

        # Always use primary calendar
        calendar_id = "primary"

        # Set time range
        if not start_date or start_date.strip() == "":
            # If no start_date provided, use current time and look ahead by days
            start_time = datetime.datetime.utcnow()
            # If days is not provided or is invalid, default to 1 day
            if not days or days < 1:
                days = 1
            end_time = start_time + datetime.timedelta(days=days)
        else:
            try:
                # Parse the provided start_date
                requested_date = datetime.datetime.strptime(start_date, "%Y-%m-%d").date()
                current_date = datetime.datetime.utcnow().date()
                
                if requested_date == current_date:
                    # If the requested date is today, use current time as start_time
                    start_time = datetime.datetime.utcnow()
                    # Set end_time to the end of today (23:59:59)
                    end_time = start_time.replace(hour=23, minute=59, second=59, microsecond=999999)
                else:
                    # If the requested date is not today, use 00:00:00 of that specific date
                    start_time = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                    # Set end_time to the end of that specific day (23:59:59)
                    end_time = start_time.replace(hour=23, minute=59, second=59, microsecond=999999)
            except ValueError:
                return {
                    "status": "error",
                    "message": f"Invalid date format: {start_date}. Use YYYY-MM-DD format.",
                    "events": [],
                }

        # Format times for API call
        time_min = start_time.isoformat() + "Z"
        time_max = end_time.isoformat() + "Z"

        # Call the Calendar API
        events_result = (
            service.events()
            .list(
                calendarId=calendar_id,
                eventTypes="default",
                timeMin=time_min,
                timeMax=time_max,
                maxResults=max_results,
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        events = events_result.get("items", [])

        if not events:
            return {
                "status": "success",
                "message": "No upcoming events found.",
                "events": [],
            }

        # Format events for display
        formatted_events = []
        for event in events:
            # Get raw start and end times from the event
            start_raw = event.get("start", {})
            end_raw = event.get("end", {})
            
            # Extract time in HH:MM format
            start_time = "00:00"
            end_time = "00:00"
            
            if "dateTime" in start_raw:
                # This is a datetime event
                dt = datetime.datetime.fromisoformat(start_raw["dateTime"].replace("Z", "+00:00"))
                start_time = dt.strftime("%H:%M")
            elif "date" in start_raw:
                # This is an all-day event
                start_time = "00:00"
                
            if "dateTime" in end_raw:
                # This is a datetime event
                dt = datetime.datetime.fromisoformat(end_raw["dateTime"].replace("Z", "+00:00"))
                end_time = dt.strftime("%H:%M")
            elif "date" in end_raw:
                # This is an all-day event
                end_time = "23:59"
            
            formatted_event = {
                "title": event.get("summary", "Untitled Event"),
                "start": start_time,
                "end": end_time,
            }
            formatted_events.append(formatted_event)

        return {
            "status": "success",
            "message": f"Found {len(formatted_events)} event(s).",
            "calendar": {
                "events": formatted_events
            }
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching events: {str(e)}",
            "events": [],
        }
