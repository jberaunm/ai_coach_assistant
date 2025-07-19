import asyncio
import base64
import json
import os
import warnings
import logging
from pathlib import Path
from typing import AsyncIterable, Dict, Set
from datetime import datetime

from dotenv import load_dotenv
from fastapi import FastAPI, Query, WebSocket, UploadFile, File, HTTPException
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from google.adk.agents import LiveRequestQueue
from google.adk.agents.run_config import RunConfig
from google.adk.events.event import Event
from google.adk.runners import Runner
from google.adk.sessions.in_memory_session_service import InMemorySessionService
from google.genai import types
from ai_coach_agent.agent import root_agent
from db.chroma_service import chroma_service

from fastapi.middleware.cors import CORSMiddleware

#
# WebSocket Log Forwarding
#

# Store active WebSocket connections for log forwarding
websocket_connections: Dict[str, WebSocket] = {}

# Module-level variable to store the current WebSocket for log forwarding
_current_websocket: WebSocket = None

class PrintInterceptor:
    """Intercepts print statements and forwards them to WebSocket clients"""
    
    def __init__(self):
        self.original_print = print
        self.interesting_patterns = [
            '[FRONTEND TO AGENT]',
            '[FileReader_tool]',
            '[CalendarAPI_tool_create_event]',
            '[CalendarAPI_tool_list_events]',
            '[WeatherAPI_tool]',
            '[StravaAPI_tool]',
            '[PLANNER_AGENT]',
            '[SCHEDULER_AGENT]',
            '[STRAVA_AGENT]'
        ]
    
    def __call__(self, *args, **kwargs):
        # Call the original print function
        self.original_print(*args, **kwargs)
        
        # Check if any of the printed content contains interesting patterns
        message = ' '.join(str(arg) for arg in args)
        
        if any(pattern in message for pattern in self.interesting_patterns):
            # Send to frontend if WebSocket is available
            global _current_websocket
            if _current_websocket:
                try:
                    log_message = {
                        "log_message": message,
                        "timestamp": datetime.now().timestamp()
                    }
                    asyncio.create_task(_current_websocket.send_text(json.dumps(log_message)))
                except Exception as e:
                    print(f"Error sending log to frontend: {e}")

def set_current_websocket(websocket: WebSocket):
    """Set the current WebSocket for log forwarding"""
    global _current_websocket
    _current_websocket = websocket

def clear_current_websocket():
    """Clear the current WebSocket for log forwarding"""
    global _current_websocket
    _current_websocket = None

# Replace the global print function
print_interceptor = PrintInterceptor()
import builtins
builtins.print = print_interceptor

async def send_log_to_frontend(websocket: WebSocket, log_message: str):
    """Send a log message to the frontend for visualization"""
    try:
        message = {
            "log_message": log_message,
            "timestamp": datetime.now().timestamp()
        }
        await websocket.send_text(json.dumps(message))
    except Exception as e:
        print(f"Error sending log message to frontend: {e}")

#
# ADK Streaming
#

# Load Gemini API Key
load_dotenv()

APP_NAME = "ADK Streaming example"
session_service = InMemorySessionService()


async def start_agent_session(session_id, is_audio=False, websocket=None):
    """Starts an agent session"""

    # Create a Session
    session = await session_service.create_session(
        app_name=APP_NAME,
        user_id=session_id,
        session_id=session_id,
    )

    # Create a Runner
    runner = Runner(
        app_name=APP_NAME,
        agent=root_agent,
        session_service=session_service,
    )

    # Set response modality
    modality = "AUDIO" if is_audio else "TEXT"

    # Create speech config with voice settings
    speech_config = types.SpeechConfig(
        voice_config=types.VoiceConfig(
            # Puck, Charon, Kore, Fenrir, Aoede, Leda, Orus, and Zephyr
            prebuilt_voice_config=types.PrebuiltVoiceConfig(voice_name="Puck")
        )
    )

    # Create run config with basic settings
    config = {"response_modalities": [modality], "speech_config": speech_config}

    # Add output_audio_transcription when audio is enabled to get both audio and text
    if is_audio:
        config["output_audio_transcription"] = {}

    run_config = RunConfig(**config)

    # Create a LiveRequestQueue for this session
    live_request_queue = LiveRequestQueue()

    try:
        # Start agent session - don't await since it returns an async generator
        live_events = runner.run_live(
            session=session,
            live_request_queue=live_request_queue,
            run_config=run_config,
        )
        return live_events, live_request_queue
    except Exception as e:
        print(f"Error starting agent session: {e}")
        raise


