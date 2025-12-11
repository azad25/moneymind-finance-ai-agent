"""
Gmail API Routes
Full CRUD operations for Gmail integration
"""
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, EmailStr

from src.application.services.gmail_service import GmailService
from src.interfaces.api.dependencies import get_current_user

router = APIRouter()


class EmailSearchRequest(BaseModel):
    """Email search request."""
    query: str
    max_results: int = 10


class SendEmailRequest(BaseModel):
    """Send email request."""
    to: EmailStr
    subject: str
    body: str
    cc: Optional[str] = None
    bcc: Optional[str] = None
    html: bool = False


class ReplyEmailRequest(BaseModel):
    """Reply to email request."""
    body: str
    html: bool = False


class EmailResponse(BaseModel):
    """Email response model."""
    id: str
    subject: str
    sender: str
    date: str
    snippet: str


class EmailDetailResponse(BaseModel):
    """Detailed email response."""
    id: str
    subject: str
    sender: str
    date: str
    body: str


class SendEmailResponse(BaseModel):
    """Send email response."""
    id: str
    thread_id: str
    to: str
    subject: str
    status: str


@router.get("/status")
async def get_gmail_status(
    current_user: dict = Depends(get_current_user),
):
    """Check if Gmail is connected for the user."""
    service = GmailService(user_id=current_user["id"])
    is_connected = await service.is_connected()
    
    return {
        "connected": is_connected,
        "user_id": current_user["id"],
    }


@router.post("/search")
async def search_emails(
    request: EmailSearchRequest,
    current_user: dict = Depends(get_current_user),
):
    """
    Search Gmail inbox.
    
    Query examples:
    - "from:bank@example.com"
    - "subject:invoice"
    - "after:2024/01/01"
    - "is:unread"
    """
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(
            status_code=400,
            detail="Gmail not connected. Please connect your Gmail account."
        )
    
    try:
        emails = await service.search_emails(
            query=request.query,
            max_results=request.max_results,
        )
        
        return {
            "emails": [
                EmailResponse(
                    id=email["id"],
                    subject=email.get("subject", "No subject"),
                    sender=email.get("from", "Unknown"),
                    date=email.get("date", ""),
                    snippet=email.get("snippet", ""),
                )
                for email in emails
            ],
            "total": len(emails),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/recent")
async def get_recent_emails(
    max_results: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Get most recent emails."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        emails = await service.get_recent_emails(max_results=max_results)
        
        return {
            "emails": [
                EmailResponse(
                    id=email["id"],
                    subject=email.get("subject", "No subject"),
                    sender=email.get("from", "Unknown"),
                    date=email.get("date", ""),
                    snippet=email.get("snippet", ""),
                )
                for email in emails
            ],
            "total": len(emails),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/unread")
async def get_unread_emails(
    max_results: int = Query(10, ge=1, le=50),
    current_user: dict = Depends(get_current_user),
):
    """Get unread emails."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        emails = await service.get_unread_emails(max_results=max_results)
        
        return {
            "emails": [
                EmailResponse(
                    id=email["id"],
                    subject=email.get("subject", "No subject"),
                    sender=email.get("from", "Unknown"),
                    date=email.get("date", ""),
                    snippet=email.get("snippet", ""),
                )
                for email in emails
            ],
            "total": len(emails),
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{message_id}")
async def get_email(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Get full email details."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        email = await service.get_email_by_id(message_id)
        
        if not email:
            raise HTTPException(status_code=404, detail="Email not found")
        
        return EmailDetailResponse(
            id=email["id"],
            subject=email.get("subject", "No subject"),
            sender=email.get("from", "Unknown"),
            date=email.get("date", ""),
            body=email.get("body", ""),
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/send")
async def send_email(
    request: SendEmailRequest,
    current_user: dict = Depends(get_current_user),
):
    """Send an email via Gmail."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        result = await service.send_email(
            to=request.to,
            subject=request.subject,
            body=request.body,
            cc=request.cc,
            bcc=request.bcc,
            html=request.html,
        )
        
        return SendEmailResponse(**result)
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/reply")
async def reply_to_email(
    message_id: str,
    request: ReplyEmailRequest,
    current_user: dict = Depends(get_current_user),
):
    """Reply to an email."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        result = await service.reply_to_email(
            message_id=message_id,
            body=request.body,
            html=request.html,
        )
        
        return {
            "id": result["id"],
            "thread_id": result["thread_id"],
            "in_reply_to": message_id,
            "status": "sent",
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{message_id}/read")
async def mark_as_read(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Mark email as read."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    success = await service.mark_as_read(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark as read")
    
    return {"message": "Email marked as read"}


@router.post("/{message_id}/unread")
async def mark_as_unread(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Mark email as unread."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    success = await service.mark_as_unread(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to mark as unread")
    
    return {"message": "Email marked as unread"}


@router.post("/{message_id}/archive")
async def archive_email(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Archive email (remove from inbox)."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    success = await service.archive_email(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to archive email")
    
    return {"message": "Email archived"}


@router.delete("/{message_id}")
async def delete_email(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Delete email (move to trash)."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    success = await service.delete_email(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to delete email")
    
    return {"message": "Email moved to trash"}


@router.post("/{message_id}/star")
async def star_email(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Star an email."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    success = await service.star_email(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to star email")
    
    return {"message": "Email starred"}


@router.delete("/{message_id}/star")
async def unstar_email(
    message_id: str,
    current_user: dict = Depends(get_current_user),
):
    """Remove star from email."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    success = await service.unstar_email(message_id)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to unstar email")
    
    return {"message": "Star removed"}


@router.get("/banking/emails")
async def get_banking_emails(
    days: int = Query(30, ge=1, le=365),
    current_user: dict = Depends(get_current_user),
):
    """Get banking and financial emails."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        emails = await service.get_banking_emails(days=days)
        
        return {
            "emails": emails,
            "total": len(emails),
            "period_days": days,
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/banking/insights")
async def get_banking_insights(
    current_user: dict = Depends(get_current_user),
):
    """Get transaction insights from banking emails."""
    service = GmailService(user_id=current_user["id"])
    
    if not await service.is_connected():
        raise HTTPException(status_code=400, detail="Gmail not connected")
    
    try:
        insights = await service.get_transaction_insights()
        return insights
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
