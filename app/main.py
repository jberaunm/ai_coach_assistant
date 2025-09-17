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
            '[PLANNER_AGENT]',
            '[SCHEDULER_AGENT]',
            '[STRAVA_AGENT]',
            '[ANALYSER_AGENT]',
            '[NUMERICAL_ANALYSER_AGENT]',
            '[VISUAL_ANALYSER_AGENT]',
            '[RAG_AGENT]',
            '[FileReader_tool]',
            '[CalendarAPI_tool_create_event]',
            '[CalendarAPI_tool_list_events]',
            '[WeatherAPI_tool]',
            '[StravaAPI_tool]',
            '[ChartCreator_tool]',
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
                text_content = part.text.strip()
                
                # Only skip obvious system warnings, not agent responses
                if text_content and len(text_content) > 3:
                    message = {
                        "mime_type": "text/plain",
                        "data": text_content,
                        "role": "model",
                    }
                    await websocket.send_text(json.dumps(message))
                    #print(f"[AGENT TO CLIENT]: text/plain: {text_content}")

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
        # Send error message to client instead of raising
        try:
            error_message = {
                "mime_type": "text/plain",
                "data": f"I apologize, but there was an error processing your request. Please try again.",
                "role": "model",
                "turn_complete": True,
                "error": True
            }
            await websocket.send_text(json.dumps(error_message))
        except Exception as send_error:
            print(f"Error sending error message to client: {send_error}")
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
        elif mime_type.startswith("image/"):
            # Send image data as binary
            decoded_data = base64.b64decode(data)
            
            # Send the image data as a blob
            live_request_queue.send_realtime(
                types.Blob(data=decoded_data, mime_type=mime_type)
            )
            print(f"[FRONTEND TO AGENT]: {mime_type}: {len(decoded_data)} bytes")
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

# Create uploads directory if it doesn't exist
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)


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
                "data": f"Uploaded Plan Processing: {normalized_path}",
                "role": "user"
            }
            
            # Get the live_request_queue for this session
            websocket = websocket_connections[session_id]
            if hasattr(websocket, 'live_request_queue'):
                # Send the message through the live_request_queue
                content = types.Content(role="user", parts=[types.Part.from_text(text=message["data"])])
                websocket.live_request_queue.send_content(content=content)
                print(f"[FRONTEND TO AGENT]: {message['data']}")
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

@app.post("/upload-research")
async def upload_research_file(file: UploadFile = File(...), session_id: str = Query(...)):
    try:        
        # Create a safe filename
        safe_filename = file.filename.replace(" ", "_").replace("\\", "_").replace("/", "_")
        file_path = UPLOAD_DIR / safe_filename
        
        # Save the file
        with open(file_path, "wb") as buffer:
            content = await file.read()
            buffer.write(content)
        
        print(f"Research file saved successfully at: {file_path}")
        
        # Send a message through WebSocket for RAG processing
        if session_id in websocket_connections:
            
            # Create a message to send to the agent for RAG processing
            normalized_path = str(file_path).replace('\\', '/')  # Normalize path separators
            message = {
                "mime_type": "text/plain",
                "data": f"RAG Document Processing: {normalized_path}",
                "role": "user"
            }
            
            # Get the live_request_queue for this session
            websocket = websocket_connections[session_id]
            if hasattr(websocket, 'live_request_queue'):
                # Send the message through the live_request_queue
                content = types.Content(role="user", parts=[types.Part.from_text(text=message["data"])])
                websocket.live_request_queue.send_content(content=content)
            else:
                print(f"No live_request_queue found for session {session_id}")
            print(f"[FRONTEND TO AGENT] RAG Document Processing: {normalized_path}")
        else:
            print(f"No WebSocket connection found for session {session_id}")
        
        return {
            "status": "success",
            "message": "Research file uploaded and processing started",
            "filename": safe_filename
        }
    except Exception as e:
        print(f"Error in upload_research_file: {str(e)}")
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
        # Send a user-friendly error message before closing the connection
        try:
            error_message = {
                "mime_type": "text/plain",
                "data": f"I apologize, but there was an unexpected error. Please try again.",
                "role": "model",
                "turn_complete": True,
                "error": True
            }
            await websocket.send_text(json.dumps(error_message))
        except Exception as send_error:
            print(f"Error sending error message to client: {send_error}")
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

@app.get("/api/weekly/{start_date}")
async def get_weekly_sessions(start_date: str):
    """Get weekly sessions starting from the given date (should be a Monday) in YYYY-MM-DD format."""
    try:
        result = chroma_service.get_weekly_sessions(start_date)
        if result["status"] == "error":
            # Only return 400 for invalid date format
            if "Invalid date format" in result["message"]:
                raise HTTPException(status_code=400, detail=result["message"])
            else:
                # For other errors, return 500
                raise HTTPException(status_code=500, detail=result["message"])
        return result
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving weekly sessions: {str(e)}")

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

