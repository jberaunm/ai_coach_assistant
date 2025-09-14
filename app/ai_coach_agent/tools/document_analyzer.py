"""
RAG knowledge chunking tools for processing document content and creating searchable knowledge chunks.
"""

import json
import hashlib
from typing import Dict, List, Any, Optional
from datetime import datetime
from .chromaDB_tools import chroma_service

def create_rag_chunks(
    content: str, 
    metadata: Optional[Dict[str, Any]] = None, 
    file_info: Optional[Dict[str, Any]] = None,
    category: str = "General",
    subcategory: Optional[str] = None
) -> Dict[str, Any]:
    """
    Create RAG knowledge chunks from document content.
    
    Args:
        content: Extracted text content
        metadata: Document metadata
        file_info: File information
        category: Main category (Training Plan or Session Analysis)
        subcategory: Optional subcategory
        
    Returns:
        Dict containing:
            - status: "success" or "error"
            - chunks_created: Number of chunks created
            - chunks: List of created chunks
    """
    try:
        print(f"[RAG_AGENT tool] Creating RAG chunks for category: {category}")
        
        # Set defaults if not provided
        if metadata is None:
            metadata = {}
        if file_info is None:
            file_info = {
                'doc_id': f"doc_{hashlib.md5(content.encode()).hexdigest()[:12]}",
                'file_name': 'uploaded_document',
                'uploaded_at': datetime.now().isoformat()
            }
        
        # Split content into chunks (200-500 words each)
        chunks = _split_into_chunks(content, target_size=300)
        
        # Prepare chunks for storage
        rag_chunks = []
        for i, chunk_content in enumerate(chunks):
            if not chunk_content.strip():
                continue
                
            chunk_id = f"{file_info['doc_id']}_chunk_{i+1:03d}"
            
            # Extract title from chunk (first sentence or first 50 chars)
            title = _extract_chunk_title(chunk_content)
            
            # Create chunk metadata
            chunk_metadata = {
                "chunk_id": chunk_id,
                "category": category,
                "subcategory": subcategory or "General",
                "title": title,
                "source": file_info['file_name'],
                "document_id": file_info['doc_id'],
                "chunk_index": i + 1,
                "total_chunks": len(chunks),
                "created_at": datetime.now().isoformat()
            }
            
            # Add document metadata if available
            if metadata.get('title'):
                chunk_metadata['document_title'] = metadata['title']
            if metadata.get('author') or metadata.get('authors'):
                chunk_metadata['authors'] = metadata.get('author') or metadata.get('authors')
            if metadata.get('year'):
                chunk_metadata['document_year'] = metadata['year']
            if metadata.get('journal'):
                chunk_metadata['journal'] = metadata['journal']
            if metadata.get('doi'):
                chunk_metadata['doi'] = metadata['doi']
            if metadata.get('abstract'):
                chunk_metadata['abstract'] = metadata['abstract']
            
            rag_chunks.append({
                "id": chunk_id,
                "content": chunk_content,
                "metadata": chunk_metadata
            })
        
        # Store chunks in ChromaDB
        if rag_chunks:
            _store_chunks_in_rag_knowledge(rag_chunks)
        
        print(f"[RAG_AGENT] Successfully created {len(rag_chunks)} RAG chunks")
        
        return {
            "status": "success",
            "chunks_created": len(rag_chunks),
            "chunks": rag_chunks,
            "message": f"Successfully created {len(rag_chunks)} RAG knowledge chunks"
        }
        
    except Exception as e:
        print(f"[RAG_AGENT] Error creating RAG chunks: {str(e)}")
        return {
            "status": "error",
            "chunks_created": 0,
            "chunks": [],
            "message": f"Error creating RAG chunks: {str(e)}"
        }

def _split_into_chunks(content: str, target_size: int = 300) -> List[str]:
    """Split content into chunks of approximately target_size words."""
    words = content.split()
    chunks = []
    
    current_chunk = []
    current_size = 0
    
    for word in words:
        current_chunk.append(word)
        current_size += 1
        
        # Check if we should create a chunk
        if current_size >= target_size:
            # Look for sentence boundary
            chunk_text = " ".join(current_chunk)
            
            # Try to break at sentence boundary
            last_period = chunk_text.rfind('.')
            last_exclamation = chunk_text.rfind('!')
            last_question = chunk_text.rfind('?')
            
            break_point = max(last_period, last_exclamation, last_question)
            
            if break_point > target_size // 2:  # If we found a good break point
                chunks.append(chunk_text[:break_point + 1].strip())
                remaining_text = chunk_text[break_point + 1:].strip()
                current_chunk = remaining_text.split() if remaining_text else []
                current_size = len(current_chunk)
            else:
                # No good break point, create chunk as is
                chunks.append(chunk_text.strip())
                current_chunk = []
                current_size = 0
    
    # Add remaining words as final chunk
    if current_chunk:
        chunks.append(" ".join(current_chunk).strip())
    
    return [chunk for chunk in chunks if chunk.strip()]

def _extract_chunk_title(chunk_content: str) -> str:
    """Extract a title from chunk content."""
    # Take first sentence or first 50 characters
    sentences = chunk_content.split('.')
    if sentences and len(sentences[0]) > 10:
        title = sentences[0].strip()
        if len(title) > 50:
            title = title[:47] + "..."
        return title
    else:
        # Fallback to first 50 characters
        title = chunk_content.strip()
        if len(title) > 50:
            title = title[:47] + "..."
        return title

def _store_chunks_in_rag_knowledge(chunks: List[Dict[str, Any]]) -> None:
    """Store chunks in the RAG knowledge ChromaDB collection."""
    try:
        # Get or create RAG knowledge collection
        rag_collection = chroma_service.client.get_or_create_collection(
            name="rag_knowledge",
            metadata={"description": "RAG knowledge base for running training insights"}
        )
        
        # Prepare data for ChromaDB
        documents = [chunk["content"] for chunk in chunks]
        metadatas = [chunk["metadata"] for chunk in chunks]
        ids = [chunk["id"] for chunk in chunks]
        
        # Add chunks to collection
        rag_collection.add(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
        
        print(f"[RAG_AGENT] Successfully stored {len(chunks)} chunks in RAG knowledge base")
        
    except Exception as e:
        print(f"[RAG_AGENT] Error storing chunks in RAG knowledge base: {str(e)}")
        raise e
