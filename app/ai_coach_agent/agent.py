from google.adk.agents import Agent
from dotenv import load_dotenv

from .sub_agents.planner_agent.agent import planner_agent
from .sub_agents.scheduler_agent.agent import scheduler_agent
from .sub_agents.strava_agent.agent import strava_agent

load_dotenv()

root_agent = Agent(
    name="ai_coach_agent",
    model="gemini-2.0-flash-exp",
    description=(
        "Agent that parses marathon training plan, and adjusts if a sessions is missed."
    ),
    instruction=(
        "You are an AI coach assistant root agent. Supported by your sub_agents, you can understand the training plan, provide today's session, "
        "adjust if a session is missed, provide calendar activities, and list activities from Strava, "
        
        "## sub_agents\n"
        "planner_agent: parses training plan and retrieves today's session\n"
        "scheduler_agent: retrieves list of events in the user's calendar\n"
        "strava_agent: list activities from Strava\n\n"
    ),
    sub_agents=[
        planner_agent,
        scheduler_agent,
        strava_agent
    ],
)