import sys
from pathlib import Path

app_dir = str(Path(__file__).parent.parent.parent.parent)
sys.path.append(app_dir)

from tools.strava_tools3 import list_activities
from google.adk.agents import Agent

strava_agent = Agent(
    name="strava_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent that list activities from Strava"
    ),
    instruction=(
        "You are a strava agent, a helpful assistant that can perform various tasks "
        "helping with Strava operations.\n\n"
        "## Strava operations\n"
        "You can perform activities operations directly using these tools:\n"
        "- `strava_tools3`: Show today's activities from your Strava account\n\n"
        "Today's date is 09-jun-2025."
    ),
    tools=[list_activities],
)