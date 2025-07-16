"""
Agent logging tool for tracking agent execution flow.
"""

from datetime import datetime
from typing import Literal, Optional

def agent_log(
    agent_name: str,
    event_type: Literal["start", "step", "finish", "error"],
    message: str,
    step_name: Optional[str] = None
) -> str:
    """
    Log agent execution events for frontend visualization.
    
    Args:
        agent_name: Name of the agent (e.g., "planner_agent", "scheduler_agent", "strava_agent")
        event_type: Type of event ("start", "step", "finish", "error")
        message: Description of what the agent is doing
        step_name: Optional name of the current step (for "step" events)
    
    Returns:
        str: Confirmation message
    """
    timestamp = datetime.now().strftime("%H:%M:%S")
    
    if event_type == "start":
        log_message = f"[{agent_name.upper()}] START: {message}"
    elif event_type == "finish":
        log_message = f"[{agent_name.upper()}] FINISH: {message}"
    elif event_type == "error":
        log_message = f"[{agent_name.upper()}] ERROR: {message}"
    else:
        log_message = f"[{agent_name.upper()}] {message}"
    
    # This will be captured by the PrintInterceptor and sent to frontend
    print(log_message)
    
    return f"Logged {event_type} event for {agent_name}" 