async def agent_to_client_messaging(
    websocket: WebSocket, live_events: AsyncIterable[Event | None]
):
    """Agent to client communication"""
    try:
        async for event in live_events:
            if event is None:
                continue

            # If the turn complete or interrupted, send it
            if event.turn_complete or event.interrupted:
                message = {
                    "turn_complete": event.turn_complete,
                    "interrupted": event.interrupted,
                }
                await websocket.send_text(json.dumps(message))
                #print(f"[AGENT TO CLIENT]: {message}")
                continue

            # Read the Content and its first Part
            part = event.content and event.content.parts and event.content.parts[0]
            if not part:
                continue

            # Make sure we have a valid Part
            if not isinstance(part, types.Part):
                continue

            # Only send text if it's a partial response (streaming)
            # Skip the final complete message to avoid duplication
            if part.text and event.partial:
                message = {
                    "mime_type": "text/plain",
                    "data": part.text,
                    "role": "model",
                }
                await websocket.send_text(json.dumps(message))
                #print(f"[AGENT TO CLIENT]: text/plain: {part.text}")

            # If it's audio, send Base64 encoded audio data
            is_audio = (
                part.inline_data
                and part.inline_data.mime_type
                and part.inline_data.mime_type.startswith("audio/pcm")
            )
            if is_audio:
                audio_data = part.inline_data and part.inline_data.data
                if audio_data:
                    message = {
                        "mime_type": "audio/pcm",
                        "data": base64.b64encode(audio_data).decode("ascii"),
                        "role": "model",
                    }
                    await websocket.send_text(json.dumps(message))
                    #print(f"[AGENT TO CLIENT]: audio/pcm: {len(audio_data)} bytes.")
    except Exception as e:
        print(f"Error in agent_to_client_messaging: {e}")
        raise


async def client_to_agent_messaging(
    websocket: WebSocket, live_request_queue: LiveRequestQueue
):
    """Client to agent communication"""
    while True:
        # Decode JSON message
        message_json = await websocket.receive_text()
        message = json.loads(message_json)
        mime_type = message["mime_type"]
        data = message["data"]
        role = message.get("role", "user")  # Default to 'user' if role is not provided

        # Send the message to the agent
        if mime_type == "text/plain":
            # Send a text message
            content = types.Content(role=role, parts=[types.Part.from_text(text=data)])
            live_request_queue.send_content(content=content)
            print(f"[FRONTEND TO AGENT]: {data}")
        elif mime_type == "audio/pcm":
            # Send audio data
            decoded_data = base64.b64decode(data)

            # Send the audio data - note that ActivityStart/End and transcription
            # handling is done automatically by the ADK when input_audio_transcription
            # is enabled in the config
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
            print(f"[FRONTEND TO AGENT]: audio/pcm: {len(decoded_data)} bytes")

        else:
            raise ValueError(f"Mime type not supported: {mime_type}")


#
# FastAPI web app
#

app = FastAPI()

# Allow CORS for frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Get the absolute path to the app directory
APP_DIR = Path(__file__).parent
FRONT_END_DIR = Path(__file__).parent.parent / "frontend"
# STATIC_DIR = APP_DIR / "static"   # Removed
UPLOAD_DIR = APP_DIR / "uploads"
PUBLIC_DIR = FRONT_END_DIR / "public"

# websocket_connections is now defined globally for log forwarding

# app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")  # Removed

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# --- Removed old root and favicon routes ---
# @app.get("/", response_class=HTMLResponse)
# async def get():
#     """Serves the index.html"""
#     return FileResponse(STATIC_DIR / "index.html")

# @app.get("/favicon.ico")
# async def favicon():
#     return FileResponse(STATIC_DIR / "favicon.ico")

# --- Add a simple health check root route ---
@app.get("/")
async def root():
    return {"status": "ok"}

