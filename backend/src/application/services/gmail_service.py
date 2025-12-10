"""
Gmail Service - REAL IMPLEMENTATION
Gmail API integration for email operations
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import re
import base64
from email.utils import parsedate_to_datetime

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build

from src.config.settings import settings


class GmailService:
    """Service for Gmail API operations."""
    
    def __init__(self, user_id: str = "default_user"):
        self.user_id = user_id
        self._service = None
        self._credentials = None
    
    async def is_connected(self) -> bool:
        """Check if Gmail is connected for the user."""
        try:
            # Get user's refresh token from database
            from src.infrastructure.database.postgres import async_session_factory
            from src.domain.models.user import User
            from sqlalchemy import select
            
            async with async_session_factory() as session:
                result = await session.execute(
                    select(User).where(User.id == self.user_id)
                )
                user = result.scalar_one_or_none()
                
                if user and user.google_refresh_token:
                    return True
                return False
                
        except Exception:
            return False
    
    async def _get_service(self):
        """Get authenticated Gmail API service."""
        if self._service:
            return self._service
        
        # Get refresh token from database
        from src.infrastructure.database.postgres import async_session_factory
        from src.domain.models.user import User
        from sqlalchemy import select
        
        async with async_session_factory() as session:
            result = await session.execute(
                select(User).where(User.id == self.user_id)
            )
            user = result.scalar_one_or_none()
            
            if not user or not user.google_refresh_token:
                raise ValueError("Gmail not connected")
            
            # Create credentials
            self._credentials = Credentials(
                token=None,
                refresh_token=user.google_refresh_token,
                token_uri="https://oauth2.googleapis.com/token",
                client_id=settings.google_client_id,
                client_secret=settings.google_client_secret,
                scopes=["https://www.googleapis.com/auth/gmail.readonly"],
            )
            
            # Refresh if needed
            if self._credentials.expired or not self._credentials.valid:
                self._credentials.refresh(Request())
            
            # Build service
            self._service = build("gmail", "v1", credentials=self._credentials)
            return self._service
    
    async def search_emails(
        self,
        query: str,
        max_results: int = 10,
    ) -> List[Dict[str, Any]]:
        """Search emails using Gmail API."""
        service = await self._get_service()
        
        # Search for messages
        results = service.users().messages().list(
            userId="me",
            q=query,
            maxResults=max_results,
        ).execute()
        
        messages = results.get("messages", [])
        emails = []
        
        for msg in messages:
            email = await self._get_email_metadata(service, msg["id"])
            if email:
                emails.append(email)
        
        return emails
    
    async def _get_email_metadata(
        self,
        service,
        message_id: str,
    ) -> Optional[Dict[str, Any]]:
        """Get email metadata (headers only)."""
        try:
            message = service.users().messages().get(
                userId="me",
                id=message_id,
                format="metadata",
                metadataHeaders=["Subject", "From", "Date"],
            ).execute()
            
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
            
            return {
                "id": message_id,
                "subject": headers.get("Subject", "No subject"),
                "from": headers.get("From", "Unknown"),
                "date": headers.get("Date", ""),
                "snippet": message.get("snippet", ""),
            }
            
        except Exception:
            return None
    
    async def get_email_by_id(self, email_id: str) -> Optional[Dict[str, Any]]:
        """Get full email content by ID."""
        service = await self._get_service()
        
        try:
            message = service.users().messages().get(
                userId="me",
                id=email_id,
                format="full",
            ).execute()
            
            headers = {h["name"]: h["value"] for h in message["payload"]["headers"]}
            
            # Extract body
            body = ""
            if "parts" in message["payload"]:
                for part in message["payload"]["parts"]:
                    if part["mimeType"] == "text/plain":
                        data = part["body"].get("data", "")
                        body = base64.urlsafe_b64decode(data).decode("utf-8")
                        break
            elif "body" in message["payload"]:
                data = message["payload"]["body"].get("data", "")
                body = base64.urlsafe_b64decode(data).decode("utf-8")
            
            return {
                "id": email_id,
                "subject": headers.get("Subject", "No subject"),
                "from": headers.get("From", "Unknown"),
                "date": headers.get("Date", ""),
                "body": body,
            }
            
        except Exception:
            return None
    
    async def get_emails_by_ids(self, email_ids: List[str]) -> List[Dict[str, Any]]:
        """Get multiple emails by IDs."""
        emails = []
        for email_id in email_ids:
            email = await self.get_email_by_id(email_id)
            if email:
                emails.append(email)
        return emails
    
    async def get_banking_emails(self, days: int = 30) -> List[Dict[str, Any]]:
        """Get banking and financial emails."""
        # Build query for banking emails
        bank_keywords = [
            "from:bank",
            "from:paypal",
            "from:stripe",
            "from:venmo",
            "from:chase",
            "from:wellsfargo",
            "from:bankofamerica",
            "from:citi",
            "subject:transaction",
            "subject:payment",
            "subject:receipt",
            "subject:purchase",
            "subject:withdrawal",
            "subject:deposit",
        ]
        
        # Date filter
        after_date = (datetime.now() - timedelta(days=days)).strftime("%Y/%m/%d")
        query = f"after:{after_date} ({' OR '.join(bank_keywords)})"
        
        emails = await self.search_emails(query=query, max_results=50)
        
        # Parse transactions from each email
        for email in emails:
            full_email = await self.get_email_by_id(email["id"])
            if full_email:
                email["body"] = full_email.get("body", "")
                email["transactions"] = self._parse_transactions(full_email)
        
        return emails
    
    def _parse_transactions(self, email: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Parse transaction information from email body."""
        transactions = []
        body = email.get("body", "")
        
        # Common transaction patterns
        patterns = [
            # Amount with currency
            r'\$\s*([\d,]+\.?\d*)',
            r'([\d,]+\.?\d*)\s*(?:USD|usd|EUR|eur|GBP|gbp|THB|thb)',
            # Credit/debit keywords
            r'(?:credited|deposited|received)\s*\$?\s*([\d,]+\.?\d*)',
            r'(?:debited|charged|spent|paid)\s*\$?\s*([\d,]+\.?\d*)',
        ]
        
        for pattern in patterns[:2]:  # Amount patterns
            matches = re.findall(pattern, body)
            for match in matches:
                amount = float(match.replace(",", ""))
                if amount > 0 and amount < 1000000:  # Sanity check
                    # Determine type based on context
                    tx_type = "credit" if any(w in body.lower() for w in 
                        ["credited", "deposited", "received", "refund"]) else "debit"
                    
                    transactions.append({
                        "amount": amount,
                        "type": tx_type,
                        "merchant": self._extract_merchant(body),
                        "date": email.get("date", ""),
                    })
                    break  # One transaction per email for now
        
        return transactions
    
    def _extract_merchant(self, body: str) -> str:
        """Extract merchant name from email body."""
        # Common patterns for merchant names
        patterns = [
            r'(?:from|at|to)\s+([A-Z][A-Za-z\s]+?)(?:\s+for|\s+on|\.|$)',
            r'(?:Payment to|Paid to)\s+([A-Z][A-Za-z\s]+)',
            r'(?:Purchase at)\s+([A-Z][A-Za-z\s]+)',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, body)
            if match:
                return match.group(1).strip()[:50]
        
        return "Unknown"
    
    async def extract_transactions(self, email: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Extract transactions from a single email."""
        return self._parse_transactions(email)
    
    async def get_transaction_insights(self) -> Dict[str, Any]:
        """Get aggregated insights from banking emails."""
        emails = await self.get_banking_emails(days=30)
        
        total_credits = 0
        total_debits = 0
        total_count = 0
        merchant_totals = {}
        
        for email in emails:
            for tx in email.get("transactions", []):
                amount = tx.get("amount", 0)
                merchant = tx.get("merchant", "Unknown")
                
                if tx.get("type") == "credit":
                    total_credits += amount
                else:
                    total_debits += amount
                
                total_count += 1
                merchant_totals[merchant] = merchant_totals.get(merchant, 0) + amount
        
        # Sort merchants by total
        top_merchants = sorted(
            merchant_totals.items(),
            key=lambda x: x[1],
            reverse=True
        )[:10]
        
        return {
            "total_count": total_count,
            "total_credits": total_credits,
            "total_debits": total_debits,
            "net_change": total_credits - total_debits,
            "top_merchants": top_merchants,
        }
