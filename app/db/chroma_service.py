import chromadb
from chromadb.config import Settings
from pathlib import Path
import os
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta

class ChromaService:
    def __init__(self):
        # Get the absolute path to the app directory
        APP_DIR = Path(__file__).parent.parent
        DB_DIR = APP_DIR / "data" / "chroma"
        
        # Create the database directory if it doesn't exist
        DB_DIR.mkdir(parents=True, exist_ok=True)
        
        # Initialize ChromaDB client
        self.client = chromadb.PersistentClient(
            path=str(DB_DIR),
            settings=Settings(
                anonymized_telemetry=False,
                allow_reset=True
                #is_persistent=True
            )
        )
        
        # Disable telemetry to avoid capture() error
        try:
            import chromadb.telemetry as telemetry_module
            telemetry_module.TelemetryClient = None
        except:
            pass
        
        # Create or get the main collection
        self.collection = self.client.get_or_create_collection(
            name="agent_memory",
            metadata={"description": "Memory storage for AI agents"}
        )
    
    def add_memory(self, 
                   text: str, 
                   metadata: Optional[Dict[str, Any]] = None,
                   embedding: Optional[List[float]] = None) -> str:
        """Add a new memory to the database"""
        if metadata is None:
            metadata = {}
            
        # Generate a unique ID for the memory
        memory_id = f"memory_{len(self.collection.get()['ids']) + 1}"
        
        # Add the memory to the collection
        self.collection.add(
            documents=[text],
            metadatas=[metadata],
            ids=[memory_id],
            embeddings=[embedding] if embedding else None
        )
        
        return memory_id
    
    def search_memories(self, 
                       query: str, 
                       n_results: int = 5,
                       where: Optional[Dict[str, Any]] = None) -> List[Dict[str, Any]]:
        """Search for relevant memories"""
        results = self.collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where
        )
        
        # Format the results
        memories = []
        for i in range(len(results['ids'][0])):
            memory = {
                'id': results['ids'][0][i],
                'text': results['documents'][0][i],
                'metadata': results['metadatas'][0][i],
                'distance': results['distances'][0][i] if 'distances' in results else None
            }
            memories.append(memory)
            
        return memories
    
    def get_memory(self, memory_id: str) -> Optional[Dict[str, Any]]:
        """Get a specific memory by ID"""
        try:
            result = self.collection.get(ids=[memory_id])
            if not result['ids']:
                return None
                
            return {
                'id': result['ids'][0],
                'text': result['documents'][0],
                'metadata': result['metadatas'][0]
            }
        except Exception:
            return None
    
    def delete_memory(self, memory_id: str) -> bool:
        """Delete a memory by ID"""
        try:
            self.collection.delete(ids=[memory_id])
            return True
        except Exception:
            return False

    def store_training_plan(self, sessions: List[Dict], metadata: Dict) -> str:
        """Store training plan sessions in ChromaDB.
        
        Args:
            sessions: List of session dictionaries
            metadata: Additional metadata for the plan
            
        Returns:
            str: Plan ID
        """
        try:
            # Generate unique IDs for each session
            ids = [f"session_{i:03d}" for i in range(1, len(sessions) + 1)]
            
            # Create document strings for each session
            documents = []
            for session in sessions:
                doc = f"Session planned for {session['date']}, {session['distance']} {session['type']}"
                if session.get('notes'):
                    doc += f", {session['notes']}"
                documents.append(doc)
            
            # Prepare metadata for each session with new structure
            metadatas = []
            for session in sessions:
                session_metadata = {
                    "date": session["date"],
                    "day": session["day"],
                    "type": session["type"],
                    "distance": session["distance"],
                    "notes": session.get("notes", ""),
                    # New fields with default empty values (serialized as JSON strings)
                    "calendar": json.dumps({
                        "events": []
                    }),
                    "weather": json.dumps({
                        "hours": []
                    }),
                    "time_scheduled": json.dumps([]),
                    "session_completed": False
                }
                metadatas.append(session_metadata)
            
            # Add the sessions to the collection
            self.collection.add(
                ids=ids,
                documents=documents,
                metadatas=metadatas
            )
            
            return "success"
            
        except Exception as e:
            print(f"Error storing training plan: {str(e)}")
            return str(e)
    
    def get_training_plan(self, plan_id: str) -> Dict:
        """Retrieve a training plan by ID."""
        try:
            results = self.collection.get(
                where={"plan_id": plan_id}
            )
            return results
        except Exception as e:
            print(f"Error retrieving training plan: {str(e)}")
            return None
        


    def update_session_calendar(self, session_id: str, calendar_events: List[Dict]) -> bool:
        """Update calendar events for a specific session.
        
        Args:
            session_id: The session ID to update
            calendar_events: List of calendar events
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current session metadata
            result = self.collection.get(ids=[session_id])
            if not result['ids']:
                return False
            
            current_metadata = result['metadatas'][0]
            
            # Update calendar events
            current_metadata['calendar'] = json.dumps({
                "events": calendar_events
            })
            
            # Update the session
            self.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating session calendar: {str(e)}")
            return False

    def update_session_weather(self, session_id: str, weather_data: Dict) -> bool:
        """Update weather data for a specific session.
        
        Args:
            session_id: The session ID to update
            weather_data: Weather data with hours array
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current session metadata
            result = self.collection.get(ids=[session_id])
            if not result['ids']:
                return False
            
            current_metadata = result['metadatas'][0]
            
            # Update weather data
            current_metadata['weather'] = json.dumps(weather_data)
            
            # Update the session
            self.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating session weather: {str(e)}")
            return False

    def update_session_time_scheduled(self, session_id: str, time_scheduled: List[Dict]) -> bool:
        """Update time scheduling for a specific session.
        
        Args:
            session_id: The session ID to update
            time_scheduled: List of scheduled time slots
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current session metadata
            result = self.collection.get(ids=[session_id])
            if not result['ids']:
                return False
            
            current_metadata = result['metadatas'][0]
            
            # Update time scheduled
            current_metadata['time_scheduled'] = json.dumps(time_scheduled)
            
            # Update the session
            self.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating session time scheduled: {str(e)}")
            return False

    def update_session_status(self, session_id: str, session_completed: bool) -> bool:
        """Update session completion status.
        
        Args:
            session_id: The session ID to update
            session_completed: Whether the session is completed
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current session metadata
            result = self.collection.get(ids=[session_id])
            if not result['ids']:
                return False
            
            current_metadata = result['metadatas'][0]
            
            # Update session completion status
            current_metadata['session_completed'] = session_completed
            
            # Update the session
            self.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating session status: {str(e)}")
            return False

    def update_session_metadata(self, session_id: str, updates: Dict) -> bool:
        """Update multiple metadata fields for a specific session.
        
        Args:
            session_id: The session ID to update
            updates: Dictionary of metadata fields to update
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Get current session metadata
            result = self.collection.get(ids=[session_id])
            if not result['ids']:
                return False
            
            current_metadata = result['metadatas'][0]
            
            # Update the metadata with new values
            current_metadata.update(updates)
            
            # Update the session
            self.collection.update(
                ids=[session_id],
                metadatas=[current_metadata]
            )
            
            return True
            
        except Exception as e:
            print(f"Error updating session metadata: {str(e)}")
            return False

    def _deserialize_metadata(self, metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Helper method to deserialize JSON strings in metadata back to objects."""
        try:
            deserialized = metadata.copy()
            
            # Deserialize calendar events
            if 'calendar' in deserialized and isinstance(deserialized['calendar'], str):
                try:
                    deserialized['calendar'] = json.loads(deserialized['calendar'])
                except json.JSONDecodeError:
                    deserialized['calendar'] = {"events": []}
            
            # Deserialize weather data
            if 'weather' in deserialized and isinstance(deserialized['weather'], str):
                try:
                    deserialized['weather'] = json.loads(deserialized['weather'])
                except json.JSONDecodeError:
                    deserialized['weather'] = {"hours": []}
            
            # Deserialize time scheduled
            if 'time_scheduled' in deserialized and isinstance(deserialized['time_scheduled'], str):
                try:
                    deserialized['time_scheduled'] = json.loads(deserialized['time_scheduled'])
                except json.JSONDecodeError:
                    deserialized['time_scheduled'] = []
            
            return deserialized
        except Exception as e:
            print(f"Error deserializing metadata: {str(e)}")
            return metadata

    def get_session_by_date(self, date: str) -> List[Dict]:
        """Get sessions from a specific date IN THE FORMAT YYYY-MM-DD"""
        try:
            results = self.collection.get(where={"date": date})
            
            # Deserialize JSON strings in metadata
            if results and 'metadatas' in results:
                for i, metadata in enumerate(results['metadatas']):
                    results['metadatas'][i] = self._deserialize_metadata(metadata)
            
            return results
        except Exception as e:
            print(f"Error retrieving today's sessions: {str(e)}")
            return []

    def get_upcoming_sessions(self, days: int = 7) -> List[Dict]:
        """Get sessions scheduled for the next n days."""
        try:
            today = datetime.now()
            end_date = (today + timedelta(days=days)).strftime("%Y-%m-%d")
            
            results = self.collection.query(
                where={
                    "date": {
                        "$gte": today.strftime("%Y-%m-%d"),
                        "$lte": end_date
                    }
                }
            )
            
            # Deserialize JSON strings in metadata
            if results and 'metadatas' in results and results['metadatas']:
                for i, metadata in enumerate(results['metadatas'][0]):
                    results['metadatas'][0][i] = self._deserialize_metadata(metadata)
            
            return results
        except Exception as e:
            print(f"Error retrieving upcoming sessions: {str(e)}")
            return []

    def list_all_sessions(self) -> Dict:
        """List all sessions stored in ChromaDB.
        
        Returns:
            Dict containing:
                - status: "success" or "error"
                - data: List of all sessions with their IDs, documents, and metadata
                - count: Total number of sessions
        """
        try:
            # Get all data from the collection
            results = self.collection.get()
            
            if not results:
                return {
                    "status": "success",
                    "data": [],
                    "count": 0,
                    "message": "No sessions found in ChromaDB"
                }
            
            # Format the results and deserialize metadata
            sessions = []
            for i in range(len(results['ids'])):
                metadata = self._deserialize_metadata(results['metadatas'][i])
                session = {
                    "id": results['ids'][i],
                    "document": results['documents'][i],
                    "metadata": metadata
                }
                sessions.append(session)
            
            return {
                "status": "success",
                "data": sessions,
                "count": len(sessions),
                "message": f"Found {len(sessions)} sessions in ChromaDB"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "data": None,
                "count": 0,
                "message": f"Error listing sessions: {str(e)}"
            }

# Create a singleton instance
chroma_service = ChromaService() 