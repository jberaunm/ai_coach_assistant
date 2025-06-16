from db.chroma_service import chroma_service
from typing import Optional, List, Dict, Any
from pydantic import BaseModel

class Metadata(BaseModel):
    date: str                    # "2025-06-17"
    day: str                     # "Tuesday"
    type: str                    # "Easy Run"
    distance: Optional[str] = None
    notes: Optional[str] = None
    time: Optional[str] = None   # or datetime if you parse it
    weather: Optional[str] = None
    session_completed: bool

class SessionData(BaseModel):
    id: str
    document: str
    embedding: List[float]
    metadata: Metadata

def write_chromaDB(sessions: List[Dict[str, Any]]):
    """Store training plan sessions in ChromaDB.
    
    Args:
        sessions: List of session dictionaries. Each session should have:
            - date: str
            - day: str
            - type: str
            - distance: str
            - notes: Optional[str]
        
    Returns:
        Dict with status and message
    """
    try:
        # Use the store_training_plan method from ChromaService
        result = chroma_service.store_training_plan(
            sessions=sessions,
            metadata={"source": "training_plan_parser"}
        )
        
        if result == "success":
            return {
                "status": "success",
                "message": f"Successfully stored {len(sessions)} sessions",
                "plan_id": "plan_001"  # You might want to generate a unique ID
            }
        else:
            return {
                "status": "error",
                "message": f"Error storing sessions: {result}",
                "plan_id": None
            }
            
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error storing sessions: {str(e)}",
            "plan_id": None
        }
