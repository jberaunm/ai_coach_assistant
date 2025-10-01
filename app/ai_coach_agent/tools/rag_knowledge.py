import json
from db.chroma_service import chroma_service
from typing import List, Dict, Any, Optional
from pydantic import BaseModel

class RAGKnowledgeChunk(BaseModel):
    chunk_id: str
    category: str
    title: str
    content: str
    source: str

def initialize_rag_knowledge():
    """Initialize the RAG knowledge base with research study chunks.
    
    Returns:
        Dict with status and message
    """
    try:
        # Create or get the RAG knowledge collection
        rag_collection = chroma_service.client.get_or_create_collection(
            name="rag_knowledge",
            metadata={"description": "RAG knowledge base for running training insights"}
        )
        
        chunks = [
            {
                "chunk_id": "physical_adaptation_001",
                "category": "Physical Adaptation",
                "title": "Session Structure",
                "content": "The structure of a training session consists of three sequential phases: warm-up, main workout, and cool-down. The warm-up prepares the body for exertion, the main workout includes the primary activities that target the training objective, and the cool-down gradually returns the body to its resting state. All coaches in the survey confirmed this three-part structure.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "physical_adaptation_002",
                "category": "Physical Adaptation",
                "title": "Principles of Adaptation",
                "content": "Physical adaptation in running is governed by the balance of workload, fatigue, and recovery. Good adaptation, known as 'supercompensation', occurs when workload and recovery are balanced, leading to an increased fitness baseline. Maladaptation, or overtraining, happens when recovery is not enough and fatigue builds up, potentially causing chronic underperformance.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "physical_adaptation_003",
                "category": "Physical Adaptation",
                "title": "Common Physical Mistakes",
                "content": "According to a survey of expert coaches, the most frequent and important mistake in physical training is 'Overdo it,' which means applying too much volume and intensity too soon. Other common mistakes include running too much at the very beginning of a training plan and starting individual workouts too fast.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "physical_adaptation_004",
                "category": "Physical Adaptation",
                "title": "Key Training Parameters",
                "content": "Expert coaches identified that the most essential parameters for designing and personalizing training sessions are the athlete's perceived effort or fatigue, and their running pace, including time and distance. While heart rate is used by some coaches, they recognize its potential for high variability and low reliability.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "technical_adaptation_001",
                "category": "Technical Adaptation",
                "title": "Individuality of Running Form",
                "content": "There is no single one-size-fits-all running technique that suits everyone, as running economy varies according to the physiological differences of each runner. All interviewed coaches agreed that runners should develop their own optimized running technique based on their body and should not simply copy or imitate the form of advanced runners.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "technical_adaptation_002",
                "category": "Technical Adaptation",
                "title": "Overstriding and Center of Mass",
                "content": "A primary goal of good running technique is to have the foot strike the ground close to the body's center of mass (COM). Striking the ground too far in front of the COM is known as overstriding and is considered a major technical mistake to correct, as identified by expert coaches.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "technical_adaptation_003",
                "category": "Technical Adaptation",
                "title": "Cadence Principles",
                "content": "Cadence refers to the number of steps taken per minute. While some coaches mention 180 steps per minute as an optimal value, survey results show a broader consensus that all athletes generally benefit from a high cadence.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "technical_adaptation_004",
                "category": "Technical Adaptation",
                "title": "Upper Body Technique",
                "content": "The runner's upper body is an important component of running technique. Most coaches agree that ideal upper body form includes a stable head, relaxed shoulders, elbows held close to the body, and arms that swing back and forth from the shoulders in a relaxed way.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "mental_adaptation_001",
                "category": "Mental Adaptation",
                "title": "Motivational Interventions",
                "content": "Expert coaches use various interventions to motivate their runners. Important motivational strategies include celebrating success, improvement, and good points, as well as showing and explaining to the athletes their progress and improvements.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "mental_adaptation_002",
                "category": "Mental Adaptation",
                "title": "Goal Setting Strategies",
                "content": "Goal setting is a methodology widely used by all interviewed and surveyed coaches to guide athletes. The most important goal-setting strategy is to set up realistic goals in collaboration with the athlete. Discussing gradual progression and setting up milestones are also key strategies.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "body_awareness_001",
                "category": "Body Awareness",
                "title": "Interpreting Bodily Sensations",
                "content": "A critical skill for runners is learning to distinguish between the pain produced by training, racing, and injuries. Expert coaches agree that learning to accurately listen and be aware of one's body is a key factor for long-term development.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            },
            {
                "chunk_id": "body_awareness_002",
                "category": "Body Awareness",
                "title": "Training by Perceived Effort",
                "content": "Expert coaches recognize that it is possible to prescribe personalized workouts based on an athlete's perceived effort. A runner's ability to identify their running pace and know how far they can push themselves is a crucial component of body awareness.",
                "source": "Cardenas Hernandez, F. P., Schneider, J., Di Mitri, D., Jivet, I., & Drachsler, H. (2024). Beyond hard workout: A multimodal framework for personalised running training with immersive technologies. British Journal of Educational Technology, 55(4), 1528-1559."
            }
        ]
        
        # Check if chunks already exist
        existing_results = rag_collection.get()
        if existing_results['ids']:
            return {
                "status": "success",
                "message": f"RAG knowledge base already initialized with {len(existing_results['ids'])} chunks"
            }
        
        # Prepare documents and metadata for ChromaDB
        documents = []
        metadatas = []
        ids = []
        
        for chunk in chunks:
            documents.append(chunk['content'])
            metadatas.append({
                "chunk_id": chunk['chunk_id'],
                "category": chunk['category'],
                "title": chunk['title'],
                "source": chunk['source']
            })
            ids.append(chunk['chunk_id'])
        
        # Add chunks to the collection
        rag_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        return {
            "status": "success",
            "message": f"Successfully initialized RAG knowledge base with {len(chunks)} chunks"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "message": f"Error initializing RAG knowledge base: {str(e)}"
        }

def retrieve_rag_knowledge(query: str, n_results: int = 3, category: Optional[str] = None) -> Dict[str, Any]:
    """Retrieve relevant knowledge chunks from the RAG knowledge base.
    
    Args:
        query: The search query
        n_results: Number of results to return (default: 3)
        category: Optional category filter (Physical Adaptation, Technical Adaptation, Mental Adaptation, Body Awareness)
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - chunks: List of relevant knowledge chunks
            - message: Description of the result
    """
    try:
        print(f"[RAG_knowledge_base] START: Retrieving RAG knowledge for query: {query}, category: {category}")
        # Get the RAG knowledge collection
        rag_collection = chroma_service.client.get_collection("rag_knowledge")
        
        # Prepare where clause for category filtering
        where_clause = None
        if category:
            where_clause = {"category": category}
        
        # Search for relevant chunks
        results = rag_collection.query(
            query_texts=[query],
            n_results=n_results,
            where=where_clause
        )
        
        # Format the results
        chunks = []
        if results['ids'] and results['ids'][0]:
            for i in range(len(results['ids'][0])):
                chunk = {
                    'id': results['ids'][0][i],
                    'content': results['documents'][0][i],
                    'metadata': results['metadatas'][0][i],
                    'distance': results['distances'][0][i] if 'distances' in results else None
                }
                chunks.append(chunk)
        print(f"[RAG_knowledge_base] FINISH: Retrieved {len(chunks)} relevant knowledge chunks")
        
        return {
            "status": "success",
            "chunks": chunks,
            "message": f"Retrieved {len(chunks)} relevant knowledge chunks"
        }
        
    except Exception as e:
        error_msg = str(e)
        print(f"[RAG_knowledge_base] ERROR: Error retrieving RAG knowledge: {error_msg}")
        
        # Handle specific cases more gracefully
        if "does not exist" in error_msg.lower() or "collection" in error_msg.lower():
            return {
                "status": "success",  # Treat missing collection as success with empty results
                "chunks": [],
                "message": "RAG knowledge base not yet initialized - no research documents available"
            }
        else:
            return {
                "status": "error",
                "chunks": [],
                "message": f"Error retrieving RAG knowledge: {error_msg}"
            }

def get_all_rag_categories() -> Dict[str, Any]:
    """Get all available categories in the RAG knowledge base.
    
    Returns:
        Dict containing:
            - status: "success" or "error"
            - categories: List of available categories
            - message: Description of the result
    """
    try:
        # Get the RAG knowledge collection
        rag_collection = chroma_service.client.get_collection("rag_knowledge")
        
        # Get all chunks
        results = rag_collection.get()
        
        # Extract unique categories
        categories = set()
        if results['metadatas']:
            for metadata in results['metadatas']:
                if 'category' in metadata:
                    categories.add(metadata['category'])
        
        return {
            "status": "success",
            "categories": list(categories),
            "message": f"Found {len(categories)} categories in RAG knowledge base"
        }
        
    except Exception as e:
        return {
            "status": "error",
            "categories": [],
            "message": f"Error retrieving categories: {str(e)}"
        }
