from datetime import timedelta, datetime
from .strava_utils import get_strava_client, format_activity_distance, format_activity_duration, format_activity_pace

def get_activity_with_streams(start_date: str) -> dict:
    """
    Get complete activity data including details and stream data for the first activity on a given date

    Args:
        start_date (str): Start date in YYYY-MM-DD format

    Returns:
        dict: Complete activity data with metadata and stream data points
    """
    try:
        print(f"[StravaAPI tool] START: get_activity_with_streams() for date {start_date}")
                
        # Get Strava client using the utility function
        client = get_strava_client()
        if not client:
            return {
                "status": "error",
                "message": "Failed to authenticate with Strava API",
                "activity_data": None,
            }
        
        # Calculate end_date as the next day after start_date
        start_datetime = datetime.strptime(start_date, "%Y-%m-%d")
        end_datetime = start_datetime + timedelta(days=1)
        end_date = end_datetime.strftime("%Y-%m-%d")
        
        # Get activities for the specified date
        activities = client.get_activities(after=start_date, before=end_date, limit=5)
        
        if not activities:
            return {
                "status": "error",
                "message": f"No activities found for {start_date}",
                "activity_data": None,
            }

        # Find the first run activity
        target_activity = None
        for activity in activities:
            if activity.sport_type == "Run":
                target_activity = activity
                break
        
        if not target_activity:
            return {
                "status": "error",
                "message": f"No running activities found for {start_date}",
                "activity_data": None,
            }

        activity_id = target_activity.id
        print(f"Found activity ID: {activity_id}")

        # Get activity streams
        types = ["distance", "velocity_smooth", "heartrate", "altitude", "cadence"]
        streams = client.get_activity_streams(
            activity_id=activity_id,
            types=types,
            resolution="low",
            series_type="distance",
        )

        if not streams:
            return {
                "status": "error",
                "message": f"No stream data available for activity {activity_id}",
                "activity_data": None,
            }

        # Structure the complete data in the format expected by write_activity_data
        activity_data = {
            "activity_id": activity_id,
            "metadata": {
                "type": target_activity.sport_type.root if target_activity.sport_type else "Unknown",
                "name": target_activity.name if target_activity.name else "Untitled Activity",
                "distance": format_activity_distance(float(target_activity.distance)) if target_activity.distance else "N/A",
                "duration": format_activity_duration(target_activity.moving_time) if target_activity.moving_time else "N/A",
                "start_date": target_activity.start_date_local.strftime("%Y-%m-%d %H:%M") if target_activity.start_date_local else "N/A",
                "actual_start": target_activity.start_date_local.strftime("%H:%M") if target_activity.start_date_local else "N/A",
                "pace": format_activity_pace(target_activity.average_speed) if target_activity.average_speed else "N/A",
                "total_distance_meters": float(target_activity.distance) if target_activity.distance else 0,
                "total_data_points": 0,
                "resolution": "low",
                "series_type": "distance"
            },
            "data_points": []
        }

        # Get the distance stream as our primary reference
        distance_stream = streams.get('distance')
        if not distance_stream or not distance_stream.data:
            return {
                "status": "error",
                "message": "No distance data available for this activity",
                "activity_data": None,
            }

        total_data_points = len(distance_stream.data)
        activity_data["metadata"]["total_data_points"] = total_data_points

        # Create synchronized data points
        for i in range(total_data_points):
            # Get velocity in m/s and convert to pace format
            velocity_ms = streams.get('velocity_smooth').data[i] if streams.get('velocity_smooth') and i < len(streams['velocity_smooth'].data) else None
            pace = format_activity_pace(velocity_ms) if velocity_ms and velocity_ms > 0 else None
            
            # Get cadence in rpm and convert to spm (1 rpm = 2 spm)
            cadence_rpm = streams.get('cadence').data[i] if streams.get('cadence') and i < len(streams['cadence'].data) else None
            cadence_spm = cadence_rpm * 2 if cadence_rpm and cadence_rpm > 0 else None
            
            data_point = {
                "index": i,
                "distance_meters": distance_stream.data[i] if i < len(distance_stream.data) else None,
                "velocity_ms": velocity_ms,
                "heartrate_bpm": streams.get('heartrate').data[i] if streams.get('heartrate') and i < len(streams['heartrate'].data) else None,
                "altitude_meters": streams.get('altitude').data[i] if streams.get('altitude') and i < len(streams['altitude'].data) else None,
                "cadence": cadence_spm,
            }
            activity_data["data_points"].append(data_point)

        print(f"Successfully processed {total_data_points} data points for activity {activity_id}")
        return {
            "status": "success",
            "message": f"Retrieved complete data for activity {activity_id} on {start_date}",
            "activity_data": activity_data
        }

    except Exception as e:
        return {
            "status": "error",
            "message": f"Error fetching activity data: {str(e)}",
            "activity_data": None,
        }