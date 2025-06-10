import pandas as pd
from datetime import datetime
from typing import List, Dict, Any


def parse_training_plan(file_path: str) -> List[Dict[str, Any]]:
    """
    Parse the training plan Excel file into a list of structured sessions.

    Returns a list of sessions with fields: date, day, type, distance, notes
    """
    #file_path = "C:/Users/jeison.beraun_unique/Documents/Cursor/cs5500/adk/ai_coach/data/training_plan.xlsx"
    
    df = pd.read_excel(file_path)
    df.columns = [col.strip().lower().replace(" ", "_") for col in df.columns]

    sessions = []
    for _, row in df.iterrows():
        session = {
            "date": str(row.get("date", ""))[:10],
            "day": row.get("day", ""),
            "type": row.get("type", ""),
            "distance": row.get("distance", 0),
            "notes": row.get("notes", "")
        }
        sessions.append(session)

    return sessions


def get_today_session(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Retrieve today's session from the parsed training plan.

    Args:
        sessions: List of session dictionaries (from parse_training_plan)

    Returns:
        A dictionary with the session for today or a not-found message.
    """
    today_str = datetime.today().strftime("%Y-%m-%d")

    for session in sessions:
        if session["date"] == today_str:
            return {
                "status": "success",
                "session": session
            }

    return {
        "status": "not_found",
        "message": f"No session scheduled for today ({today_str})."
    }
