"""
DateTime Tool
Provides current date and time information to the AI
"""
from datetime import datetime, date
from langchain_core.tools import tool


@tool
def get_current_date() -> str:
    """
    Get the current date and time.
    
    Use this when you need to know today's date for creating expenses,
    goals, bills, or any other date-based operations.
    
    Returns:
        Current date in YYYY-MM-DD format and full datetime info
    """
    now = datetime.now()
    today = date.today()
    
    return (
        f"📅 **Current Date & Time**\n\n"
        f"**Date:** {today.strftime('%Y-%m-%d')} ({today.strftime('%A, %B %d, %Y')})\n"
        f"**Time:** {now.strftime('%H:%M:%S')}\n"
        f"**ISO Format:** {now.isoformat()}\n\n"
        f"Use `{today.strftime('%Y-%m-%d')}` for date fields."
    )


@tool
def get_today() -> str:
    """
    Get today's date in YYYY-MM-DD format.
    
    Quick tool to get just the date without extra information.
    
    Returns:
        Today's date as YYYY-MM-DD string
    """
    return date.today().strftime('%Y-%m-%d')


# Export tools
datetime_tools = [
    get_current_date,
    get_today,
]
