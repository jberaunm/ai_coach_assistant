from stravalib import Client, unit_helper
import os
from datetime import datetime

def list_activities() -> dict:
    """
    List Strava activities of today

    Returns:
        dict: Information about Strava activities or error details
    """
    try:
        # Get access token from environment variable
        access_token = os.getenv('STRAVA_ACCESS_TOKEN')
        if not access_token:
            return {
                "status": "error",
                "message": "Strava access token not configured",
                "events": [],
            }

        client = Client(access_token=access_token)
        
        # Get today's date
        #today = datetime.now().strftime("%Y-%m-%d")
        today = "2025-06-10"
        activities = client.get_activities(after=today, limit=10)

        if not activities:
            return {
                "status": "success",
                "message": "No activities found for today.",
                "events": [],
            }

        # Format activities for display
        formatted_activities = []
        for activity in activities:
            formatted_activity = {
                "id": activity.id,
                "type": activity.type,
                "name": activity.name,
                "distance": float(activity.distance),
            }
            formatted_activities.append(formatted_activity)

        return {
            "status": "success",
            "message": f"Found {len(formatted_activities)} activity(s) for today.",
            "events": formatted_activities,
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching activities: {str(e)}",
            "events": [],
        }