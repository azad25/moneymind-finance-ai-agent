"""
Document Tools
LangChain tools for document search and analysis
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
    Perfect for finding receipts, invoices, bank statements, or any financial documents.
    
    Args:
        query: Natural language search query (e.g., "bank statement", "receipt for coffee")
        top_k: Number of results to return (default: 5)
    
    Returns:
        Relevant excerpts from user's documents with filenames and relevance scores
    """
    from src.langchain.context import get_user_context
    from src.application.services.document_service import DocumentService
    
    try:
        # Get user context
        user_context = get_user_context()
        if not user_context or not user_context.get("user_id"):
            return "📄 Please log in to search your documents."
        
        user_id = user_context["user_id"]
        service = DocumentService(user_id=user_id)
        
        # Search documents
        results = await service.search_documents(query=query, top_k=top_k)
        
        if not results:
            return f"📄 No documents found matching: '{query}'\n\nTip: Upload documents using the upload feature."
        
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
async def list_my_documents() -> str:
    """
    List all documents uploaded by the user.
    
    Shows document names, types, sizes, and upload dates.
    
    Returns:
        List of user's documents
    """
    from src.langchain.context import get_user_context
    from src.application.services.document_service import DocumentService
    
    try:
        user_context = get_user_context()
        if not user_context or not user_context.get("user_id"):
            return "📄 Please log in to view your documents."
        
        user_id = user_context["user_id"]
        service = DocumentService(user_id=user_id)
        
        documents = await service.list_documents(limit=50)
        
        if not documents:
            return "📄 You haven't uploaded any documents yet.\n\nUpload PDFs, Excel files, or text documents to get started!"
        
        output = f"📄 **Your Documents** ({len(documents)} total)\n\n"
        output += "| Filename | Type | Size | Uploaded |\n"
        output += "|----------|------|------|----------|\n"
        
        for doc in documents:
            filename = doc["filename"][:30]
            file_type = doc["content_type"].split("/")[-1].upper()
            size_kb = doc["file_size"] / 1024
            uploaded = doc["created_at"][:10]
            
            output += f"| {filename} | {file_type} | {size_kb:.1f}KB | {uploaded} |\n"
        
        return output
        
    except Exception as e:
        return f"❌ Error listing documents: {str(e)}"


@tool
async def extract_expenses_from_document(query: str) -> str:
    """
    Search documents for expense information and extract financial data.
    
    Useful for finding receipts, invoices, or expense reports and extracting:
    - Amounts
    - Merchants
    - Dates
    - Categories
    
    Args:
        query: Search query to find relevant documents (e.g., "restaurant receipts", "December expenses")
    
    Returns:
        Extracted expense information from matching documents
    """
    from src.langchain.context import get_user_context
    from src.application.services.document_service import DocumentService
    from src.infrastructure.llm import get_llm
    
    try:
        user_context = get_user_context()
        if not user_context or not user_context.get("user_id"):
            return "💰 Please log in to extract expense data."
        
        user_id = user_context["user_id"]
        service = DocumentService(user_id=user_id)
        
        # Search for relevant documents
        results = await service.search_documents(query=query, top_k=3)
        
        if not results:
            return f"💰 No documents found matching: '{query}'"
        
        # Build context from documents
        context = ""
        for result in results:
            payload = result.get("payload", {})
            context += f"Document: {payload.get('filename', 'Unknown')}\n"
            context += f"Content: {payload.get('text', '')}\n\n"
        
        # Use LLM to extract structured expense data
        llm = await get_llm()
        
        prompt = f"""Extract expense information from the following document excerpts.

{context}

For each expense found, extract:
- Amount (with currency)
- Merchant/vendor name
- Date (if available)
- Category (food, transport, utilities, etc.)

Format as a clear list. If no expenses found, say so."""
        
        response = await llm.chat([
            {"role": "system", "content": "You are a financial data extraction assistant."},
            {"role": "user", "content": prompt}
        ])
        
        extracted_data = response.get("content", "Unable to extract expense data.")
        
        output = f"💰 **Expense Data Extracted** from documents matching '{query}':\n\n"
        output += extracted_data
        output += "\n\n*Tip: Use create_expense tool to save these to your expense tracker.*"
        
        return output
        
    except Exception as e:
        return f"❌ Extraction error: {str(e)}"


# Export document tools
document_tools = [
    search_documents,
    list_my_documents,
    extract_expenses_from_document,
]
