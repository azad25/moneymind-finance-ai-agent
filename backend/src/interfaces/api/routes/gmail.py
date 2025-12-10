"""
Gmail Integration Routes
Fetch and process emails via Gmail API
"""
from typing import Optional, List
from datetime import datetime
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

router = APIRouter()


class EmailSummary(BaseModel):
    """Email summary model."""
    id: str
    thread_id: str
    subject: str
    sender: str
    snippet: str
    date: datetime
    has_attachments: bool
    labels: List[str]


class EmailListResponse(BaseModel):
    """Email list response."""
    emails: List[EmailSummary]
    total: int
    next_page_token: Optional[str]


class EmailDetailResponse(BaseModel):
    """Full email detail response."""
    id: str
    thread_id: str
    subject: str
    sender: str
    recipients: List[str]
    body_text: Optional[str]
    body_html: Optional[str]
    date: datetime
    attachments: List[dict]


class BankingEmailResponse(BaseModel):
    """Banking email with extracted transaction data."""
    id: str
    subject: str
    sender: str
    date: datetime
    transaction_type: Optional[str]  # credit, debit, transfer
    amount: Optional[float]
    currency: Optional[str]
    merchant: Optional[str]
    raw_content: str


class GmailAuthStatus(BaseModel):
    """Gmail authentication status."""
    connected: bool
    email: Optional[str]
    scopes: List[str]
    last_sync: Optional[datetime]


@router.get("/auth-status", response_model=GmailAuthStatus)
async def get_gmail_auth_status():
    """
    Check if user has connected Gmail.
    """
    # TODO: Check if user has Gmail refresh token
    return GmailAuthStatus(
        connected=False,
        email=None,
        scopes=[],
        last_sync=None
    )


@router.get("/emails", response_model=EmailListResponse)
async def list_emails(
    query: Optional[str] = Query(None, description="Gmail search query"),
    max_results: int = Query(20, ge=1, le=100),
    page_token: Optional[str] = None
):
    """
    List recent emails with optional search query.
    
    Query examples:
    - "from:bank" - Emails from banks
    - "subject:transaction" - Transaction notifications
    - "is:unread" - Unread emails
    - "after:2024/01/01" - Emails after date
    """
    # TODO: Check Gmail connection
    # TODO: Fetch emails via Gmail API
    return EmailListResponse(
        emails=[],
        total=0,
        next_page_token=None
    )


@router.get("/emails/{email_id}", response_model=EmailDetailResponse)
async def get_email(email_id: str):
    """
    Get full email details including body.
    """
    # TODO: Fetch email from Gmail API
    raise HTTPException(status_code=404, detail="Email not found")


@router.get("/banking", response_model=List[BankingEmailResponse])
async def get_banking_emails(
    days: int = Query(30, ge=1, le=365, description="Number of days to look back"),
    sources: Optional[str] = Query(None, description="Comma-separated bank domains")
):
    """
    Get banking-related emails with extracted transaction data.
    
    Automatically searches for emails from:
    - Major banks (chase, bofa, wells fargo, etc.)
    - Payment services (paypal, venmo, zelle)
    - Credit cards
    
    Extracts:
    - Transaction amounts
    - Merchant names
    - Transaction types
    """
    # TODO: Search Gmail for banking emails
    # TODO: Parse and extract transaction data
    return []


@router.post("/sync")
async def trigger_email_sync():
    """
    Trigger background sync of user's emails.
    
    This is a background task that:
    1. Fetches new emails since last sync
    2. Processes banking emails
    3. Extracts transactions
    4. Updates user's expense records
    """
    # TODO: Trigger Celery background task
    return {
        "message": "Email sync started",
        "task_id": "task_123"
    }


@router.get("/sync-status")
async def get_sync_status(task_id: str):
    """
    Check status of email sync task.
    """
    # TODO: Check Celery task status
    return {
        "task_id": task_id,
        "status": "pending",  # pending, running, completed, failed
        "progress": 0,
        "message": "Waiting to start"
    }


@router.post("/summarize")
async def summarize_emails(
    email_ids: List[str] = Query(..., description="Email IDs to summarize")
):
    """
    Summarize selected emails using LLM.
    """
    # TODO: Fetch emails
    # TODO: Use LLM to summarize
    return {
        "summary": "This is a mock summary of the selected emails.",
        "email_count": len(email_ids)
    }


@router.get("/insights")
async def get_email_insights():
    """
    Get insights from analyzed banking emails.
    
    Returns:
    - Total transactions this month
    - Top merchants
    - Spending by category (from email data)
    """
    # TODO: Aggregate transaction data from emails
    return {
        "total_transactions": 0,
        "total_amount": 0.0,
        "top_merchants": [],
        "by_category": {}
    }
