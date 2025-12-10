"""
LangGraph Agent State
Defines the state schema for the MoneyMind agent
"""
from typing import TypedDict, List, Optional, Annotated, Dict, Any
from datetime import datetime
from langgraph.graph import add_messages


class AgentState(TypedDict):
    """
    State schema for the MoneyMind LangGraph agent.
    
    This state is passed between nodes and maintains the context
    of the conversation and agent execution.
    """
    # Conversation history - uses add_messages reducer for proper message handling
    messages: Annotated[List[Dict[str, Any]], add_messages]
    
    # User context
    user_id: str
    user_name: Optional[str]
    
    # Current intent detected
    current_intent: Optional[str]
    
    # Tool execution results
    tool_results: List[Dict[str, Any]]
    
    # Error tracking
    error: Optional[str]
    retry_count: int
    
    # Memory context from vector DB
    memory_context: Optional[str]
    
    # Session metadata
    session_id: str
    started_at: datetime
    
    # Control flow
    next_node: Optional[str]
    should_respond: bool


def create_initial_state(
    user_id: str,
    session_id: str,
    user_name: Optional[str] = None,
) -> AgentState:
    """Create initial state for a new conversation."""
    return AgentState(
        messages=[],
        user_id=user_id,
        user_name=user_name,
        current_intent=None,
        tool_results=[],
        error=None,
        retry_count=0,
        memory_context=None,
        session_id=session_id,
        started_at=datetime.utcnow(),
        next_node=None,
        should_respond=True,
    )
