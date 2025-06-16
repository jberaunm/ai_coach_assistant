import chromadb
from chromadb.config import Settings
from pathlib import Path
import os
from typing import List, Dict, Any, Optional

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
            )
        )
        
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

# Create a singleton instance
chroma_service = ChromaService() 