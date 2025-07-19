#!/usr/bin/env python3
"""
Strava API Authentication Setup Script

This script helps you set up OAuth 2.0 credentials for Strava API integration.
Follow the instructions in the console.
"""

import json
import os
from pathlib import Path
from dotenv import load_dotenv
from stravalib import Client
from stravalib.exc import AccessUnauthorized

# Load environment variables
load_dotenv()

# Define scopes needed for Strava API
SCOPES = ['read_all', 'activity:read_all', 'profile:read_all']

# Path for token storage
TOKEN_PATH = Path(os.path.expanduser("~/.credentials/strava_tokens.json"))

# Get client ID and secret from environment variables
STRAVA_CLIENT_ID = os.getenv("STRAVA_CLIENT_ID")
STRAVA_CLIENT_SECRET = os.getenv("STRAVA_CLIENT_SECRET")
STRAVA_REDIRECT_URI = "http://localhost"


def setup_oauth():
    """Set up OAuth 2.0 for Strava API"""
    print("\n=== Strava API OAuth Setup ===\n")

    if not STRAVA_CLIENT_ID or not STRAVA_CLIENT_SECRET:
        print("Error: STRAVA_CLIENT_ID or STRAVA_CLIENT_SECRET environment variables are not set!")
        print("\nTo set up Strava API integration:")
        print("1. Go to https://www.strava.com/settings/api")
        print("2. Create a new API application")
        print("3. Set the Authorization Callback Domain to 'localhost'")
        print("4. Copy the Client ID and Client Secret")
        print("5. Add them to your .env file:")
        print("   STRAVA_CLIENT_ID=your_client_id_here")
        print("   STRAVA_CLIENT_SECRET=your_client_secret_here")
        print("\nThen run this script again.")
        return False

    print(f"Found Strava API credentials. Setting up OAuth flow...")

    try:
        # Initialize client for OAuth
        client = Client()
        
        # Generate authorization URL
        auth_url = client.authorization_url(
            client_id=STRAVA_CLIENT_ID,
            redirect_uri=STRAVA_REDIRECT_URI,
            scope=SCOPES
        )
        
        print("\n1. Open this URL in your web browser to authorize your application:")
        print(auth_url)
        print("\n2. After authorizing, Strava will redirect you to a URL (e.g., http://localhost/?state=&code=YOUR_CODE_HERE&scope=...).")
        print("   Copy the 'code' value from that URL.")
        
        authorization_code = input("\n3. Paste the authorization code here and press Enter: ")

        # Exchange authorization code for tokens
        print("\nExchanging authorization code for tokens...")
        token_response = client.exchange_code_for_token(
            client_id=STRAVA_CLIENT_ID,
            client_secret=STRAVA_CLIENT_SECRET,
            code=authorization_code
        )

        # Extract and save all necessary token data
        access_token = token_response["access_token"]
        refresh_token = token_response["refresh_token"]
        expires_at = token_response["expires_at"]

        # Store athlete info that comes with the token response
        athlete_info = token_response.get("athlete", {})

        token_data = {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "expires_at": expires_at,
            "athlete_id": athlete_info.get("id"),
            "athlete_resource_state": athlete_info.get("resource_state")
        }

        # Save tokens
        TOKEN_PATH.parent.mkdir(parents=True, exist_ok=True)
        with open(TOKEN_PATH, "w") as f:
            json.dump(token_data, f, indent=4)

        print(f"\nSuccessfully saved tokens to {TOKEN_PATH}")

        # Test the API connection
        print("\nTesting connection to Strava API...")
        test_client = Client(
            access_token=access_token,
            refresh_token=refresh_token,
            token_expires=expires_at
        )
        
        athlete = test_client.get_athlete()
        print(f"\nSuccess! Connected to Strava API as {athlete.firstname} {athlete.lastname}")
        
        # Test getting activities
        activities = test_client.get_activities(limit=1)
        if activities:
            print(f"Found {len(list(activities))} recent activity(ies)")
        else:
            print("No recent activities found")

        print("\nOAuth setup complete! You can now use the Strava API integration.")
        return True

    except AccessUnauthorized as e:
        print(f"\nAuthentication Error during code exchange: {e}")
        print("Please ensure the authorization code is correct and has not been used before.")
        return False
    except Exception as e:
        print(f"\nError during setup: {str(e)}")
        return False


if __name__ == "__main__":
    setup_oauth() 