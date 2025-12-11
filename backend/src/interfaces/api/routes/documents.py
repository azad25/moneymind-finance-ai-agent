"""
Document Management Routes
Upload, process, and query documents with LLM
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, UploadFile, File, Form, Query, Depends
from pydantic import BaseModel

from src.application.services.document_service import DocumentService
from src.interfaces.api.dependencies import get_current_user

router = APIRouter()


class DocumentResponse(BaseModel):
    """Document response model."""
    id: str
    filename: str
    content_type: str
    file_size: int
    chunk_count: int
    description: Optional[str] = None
    status: str  # processing, ready, failed
    created_at: str


class DocumentListResponse(BaseModel):
    """List of documents response."""
    documents: List[DocumentResponse]
    total: int


class DocumentQueryRequest(BaseModel):
    """Document query request."""
    query: str
    top_k: int = 5


class DocumentQueryResponse(BaseModel):
    """Document query response."""
    answer: str
    sources: List[dict]


class DocumentProcessResult(BaseModel):
    """Document processing result."""
    document_id: str
    filename: str
    content_type: str
    file_size: int
    chunk_count: int
    text_length: int
    financial_data: dict
    status: str


@router.post("/upload", response_model=DocumentProcessResult)
async def upload_document(
    file: UploadFile = File(...),
    description: Optional[str] = Form(None),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload and process a document (PDF, DOCX, Excel, CSV, TXT).
    
    The document will be:
    1. Text extracted based on file type
    2. Chunked for vector storage
    3. Embeddings generated
    4. Stored in Qdrant for semantic search
    5. Metadata saved to PostgreSQL
    6. Financial data extracted (if applicable)
    
    Supported formats:
    - PDF (.pdf)
    - Word (.docx)
    - Excel (.xlsx, .xls)
    - CSV (.csv)
    - Text (.txt)
    """
    service = DocumentService(user_id=current_user["id"])
    
    # Validate file type
    if not service.is_supported(file.content_type):
        raise HTTPException(
            status_code=400,
            detail=f"File type not supported: {file.content_type}. "
                   f"Supported: PDF, DOCX, XLSX, XLS, CSV, TXT"
        )
    
    # Read file content
    file_content = await file.read()
    
    if len(file_content) == 0:
        raise HTTPException(status_code=400, detail="Empty file")
    
    if len(file_content) > 10 * 1024 * 1024:  # 10MB limit
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")
    
    try:
        # Process document
        result = await service.process_document(
            file_content=file_content,
            filename=file.filename or "unknown",
            content_type=file.content_type,
            description=description,
        )
        
        return DocumentProcessResult(**result)
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@router.get("", response_model=DocumentListResponse)
async def list_documents(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    current_user: dict = Depends(get_current_user),
):
    """
    List all documents for the current user.
    """
    service = DocumentService(user_id=current_user["id"])
    documents = await service.list_documents(skip=skip, limit=limit)
    
    return DocumentListResponse(
        documents=[DocumentResponse(**doc) for doc in documents],
        total=len(documents)
    )


@router.get("/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Get document details by ID.
    """
    service = DocumentService(user_id=current_user["id"])
    document = await service.get_document(document_id)
    
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return DocumentResponse(**document)


@router.delete("/{document_id}")
async def delete_document(
    document_id: str,
    current_user: dict = Depends(get_current_user),
):
    """
    Delete a document and its embeddings.
    """
    service = DocumentService(user_id=current_user["id"])
    deleted = await service.delete_document(document_id)
    
    if not deleted:
        raise HTTPException(status_code=404, detail="Document not found")
    
    return {"message": "Document deleted successfully"}


@router.post("/{document_id}/query", response_model=DocumentQueryResponse)
async def query_document(
    document_id: str,
    request: DocumentQueryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Query a document using natural language.
    Uses vector search + LLM to answer questions.
    """
    from src.infrastructure.llm import get_llm
    
    service = DocumentService(user_id=current_user["id"])
    
    # Verify document exists
    document = await service.get_document(document_id)
    if not document:
        raise HTTPException(status_code=404, detail="Document not found")
    
    # Search for relevant chunks
    results = await service.search_documents(
        query=request.query,
        top_k=request.top_k,
    )
    
    # Filter by document_id
    results = [r for r in results if r.get("payload", {}).get("document_id") == document_id]
    
    if not results:
        return DocumentQueryResponse(
            answer=f"No relevant information found in {document['filename']}.",
            sources=[]
        )
    
    # Build context from results
    context = "\n\n".join([
        f"[Chunk {i+1}]: {r['payload']['text']}"
        for i, r in enumerate(results)
    ])
    
    # Use LLM to generate answer
    llm = await get_llm()
    
    prompt = f"""Based on the following excerpts from the document "{document['filename']}", answer the question.

Document excerpts:
{context}

Question: {request.query}

Provide a clear, concise answer based only on the information in the document."""
    
    try:
        response = await llm.chat([
            {"role": "system", "content": "You are a helpful assistant that answers questions based on document content."},
            {"role": "user", "content": prompt}
        ])
        
        answer = response.get("content", "Unable to generate answer.")
        
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
    
    return DocumentQueryResponse(
        answer=answer,
        sources=[
            {
                "text": r["payload"]["text"][:200] + "...",
                "score": r.get("score", 0),
                "chunk_index": r["payload"]["chunk_index"],
            }
            for r in results
        ]
    )


@router.post("/query-all", response_model=DocumentQueryResponse)
async def query_all_documents(
    request: DocumentQueryRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Query across all user documents.
    """
    from src.infrastructure.llm import get_llm
    
    service = DocumentService(user_id=current_user["id"])
    
    # Search all user documents
    results = await service.search_documents(
        query=request.query,
        top_k=request.top_k,
    )
    
    if not results:
        return DocumentQueryResponse(
            answer="No relevant information found in your documents.",
            sources=[]
        )
    
    # Build context from results
    context = "\n\n".join([
        f"[{r['payload']['filename']} - Chunk {r['payload']['chunk_index']}]: {r['payload']['text']}"
        for r in results
    ])
    
    # Use LLM to generate answer
    llm = await get_llm()
    
    prompt = f"""Based on the following excerpts from the user's documents, answer the question.

Document excerpts:
{context}

Question: {request.query}

Provide a clear, concise answer based on the information in the documents."""
    
    try:
        response = await llm.chat([
            {"role": "system", "content": "You are a helpful assistant that answers questions based on document content."},
            {"role": "user", "content": prompt}
        ])
        
        answer = response.get("content", "Unable to generate answer.")
        
    except Exception as e:
        answer = f"Error generating answer: {str(e)}"
    
    return DocumentQueryResponse(
        answer=answer,
        sources=[
            {
                "filename": r["payload"]["filename"],
                "text": r["payload"]["text"][:200] + "...",
                "score": r.get("score", 0),
            }
            for r in results
        ]
    )
