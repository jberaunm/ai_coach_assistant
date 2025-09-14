from typing import List, Dict, Any
from pathlib import Path
import mimetypes
import base64

def file_reader(file_path: str) -> str:
    """
    Read the training plan file and return its content as text.
    The actual parsing will be done by the LLM.

    Args:
        file_path: Path to the uploaded file.

    Returns:
        The content of the file as text, or base64 encoded if binary.
    """
 
    print(f"[FileReader_tool]: {file_path}")
    # Normalize the file path to handle different separators
    normalized_path = str(file_path).replace('\\', '/').strip()

    try:
        mime_type, _ = mimetypes.guess_type(normalized_path)
        
        if mime_type and mime_type.startswith('text'):
            # Try to read as text
            with open(normalized_path, 'r', encoding='utf-8', errors='replace') as f:
                content = f.read()
            return content
        else:
            # Binary file: return base64 string
            with open(normalized_path, 'rb') as f:
                encoded = base64.b64encode(f.read()).decode('utf-8')
                content = f"[BINARY FILE - base64 encoded]\n{encoded}"
                print(f"[FileReader_tool] Binary file: {normalized_path}")
            return content
    except Exception as e:
        print(f"[FileReader_tool] Error reading file: {str(e)}")
        return f"Error reading file: {str(e)}"
