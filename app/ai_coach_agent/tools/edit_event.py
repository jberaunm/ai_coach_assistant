"""
Edit event tool for Google Calendar integration.
"""

from .calendar_utils import get_calendar_service, parse_datetime


def edit_event(
    event_id: str,
    date: str,
    start_time: str,
    end_time: str,
    title: str,
) -> dict:
    """
    Edit an existing event in Google Calendar - change title and/or reschedule.

    Args:
        event_id (str): The ID of the event to edit
        date (str): The date of the event in YYYY-MM-DD format
        start_time (str): Start time in HH:MM format (24-hour)
        end_time (str): End time in HH:MM format (24-hour)

    Returns:
        dict: Information about the edited event or error details
    """
    try:
        # Get calendar service
        print(f"[CalendarAPI_tool_edit_event]: event_id: {event_id}, date: {date}, start_time: {start_time}, end_time: {end_time}, title: {title}")
        service = get_calendar_service()
        if not service:
            return {
                "status": "error",
                "message": "Failed to authenticate with Google Calendar. Please check credentials.",
            }

        # Always use primary calendar
        calendar_id = "primary"

        # Combine date and times
        start_datetime = f"{date} {start_time}"
        end_datetime = f"{date} {end_time}"

        # Parse times
        start_dt = parse_datetime(start_datetime)
        end_dt = parse_datetime(end_datetime)

        if not start_dt or not end_dt:
            return {
                "status": "error",
                "message": "Invalid date/time format. Please use YYYY-MM-DD for date and HH:MM for time.",
            }

        # Dynamically determine timezone
        timezone_id = "America/New_York"  # Default to Eastern Time

        try:
            # Try to get the timezone from the calendar settings
            settings = service.settings().list().execute()
            for setting in settings.get("items", []):
                if setting.get("id") == "timezone":
                    timezone_id = setting.get("value")
                    break
        except Exception:
            # If we can't get it from settings, we'll use the default
            pass

        # Create event body without type annotations
        event_body = {}

        # Add title
        event_body["summary"] = title

        # Add start and end times with the dynamically determined timezone
        event_body["start"] = {
            "dateTime": start_dt.isoformat(),
            "timeZone": timezone_id,
        }
        event_body["end"] = {"dateTime": end_dt.isoformat(), "timeZone": timezone_id}
        event_body["id"] = event_id

        

        # Update the event
        updated_event = (
            service.events()
            .update(calendarId=calendar_id, eventId=event_id,body=event_body)
            .execute()
        )

        return {
            "status": "success",
            "message": "Event updated successfully",
        }

    except Exception as e:
        return {"status": "error", "message": f"Error updating event: {str(e)}"}