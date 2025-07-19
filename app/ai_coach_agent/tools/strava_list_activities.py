from datetime import timedelta, datetime
from .strava_utils import get_strava_client, format_activity_distance, format_activity_duration, format_activity_pace

def list_strava_activities(start_date: str) -> dict:
    """
    List Strava activities for the specified date

    Args:
        start_date (str): Start date in YYYY-MM-DD format

    Returns:
        dict: Information about Strava activities or error details
    """
    try:
        print(f"[StravaAPI tool] START: list_activities()")
        
        # Calculate end_date as the next day after start_date
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = start_datetime + timedelta(days=1)
        end_date = end_datetime.strftime("%Y-%m-%d")
        
        # Get Strava client using the utility function
        client = get_strava_client()
        if not client:
            return {
                "status": "error",
                "message": "Failed to authenticate with Strava API",
                "events": [],
            }
        
        activities = client.get_activities(after=start_date, before=end_date, limit=5)

        if not activities:
            return {
                "status": "success",
                "message": f"No activities found for {start_date}.",
                "events": [],
            }

        # Format activities for display
        formatted_activities = []
        actual_start = None
        
        for activity in activities:
            # Check if the sport_type is 'Run'
            if activity.sport_type == "Run":
                # Extract the actual start time from the first run activity
                if actual_start is None and activity.start_date_local:
                    actual_start = activity.start_date_local.strftime("%H:%M")
                
                formatted_activity = {
                    "id": activity.id,
                    "type": activity.sport_type.root,
                    "name": activity.name,
                    "distance": format_activity_distance(float(activity.distance)),
                    "duration": format_activity_duration(activity.moving_time) if activity.moving_time else "N/A",
                    "start_date": activity.start_date_local.strftime("%Y-%m-%d %H:%M") if activity.start_date else "N/A",
                    "pace": format_activity_pace(activity.average_speed) if activity.average_speed else "N/A",
                }
                formatted_activities.append(formatted_activity)

        print(f"{formatted_activities}")
        return {
            "status": "success",
            "message": f"Found {len(formatted_activities)} activity(s).",
            "events": formatted_activities,
            "actual_start": actual_start  # Include the actual start time in the response
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching activities: {str(e)}",
            "events": [],
        }


