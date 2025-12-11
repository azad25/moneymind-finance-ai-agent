"""
User Context for LangChain Tools
Provides authenticated user context to tools
"""
from contextvars import ContextVar
from typing import Optional

# Context variable to store current user ID
current_user_id: ContextVar[Optional[str]] = ContextVar('current_user_id', default='default_user')


def set_user_context(user_id: str):
    """Set the current user context for tool execution."""
    current_user_id.set(user_id)


def get_user_context() -> str:
    """Get the current user ID from context."""
    return current_user_id.get()


def clear_user_context():
    """Clear the user context."""
    current_user_id.set('default_user')
