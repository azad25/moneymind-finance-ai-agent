"""
Email Tools - REAL IMPLEMENTATION
LangChain tools for Gmail integration using Google API
"""
from typing import Optional, List
from langchain_core.tools import tool


@tool
async def search_emails(
    query: str,
    max_results: int = 10,
) -> str:
    """
    Search user's Gmail inbox using Gmail API.
    
    Args:
        query: Gmail search query (e.g., "from:bank", "subject:payment", "after:2024/01/01")
        max_results: Maximum number of emails to return (default: 10)
    
    Returns:
        List of matching emails with subject, sender, and date
    """
    from src.application.services.gmail_service import GmailService
    
    try:
        service = GmailService()
        
        # Check if Gmail is connected
        if not await service.is_connected():
            return "📧 Gmail is not connected. Please connect your Gmail account in Settings."
        
        # Search emails
        emails = await service.search_emails(query=query, max_results=max_results)
        
        if not emails:
            return f"📧 No emails found matching: '{query}'"
        
        output = f"📧 **Gmail Search Results** for '{query}'\n\n"
        output += "| Subject | From | Date |\n"
        output += "|---------|------|------|\n"
        
        for email in emails:
            subject = email.get("subject", "No subject")[:40]
            sender = email.get("from", "Unknown")[:30]
            date = email.get("date", "")
            output += f"| {subject} | {sender} | {date} |\n"
        
        output += f"\n*Found {len(emails)} emails*"
        return output
        
    except Exception as e:
        return f"❌ Email search error: {str(e)}"


@tool
async def get_banking_emails(days: int = 30) -> str:
    """
    Get banking and financial emails from the past N days.
    
    Automatically searches for emails from common banks and payment services.
    
    Args:
        days: Number of days to look back (default: 30)
    
    Returns:
        List of banking emails with extracted transaction data
    """
    from src.application.services.gmail_service import GmailService
    
    try:
        service = GmailService()
        
        if not await service.is_connected():
            return "🏦 Gmail is not connected. Connect Gmail to analyze banking emails."
        
        # Search for banking emails
        banking_emails = await service.get_banking_emails(days=days)
        
        if not banking_emails:
            return f"🏦 No banking emails found in the past {days} days."
        
        output = f"🏦 **Banking Emails** (Last {days} days)\n\n"
        
        total_credits = 0
        total_debits = 0
        
        for email in banking_emails:
            subject = email.get("subject", "No subject")
            sender = email.get("from", "Unknown")
            transactions = email.get("transactions", [])
            
            output += f"**{subject}**\n"
            output += f"*From: {sender}*\n"
            
            if transactions:
                for tx in transactions:
                    tx_type = tx.get("type", "unknown")
                    amount = tx.get("amount", 0)
                    merchant = tx.get("merchant", "Unknown")
                    
                    if tx_type == "credit":
                        output += f"  💚 +{amount:,.2f} from {merchant}\n"
                        total_credits += amount
                    else:
                        output += f"  🔴 -{amount:,.2f} to {merchant}\n"
                        total_debits += amount
            
            output += "\n"
        
        output += f"**Summary:**\n"
        output += f"- Total Credits: +{total_credits:,.2f}\n"
        output += f"- Total Debits: -{total_debits:,.2f}\n"
        output += f"- Net: {total_credits - total_debits:+,.2f}"
        
        return output
        
    except Exception as e:
        return f"❌ Banking email error: {str(e)}"


