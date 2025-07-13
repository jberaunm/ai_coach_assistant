from typing import List, Dict, Any
from pathlib import Path
import mimetypes
import base64

def read_training_plan(file_path: str) -> str:
    """
    Read the training plan file and return its content as text.
    The actual parsing will be done by the LLM.

    Args:
        file_path: Path to the uploaded file.

    Returns:
        The content of the file as text, or base64 encoded if binary.
    """
    print(f"[PLANNER] Reading file: {file_path}")
    
    # Normalize the file path to handle different separators
    normalized_path = str(file_path).replace('\\', '/').strip()
    print(f"[PLANNER] Normalized path: {normalized_path}")
    
    try:
        mime_type, _ = mimetypes.guess_type(normalized_path)
        
        if mime_type and mime_type.startswith('text'):
            # Try to read as text
            print(f"[PLANNER] Reading as text file (mime type: {mime_type})")
            with open(normalized_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            print(f"[PLANNER] Successfully read text file, content length: {len(content)} characters")
            return content
        else:
            # Binary file: return base64 string
            print(f"[PLANNER] Reading as binary file (mime type: {mime_type})")
            with open(normalized_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                content = f"[BINARY FILE - base64 encoded]\n{encoded}"
            print(f"[PLANNER] Successfully encoded binary file, content length: {len(content)} characters")
            return content
    except Exception as e:
        print(f"[PLANNER] Error reading file {normalized_path}: {str(e)}")
        return f"Error reading file: {str(e)}"


#def get_today_session(sessions: List[Dict[str, Any]]) -> Dict[str, Any]:
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