@app.post("/upload")
async def upload_file(file: UploadFile = File(...), session_id: str = Query(...)):
    try:
        print(f"Received file upload request for session {session_id}")
        print(f"Active WebSocket connections: {list(websocket_connections.keys())}")
        
        # Create a safe filename
        safe_filename = file.filename.replace(" ", "_").replace("\\", "_").replace("/", "_")
        file_path = UPLOAD_DIR / safe_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"File saved successfully at: {file_path}")
        print(f"File exists: {file_path.exists()}")
        print(f"File size: {file_path.stat().st_size} bytes")
        
        # Send a message through WebSocket
        if session_id in websocket_connections:
            print(f"Sending WebSocket message to session {session_id}")
            
            # Create a message to send to the agent with normalized file path
            normalized_path = str(file_path).replace('\\', '/')  # Normalize path separators
            message = {
                "mime_type": "text/plain",
                "data": f"can you parse my training plan? this is the file path: {normalized_path}",
                "role": "user"
            }
            
            # Get the live_request_queue for this session
            websocket = websocket_connections[session_id]
            if hasattr(websocket, 'live_request_queue'):
                # Send the message through the live_request_queue
                content = types.Content(role="user", parts=[types.Part.from_text(text=message["data"])])
                websocket.live_request_queue.send_content(content=content)
                print(f"Message sent to agent through live_request_queue: {message['data']}")
            else:
                print(f"No live_request_queue found for session {session_id}")
            
            print(f"WebSocket message sent successfully to session {session_id}")
        else:
            print(f"No WebSocket connection found for session {session_id}")
        
        return {
            "status": "success",
            "message": "File uploaded successfully",
            "filename": safe_filename
        }
    except Exception as e:
        print(f"Error in upload_file: {str(e)}")
        return {
            "status": "error",
            "message": str(e)
        }

@app.websocket("/ws/{session_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    session_id: str,
    is_audio: str = Query(...),
):
    """Client websocket endpoint"""
    print(f"New WebSocket connection request for session {session_id}")
    
    # Wait for client connection
    await websocket.accept()
    websocket_connections[session_id] = websocket
    
    # Set the current WebSocket for log forwarding
    set_current_websocket(websocket)
    
    print(f"Client #{session_id} connected, audio mode: {is_audio}")
    print(f"Active WebSocket connections: {list(websocket_connections.keys())}")

    try:
        # Start agent session
        live_events, live_request_queue = await start_agent_session(
            session_id, is_audio == "true", websocket
        )

        # Store live_request_queue with the WebSocket connection
        websocket.live_request_queue = live_request_queue

        # Start tasks
        agent_to_client_task = asyncio.create_task(
            agent_to_client_messaging(websocket, live_events)
        )
        client_to_agent_task = asyncio.create_task(
            client_to_agent_messaging(websocket, live_request_queue)
        )
        
        # Wait for both tasks to complete
        await asyncio.gather(agent_to_client_task, client_to_agent_task)
    except Exception as e:
        print(f"WebSocket error for session {session_id}: {e}")
        raise  # Re-raise the exception to ensure proper error handling
    finally:
        # Remove the connection when it's closed
        if session_id in websocket_connections:
            del websocket_connections[session_id]
            print(f"WebSocket connection removed for session {session_id}")
            print(f"Remaining WebSocket connections: {list(websocket_connections.keys())}")
        
        # Clear the current WebSocket if it's the same one
        clear_current_websocket()
            
        print(f"Client #{session_id} disconnected")

@app.get("/api/sessions")
async def list_sessions():
    """List all sessions stored in ChromaDB."""
    try:
        result = chroma_service.list_all_sessions()
        return result
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error listing sessions: {str(e)}"
        }

@app.get("/api/training-plan-exists")
async def training_plan_exists():
    """Check if any file exists in uploads."""
    exists = any(UPLOAD_DIR.iterdir())
    return {"exists": exists}

@app.get("/favicon.ico")
async def favicon():
    return FileResponse(PUBLIC_DIR / "favicon.ico")

@app.get("/api/todays-session")
async def get_todays_session():
    today = datetime.now().strftime("%Y-%m-%d")
    result = chroma_service.get_session_by_date(today)
    if not result or not result.get('documents') or not result['documents']:
        raise HTTPException(status_code=404, detail="No session found for today")
    return {
        "session": result['documents'][0],
        "metadata": result['metadatas'][0]
    }

@app.get("/api/session/{date}")
async def get_session_by_date(date: str):
    """Get session for a specific date in YYYY-MM-DD format."""
    try:
        result = chroma_service.get_session_by_date(date)
        if not result or not result.get('documents') or not result['documents']:
            raise HTTPException(status_code=404, detail=f"No session found for date: {date}")
        return {
            "session": result['documents'][0],
            "metadata": result['metadatas'][0]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving session: {str(e)}")

@app.get("/api/activity/{activity_id}")
async def get_activity_by_id_endpoint(activity_id: int):
    """Get activity data for a specific activity_id."""
    try:
        result = chroma_service.get_activity_by_id(activity_id)
        if result["status"] == "error":
            raise HTTPException(status_code=404, detail=result["message"])
        return result["activity_data"]
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving activity: {str(e)}")
