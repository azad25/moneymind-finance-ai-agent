"""
WebSocket Chat Endpoint - REAL IMPLEMENTATION
Real-time chat with LangGraph agent streaming
"""
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, Query, Header
from pydantic import BaseModel
import json
import asyncio
import uuid
from datetime import datetime
from src.config.settings import settings

router = APIRouter()


class ConnectionManager:
    """WebSocket connection manager for real-time chat."""
    
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
    
    async def connect(self, websocket: WebSocket, session_id: str, user_id: str):
        """Accept connection and store session info."""
        await websocket.accept()
        self.active_connections[session_id] = websocket
        self.user_sessions[session_id] = {
            "user_id": user_id,
            "connected_at": datetime.utcnow(),
            "messages": [],
        }
    
    def disconnect(self, session_id: str):
        """Remove connection and session."""
        if session_id in self.active_connections:
            del self.active_connections[session_id]
        if session_id in self.user_sessions:
            del self.user_sessions[session_id]
    
    async def send_json(self, session_id: str, data: dict):
        """Send JSON message to specific session."""
        if session_id in self.active_connections:
            await self.active_connections[session_id].send_json(data)
    
    def get_session_history(self, session_id: str) -> List[Dict]:
        """Get conversation history for session."""
        if session_id in self.user_sessions:
            return self.user_sessions[session_id].get("messages", [])
        return []
    
    def add_message(self, session_id: str, role: str, content: str):
        """Add message to session history."""
        if session_id in self.user_sessions:
            self.user_sessions[session_id]["messages"].append({
                "role": role,
                "content": content,
                "timestamp": datetime.utcnow().isoformat(),
            })


manager = ConnectionManager()


@router.websocket("/chat")
async def websocket_chat(
    websocket: WebSocket,
    token: Optional[str] = Query(None),
):
    """
    WebSocket endpoint for real-time chat with LangGraph agent.
    
    DEBUG: This endpoint is being called
    
    Connection URL: ws://localhost:8000/ws/chat?token=<jwt_token>
    
    Client -> Server Message Format:
    {
        "type": "message",
        "content": "User message here",
        "attachments": []  // optional
    }
    
    Server -> Client Response Format:
    {
        "type": "status" | "stream" | "complete" | "error" | "chart",
        "content": "Response content",
        "metadata": {}  // optional
    }
    
    Chart Response Example:
    {
        "type": "chart",
        "content": "",
        "chart": {
            "kind": "pie",
            "data": [...]
        }
    }
    """
    # Manual CORS check for WebSocket (CORSMiddleware doesn't handle WebSocket upgrades)
    import logging
    logger = logging.getLogger(__name__)
    
    logger.info("=" * 80)
    logger.info("WebSocket connection attempt received!")
    logger.info(f"Headers: {dict(websocket.headers)}")
    logger.info(f"Query params: token={token}")
    logger.info("=" * 80)
    
    # Generate session ID
    session_id = str(uuid.uuid4())
    
    # Get user_id from token
    user_id = "default_user"  # Default fallback
    if token:
        try:
            from src.application.services.auth_service import AuthService
            payload = AuthService.decode_token(token)
            user_id = payload.get("sub", "default_user")
        except Exception as e:
            logger.warning(f"Failed to decode token: {e}")
    
    # Set user context for tools
    from src.langchain.context import set_user_context
    set_user_context(user_id)
    
    try:
        # Accept connection
        await manager.connect(websocket, session_id, user_id)
        logger.info(f"✅ WebSocket connected: session={session_id}")
    except Exception as e:
        logger.error(f"❌ Failed to accept WebSocket: {e}")
        raise
    
    # Send welcome message
    await manager.send_json(session_id, {
        "type": "system",
        "content": "Connected to MoneyMind AI. How can I help you manage your finances today?",
        "session_id": session_id,
    })
    
    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            
            try:
                message = json.loads(data)
            except json.JSONDecodeError:
                await manager.send_json(session_id, {
                    "type": "error",
                    "content": "Invalid JSON format. Please send valid JSON messages."
                })
                continue
            
            # Validate message
            msg_type = message.get("type", "message")
            content = message.get("content", "")
            
            if not content and msg_type == "message":
                await manager.send_json(session_id, {
                    "type": "error",
                    "content": "Message content is required."
                })
                continue
            
            # Handle different message types
            if msg_type == "ping":
                await manager.send_json(session_id, {"type": "pong"})
                continue
            
            if msg_type == "clear":
                # Clear conversation history
                if session_id in manager.user_sessions:
                    manager.user_sessions[session_id]["messages"] = []
                await manager.send_json(session_id, {
                    "type": "system",
                    "content": "Conversation cleared."
                })
                continue
            
            # Process chat message with LangGraph
            manager.add_message(session_id, "user", content)
            
            await process_with_langgraph(
                session_id=session_id,
                user_id=user_id,
                content=content,
                history=manager.get_session_history(session_id),
            )
            
    except WebSocketDisconnect:
        manager.disconnect(session_id)
    except Exception as e:
        await manager.send_json(session_id, {
            "type": "error",
            "content": f"Connection error: {str(e)}"
        })
        manager.disconnect(session_id)


async def process_with_langgraph(
    session_id: str,
    user_id: str,
    content: str,
    history: List[Dict],
):
    """
    Process user message with LangGraph agent and stream response.
    
    This is the main integration point with the LangGraph agent.
    """
    from src.langgraph import run_agent
    
    try:
        # Stream responses from agent
        full_response = []
        
        async for chunk in run_agent(
            user_message=content,
            user_id=user_id,
            session_id=session_id,
            conversation_history=history[:-1],  # Exclude current message
        ):
            chunk_type = chunk.get("type", "stream")
            chunk_content = chunk.get("content", "")
            
            # Send chunk to client
            await manager.send_json(session_id, chunk)
            
            # Collect response content
            if chunk_type in ["stream", "complete"] and chunk_content:
                full_response.append(chunk_content)
            
            # Check for chart data in content
            if chunk_content and "```chart" in chunk_content:
                await send_chart_data(session_id, chunk_content)
        
        # Store assistant response in history
        if full_response:
            manager.add_message(session_id, "assistant", "".join(full_response))
        
    except Exception as e:
        await manager.send_json(session_id, {
            "type": "error",
            "content": f"Processing error: {str(e)}"
        })


async def send_chart_data(session_id: str, content: str):
    """
    Extract and send chart data from response content.
    
    Parses ```chart blocks and sends separate chart message.
    """
    import re
    
    chart_pattern = r'```chart\n(.*?)\n```'
    matches = re.findall(chart_pattern, content, re.DOTALL)
    
    for chart_json in matches:
        try:
            chart_data = json.loads(chart_json)
            await manager.send_json(session_id, {
                "type": "chart",
                "chart": chart_data,
            })
        except json.JSONDecodeError:
            pass  # Skip invalid chart JSON


@router.get("/chat/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    history = manager.get_session_history(session_id)
    return {"session_id": session_id, "messages": history}


@router.delete("/chat/history/{session_id}")
async def clear_chat_history(session_id: str):
    """Clear chat history for a session."""
    if session_id in manager.user_sessions:
        manager.user_sessions[session_id]["messages"] = []
        return {"message": "History cleared"}
    return {"message": "Session not found"}