@app.post("/api/analyze-chart")
async def analyze_chart_endpoint(image_path: str = Query(...), session_id: str = Query(...)):
    """Analyze a running chart image directly from the backend."""
    try:
        print(f"Received chart analysis request for session {session_id}, image: {image_path}")
        
        # Check if WebSocket connection exists for this session
        if session_id not in websocket_connections:
            raise HTTPException(status_code=404, detail="No active session found")
        
        websocket = websocket_connections[session_id]
        if not hasattr(websocket, 'live_request_queue'):
            raise HTTPException(status_code=404, detail="No active agent session found")
        
        # Send the analysis request to the agent
        analysis_request = f"Analyze this chart: {image_path}"
        content = types.Content(role="user", parts=[types.Part.from_text(text=analysis_request)])
        websocket.live_request_queue.send_content(content=content)
        
        print(f"Chart analysis request sent to agent: {analysis_request}")
        
        return {
            "status": "success",
            "message": "Chart analysis request sent to agent",
            "image_path": image_path
        }
        
    except HTTPException:
        raise
    except Exception as e:
        print(f"Error in analyze_chart_endpoint: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error analyzing chart: {str(e)}")

@app.get("/api/rag-knowledge")
async def get_rag_knowledge(query: str = Query("", description="Search query for RAG knowledge"), 
                           category: str = Query(None, description="Filter by category"), 
                           limit: int = Query(10, description="Number of results to return")):
    """Retrieve RAG knowledge chunks from the knowledge base."""
    try:
        from ai_coach_agent.tools.rag_knowledge import retrieve_rag_knowledge
        
        if not query:
            # If no query provided, get all chunks
            from ai_coach_agent.tools.rag_knowledge import get_all_rag_categories
            from db.chroma_service import chroma_service
            
            rag_collection = chroma_service.client.get_collection("rag_knowledge")
            results = rag_collection.get()
            
            chunks = []
            if results['ids']:
                for i in range(len(results['ids'])):
                    chunk = {
                        'id': results['ids'][i],
                        'content': results['documents'][i],
                        'metadata': results['metadatas'][i]
                    }
                    chunks.append(chunk)
            
            return {
                "status": "success",
                "chunks": chunks,
                "total_count": len(chunks),
                "message": f"Retrieved all {len(chunks)} knowledge chunks"
            }
        else:
            # Search with query
            result = retrieve_rag_knowledge(query, n_results=limit, category=category)
            return result
            
    except Exception as e:
        print(f"Error in get_rag_knowledge: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving RAG knowledge: {str(e)}")

@app.get("/api/rag-categories")
async def get_rag_categories():
    """Get all available categories in the RAG knowledge base."""
    try:
        from ai_coach_agent.tools.rag_knowledge import get_all_rag_categories
        result = get_all_rag_categories()
        return result
    except Exception as e:
        print(f"Error in get_rag_categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving RAG categories: {str(e)}")

@app.get("/api/rag-stats")
async def get_rag_stats():
    """Get statistics about the RAG knowledge base with detailed source information."""
    try:
        from db.chroma_service import chroma_service
        
        rag_collection = chroma_service.client.get_collection("rag_knowledge")
        results = rag_collection.get()
        
        # Count chunks by category
        category_counts = {}
        if results['metadatas']:
            for metadata in results['metadatas']:
                category = metadata.get('category', 'Unknown')
                category_counts[category] = category_counts.get(category, 0) + 1
        
        # Group chunks by source and extract detailed metadata
        sources_info = {}
        if results['metadatas']:
            for i, metadata in enumerate(results['metadatas']):
                source = metadata.get('source', 'Unknown')
                document_id = metadata.get('document_id', 'unknown')
                
                if source not in sources_info:
                    sources_info[source] = {
                        "source": source,
                        "document_id": document_id,
                        "document_title": metadata.get('document_title', 'Unknown'),
                        "document_year": metadata.get('document_year', 'Unknown'),
                        "authors": metadata.get('authors', 'Unknown'),
                        "journal": metadata.get('journal', 'Unknown'),
                        "category": metadata.get('category', 'Unknown'),
                        "chunk_count": 0,
                        "chunks": []
                    }
                
                # Add chunk information
                chunk_info = {
                    "chunk_id": metadata.get('chunk_id', 'unknown'),
                    "title": metadata.get('title', 'Untitled'),
                    "content_preview": results['documents'][i][:200] + "..." if len(results['documents'][i]) > 200 else results['documents'][i]
                }
                sources_info[source]["chunks"].append(chunk_info)
                sources_info[source]["chunk_count"] += 1
        
        # Convert to list and sort by chunk count (descending)
        sources_list = list(sources_info.values())
        sources_list.sort(key=lambda x: x["chunk_count"], reverse=True)
        
        return {
            "status": "success",
            "total_chunks": len(results['ids']) if results['ids'] else 0,
            "categories": category_counts,
            "unique_sources": len(sources_list),
            "sources": sources_list,
            "message": f"RAG knowledge base contains {len(results['ids']) if results['ids'] else 0} chunks across {len(category_counts)} categories from {len(sources_list)} sources"
        }
        
    except Exception as e:
        print(f"Error in get_rag_stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving RAG stats: {str(e)}")
