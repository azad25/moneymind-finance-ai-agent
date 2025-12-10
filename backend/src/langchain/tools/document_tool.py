"""
Document Search Tool
LangChain tool for searching user documents in Qdrant
"""
from typing import Optional, List
from langchain_core.tools import tool


@tool
async def search_documents(
    query: str,
    top_k: int = 5,
) -> str:
    """
    Search through user's uploaded documents using semantic search.
    
    Uses vector embeddings to find relevant document chunks.
    
    Args:
        query: Natural language search query
        top_k: Number of results to return (default: 5)
    
    Returns:
        Relevant excerpts from user's documents
    """
    from src.infrastructure.database.qdrant_client import qdrant_client
    from src.infrastructure.llm.huggingface_client import huggingface_client
    
    try:
        # Generate embedding for query
        embeddings = await huggingface_client.embeddings([query])
        
        if not embeddings or not embeddings[0]:
            return "❌ Could not generate embedding for search query."
        
        query_vector = embeddings[0]
        
        # Search Qdrant
        results = qdrant_client.search(
            query_vector=query_vector,
            top_k=top_k,
        )
        
        if not results:
            return f"📄 No documents found matching: '{query}'"
        
        # Format results
        output = f"📄 **Document Search Results** for '{query}':\n\n"
        
        for i, result in enumerate(results, 1):
            payload = result.get("payload", {})
            text = payload.get("text", "No content")
            filename = payload.get("filename", "Unknown")
            score = result.get("score", 0)
            
            # Truncate long text
            if len(text) > 300:
                text = text[:300] + "..."
            
            output += f"**{i}. {filename}** (relevance: {score:.2f})\n"
            output += f"> {text}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Document search error: {str(e)}"


@tool
async def get_document_summary(document_id: str) -> str:
    """
    Get a summary of a specific document.
    
    Args:
        document_id: The document ID to summarize
    
    Returns:
        AI-generated summary of the document
    """
    # TODO: Implement document summarization
    return f"📄 Document summary for {document_id}: Feature coming soon."