@tool
async def summarize_emails(
    query: Optional[str] = None,
    email_ids: Optional[List[str]] = None,
) -> str:
    """
    Summarize emails matching a query or specific email IDs.
    
    Uses AI to generate a concise summary of the email contents.
    
    Args:
        query: Gmail search query to find emails to summarize
        email_ids: Specific email IDs to summarize
    
    Returns:
        AI-generated summary of the emails
    """
    from src.application.services.gmail_service import GmailService
    from src.infrastructure.llm import get_llm
    
    try:
        service = GmailService()
        
        if not await service.is_connected():
            return "📝 Gmail is not connected."
        
        # Get emails
        if email_ids:
            emails = await service.get_emails_by_ids(email_ids)
        elif query:
            emails = await service.search_emails(query=query, max_results=5)
        else:
            return "📝 Please provide a query or email IDs to summarize."
        
        if not emails:
            return "📝 No emails found to summarize."
        
        # Build email content for summarization
        email_content = ""
        for email in emails:
            email_content += f"Subject: {email.get('subject', 'No subject')}\n"
            email_content += f"From: {email.get('from', 'Unknown')}\n"
            email_content += f"Body: {email.get('body', '')[:500]}\n\n"
        
        # Use LLM to summarize
        llm = await get_llm()
        
        prompt = f"""Summarize the following emails concisely. Focus on key information, action items, and important details:

{email_content}

Provide a brief summary in 2-3 paragraphs."""
        
        summary = await llm.chat([
            {"role": "system", "content": "You are a helpful assistant that summarizes emails."},
            {"role": "user", "content": prompt}
        ])
        
        return f"📝 **Email Summary**\n\n{summary}"
        
    except Exception as e:
        return f"❌ Email summarization error: {str(e)}"


@tool
async def extract_transactions_from_email(email_id: str) -> str:
    """
    Extract transaction details from a banking email.
    
    Parses the email content to find:
    - Transaction amount
    - Transaction type (credit/debit)
    - Merchant name
    - Date and time
    
    Args:
        email_id: Gmail email ID to process
    
    Returns:
        Extracted transaction details
    """
    from src.application.services.gmail_service import GmailService
    
    try:
        service = GmailService()
        
        if not await service.is_connected():
            return "💳 Gmail is not connected."
        
        # Get email content
        email = await service.get_email_by_id(email_id)
        
        if not email:
            return f"💳 Email not found: {email_id}"
        
        # Extract transactions
        transactions = await service.extract_transactions(email)
        
        if not transactions:
            return f"💳 No transactions found in email: {email.get('subject', 'Unknown')}"
        
        output = f"💳 **Transactions Extracted**\n\n"
        output += f"From: {email.get('subject', 'Unknown')}\n\n"
        
        for tx in transactions:
            tx_type = "Credit 💚" if tx.get("type") == "credit" else "Debit 🔴"
            output += f"- {tx_type}: {tx.get('amount', 0):,.2f}\n"
            output += f"  Merchant: {tx.get('merchant', 'Unknown')}\n"
            output += f"  Date: {tx.get('date', 'Unknown')}\n\n"
        
        return output
        
    except Exception as e:
        return f"❌ Transaction extraction error: {str(e)}"


@tool
async def get_email_insights() -> str:
    """
    Get insights from analyzed banking emails.
    
    Returns aggregated data about transactions detected in emails:
    - Total transaction count
    - Total amounts by type
    - Top merchants
    
    Returns:
        Summary of email-based financial insights
    """
    from src.application.services.gmail_service import GmailService
    
    try:
        service = GmailService()
        
        if not await service.is_connected():
            return "📊 Connect Gmail to see transaction insights from banking emails."
        
        insights = await service.get_transaction_insights()
        
        if not insights:
            return "📊 No transaction insights available. Try syncing your banking emails first."
        
        output = "📊 **Email Transaction Insights** (Last 30 days)\n\n"
        
        output += f"**Transaction Summary:**\n"
        output += f"- Total Transactions: {insights.get('total_count', 0)}\n"
        output += f"- Total Credits: +{insights.get('total_credits', 0):,.2f}\n"
        output += f"- Total Debits: -{insights.get('total_debits', 0):,.2f}\n"
        output += f"- Net Change: {insights.get('net_change', 0):+,.2f}\n\n"
        
        if insights.get("top_merchants"):
            output += "**Top Merchants:**\n"
            for merchant, amount in insights["top_merchants"][:5]:
                output += f"- {merchant}: {amount:,.2f}\n"
        
        return output
        
    except Exception as e:
        return f"❌ Insights error: {str(e)}"


# Export email tools
email_tools = [
    search_emails,
    get_banking_emails,
    summarize_emails,
    extract_transactions_from_email,
    get_email_insights,
]
