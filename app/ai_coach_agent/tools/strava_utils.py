"""
Utility functions for Strava API integration.
"""

import json
import os
from pathlib import Path
import datetime
from dotenv import load_dotenv
from stravalib import Client
from stravalib.exc import AccessUnauthorized

# Load environment variables
load_dotenv()

# Path for token storage
TOKEN_PATH = Path(os.path.expanduser("~/.credentials/strava_tokens.json"))


def get_strava_client():
    """
    Authenticate and create a Strava client object.

    Returns:
        A Strava client object or None if authentication fails
    """
    # Check if tokens exist and are valid
    if not TOKEN_PATH.exists():
        print(f"Error: {TOKEN_PATH} not found.")
        print("Please run setup_strava_auth.py to set up OAuth authentication.")
        return None

    try:
        with open(TOKEN_PATH, "r") as f:
            token_data = json.load(f)
        
        # Basic check for required keys
        if not all(key in token_data for key in ["access_token", "refresh_token", "expires_at"]):
            print("Error: Token file is incomplete.")
            print("Please run setup_strava_auth.py to re-authenticate.")
            return None

    except (json.JSONDecodeError, FileNotFoundError):
        print("Error: Token file is corrupted or not found.")
        print("Please run setup_strava_auth.py to re-authenticate.")
        return None

    # Initialize client with tokens
    try:
        client = Client(
            access_token=token_data["access_token"],
            refresh_token=token_data["refresh_token"],
            token_expires=token_data["expires_at"]
        )

        # Test the connection and trigger refresh if needed
        #athlete = client.get_athlete()
        #print(f"Connected to Strava as {athlete.firstname} {athlete.lastname}")

        # Save refreshed tokens if they were updated
        current_expires_timestamp = client.token_expires

        if (client.access_token != token_data["access_token"] or
            client.refresh_token != token_data["refresh_token"] or
            current_expires_timestamp != token_data["expires_at"]):
            print("Token refreshed! Saving new tokens...")
            updated_token_data = {
                "access_token": client.access_token,
                "refresh_token": client.refresh_token,
                "expires_at": current_expires_timestamp,
                **{k: v for k, v in token_data.items() if k not in ["access_token", "refresh_token", "expires_at"]}
            }
            try:
                with open(TOKEN_PATH, "w") as f:
                    json.dump(updated_token_data, f, indent=4)
                print("New tokens saved successfully.")
            except Exception as e:
                print(f"Error saving refreshed tokens: {e}")

        return client

    except AccessUnauthorized as e:
        print(f"Authentication Error with Strava API: {e}")
        print("Your tokens might be invalid or expired.")
        print("Please run setup_strava_auth.py to re-authenticate.")
        return None
    except Exception as e:
        print(f"An unexpected error occurred during Strava API interaction: {e}")
        return None


def format_activity_distance(distance_meters):
    """
    Format activity distance from meters to a human-readable string.

    Args:
        distance_meters (float): Distance in meters

    Returns:
        str: A human-readable distance string
    """
    if distance_meters < 1000:
        return f"{distance_meters:.0f}m"
    else:
        return f"{distance_meters / 1000:.2f}km"


def format_activity_duration(duration_seconds):
    """
    Format activity duration from seconds to a human-readable string.

    Args:
        duration_seconds (int): Duration in seconds

    Returns:
        str: A human-readable duration string
    """
    hours = duration_seconds // 3600
    minutes = (duration_seconds % 3600) // 60
    seconds = duration_seconds % 60

    if hours > 0:
        return f"{hours}h {minutes}m {seconds}s"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"


def format_activity_pace(average_speed_mps):
    """
    Format activity pace from meters per second to minutes per kilometer.

    Args:
        average_speed_mps (float): Average speed in meters per second

    Returns:
        str: A human-readable pace string in minutes per kilometer
    """
    if not average_speed_mps or average_speed_mps <= 0:
        return "N/A"
    
    # Convert m/s to min/km
    # 1 km = 1000 meters
    # Time = Distance / Speed
    # Time in seconds = 1000 / average_speed_mps
    # Time in minutes = (1000 / average_speed_mps) / 60
    
    seconds_per_km = 1000 / average_speed_mps
    minutes_per_km = seconds_per_km / 60
    
    # Extract minutes and seconds
    whole_minutes = int(minutes_per_km)
    remaining_seconds = int((minutes_per_km - whole_minutes) * 60)
    
    return f"{whole_minutes}:{remaining_seconds:02d}/km"


def get_current_time() -> dict:
    """
    Get the current time and date
    """
    now = datetime.datetime.now()

    # Format date as YYYY-MM-DD
    formatted_date = now.strftime("%Y-%m-%d")

    return {
        "current_time": now.strftime("%Y-%m-%d %H:%M:%S"),
        "formatted_date": formatted_date,
    }