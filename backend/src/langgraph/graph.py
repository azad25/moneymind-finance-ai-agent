"""
LangGraph Agent Graph - REAL IMPLEMENTATION
Complete agent with LLM tool calling, database operations, and streaming
"""
from typing import Dict, Any, AsyncIterator, Literal, List, Sequence
from datetime import datetime
import json
import uuid

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langchain_core.messages import (
    HumanMessage, 
    AIMessage, 
    SystemMessage,
    ToolMessage,
    BaseMessage,
)
from langchain_core.tools import BaseTool

from .state import AgentState, create_initial_state
from src.langchain.tools.expense_tools import expense_tools
from src.langchain.tools.income_tools import income_tools
from src.langchain.tools.chart_tool import generate_chart
from src.langchain.tools.exchange_rate_tool import convert_currency, get_exchange_rate
from src.langchain.tools.email_tools import email_tools
from src.langchain.tools.stock_tool import get_stock_price, get_stock_quote
from src.langchain.tools.document_tool import document_tools
from src.langchain.tools.sandbox_tool import sandbox_tools
from src.langchain.tools.datetime_tool import datetime_tools


# System prompt for the MoneyMind agent
SYSTEM_PROMPT = """You are MoneyMind, an AI personal finance assistant.

You have access to the following tools to help users manage their finances:

EXPENSE MANAGEMENT:
- create_expense: Create a new expense entry
- list_expenses: List expenses with optional filters
- get_spending_by_category: Get spending breakdown by category
- create_subscription: Create a recurring subscription
- list_subscriptions: List all active subscriptions
- create_bill: Create a bill/payment reminder
- list_upcoming_bills: List bills due soon
- create_goal: Create a financial savings goal
- list_goals: List all financial goals

INCOME & BALANCE:
- create_income: Add income record (salary, freelance, etc.)
- list_income: List income records
- get_balance: Get current account balance
- get_income_vs_expenses: Compare income vs expenses
- get_monthly_summary: Get complete monthly financial summary

FINANCIAL DATA:
- convert_currency: Convert between currencies using real-time rates
- get_exchange_rate: Get current exchange rate between currencies
- get_stock_price: Get current stock price
- get_stock_quote: Get detailed stock quote

DATE & TIME:
- get_current_date: Get current date and time with full details
- get_today: Get today's date in YYYY-MM-DD format (quick access)

VISUALIZATION:
- generate_chart: Generate a chart for display in chat

DOCUMENTS:
- search_documents: Search user's uploaded documents using semantic search
- list_my_documents: List all uploaded documents
- extract_expenses_from_document: Extract expense data from documents (receipts, invoices)

EMAIL (Gmail Integration - Full CRUD):
READ:
- search_emails: Search Gmail inbox with queries
- get_recent_emails: Get most recent emails
- get_unread_emails: Get unread emails
- get_email_details: Read full email content
- get_banking_emails: Get banking/financial emails
- summarize_emails: AI-powered email summaries
- extract_transactions_from_email: Extract transaction data
- get_email_insights: Aggregated financial insights from emails

WRITE:
- send_email: Send new email via Gmail
- reply_to_email: Reply to an existing email

UPDATE:
- mark_email_as_read: Mark email as read
- archive_email: Archive email (remove from inbox)
- delete_email: Move email to trash

NOTE: There is NO tool to create bank accounts. If user mentions "savings account", 
they likely mean either:
- A savings GOAL (use create_goal)
- Adding money to their balance (use create_income)

IMPORTANT RULES:
1. ALWAYS use the appropriate tool when a user requests financial data or operations
2. When showing spending data, generate a chart using generate_chart tool
3. For currency conversions, use convert_currency with accurate amounts
4. For stock prices, use get_stock_price or get_stock_quote
5. Format responses with markdown for readability
6. Be concise but helpful
7. When creating expenses, confirm the details back to the user
8. NEVER say you don't have access to data - use the tools to get it
9. NEVER add disclaimers about data accuracy - the tools provide real data
10. When asked about balance or expenses, ALWAYS call the appropriate tools
11. If you need today's date, use get_today or get_current_date tool
12. When user says "savings account", they might mean a savings GOAL - clarify if needed
13. Don't ask for information you can infer - use reasonable defaults
14. NEVER say you don't have access to current date - use the get_today tool
15. NEVER show tool call syntax like <|tool_call|> or [tool_name] in your responses
16. NEVER say "continue" or "let's proceed" - just execute the tools immediately
17. When user says "add income", use create_income tool, NOT create_expense
18. When user says "loan", it's an expense (money out) or income (money in) - ask which
19. Execute tools IMMEDIATELY - don't describe what you'll do, just do it
20. After tool execution, provide a clear summary of what was done
21. NEVER create duplicate entries - check if similar entry exists first

Always call tools when needed - don't just describe what you would do.
You have FULL ACCESS to the user's financial data through the tools.

RESPONSE FORMAT:
- Call tools silently (no syntax shown to user)
- After tool execution, provide clear confirmation
- Use natural language, not technical jargon
- Be direct and actionable"""


def get_all_tools() -> List[BaseTool]:
    """Get all available tools for the agent."""
    return [
        # Expense tools
        *expense_tools,
        # Income and balance tools
        *income_tools,
        # Financial data tools
        convert_currency,
        get_exchange_rate,
        get_stock_price,
        get_stock_quote,
        # Date/time tools
        *datetime_tools,
        # Chart tool
        generate_chart,
        # Document tools
        *document_tools,
        # Email tools (if Gmail connected)
        *email_tools,
        # Sandbox MCP tools
        *sandbox_tools,
    ]


def create_agent_graph():
    """
    Create the LangGraph agent graph for MoneyMind.
    
    Graph structure:
    [START] -> [agent] -> [should_continue] -> [tools] -> [agent] -> ...
                                            -> [END]
    """
    from langgraph.prebuilt import create_react_agent
    from src.infrastructure.llm import get_llm
    
    # Get all tools
    tools = get_all_tools()
    
    # Create the graph using StateGraph
    graph = StateGraph(AgentState)
    
    # Add nodes
    graph.add_node("agent", agent_node)
    graph.add_node("tools", ToolNode(tools))
    
    # Set entry point
    graph.set_entry_point("agent")
    
    # Add conditional edges
    graph.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        }
    )
    
    # Tools always go back to agent
    graph.add_edge("tools", "agent")
    
    return graph.compile()


async def agent_node(state: AgentState) -> Dict[str, Any]:
    """
    Agent node - calls LLM to interpret user message and decide on actions.
    
    Implements the LLM node from backend-moneymind.md architecture.
    """
    from src.infrastructure.llm import get_llm
    
    messages = state.get("messages", [])
    
    # Build conversation with system prompt
    full_messages = [{"role": "system", "content": SYSTEM_PROMPT}]
    
    for msg in messages:
        if isinstance(msg, HumanMessage):
            full_messages.append({"role": "user", "content": msg.content})
        elif isinstance(msg, AIMessage):
            if msg.tool_calls:
                full_messages.append({
                    "role": "assistant",
                    "content": msg.content or "",
                    "tool_calls": msg.tool_calls,
                })
            else:
                full_messages.append({"role": "assistant", "content": msg.content})
        elif isinstance(msg, ToolMessage):
            full_messages.append({
                "role": "tool",
                "content": msg.content,
                "tool_call_id": msg.tool_call_id,
            })
    
    try:
        llm = await get_llm()
        
        # Get available tools for tool calling
        tools = get_all_tools()
        tool_schemas = [
            {
                "type": "function",
                "function": {
                    "name": tool.name,
                    "description": tool.description,
                    "parameters": tool.args_schema.schema() if hasattr(tool, 'args_schema') and tool.args_schema else {},
                }
            }
            for tool in tools
        ]
        
        # Call LLM with tool definitions
        response = await llm.chat_with_tools(
            messages=full_messages,
            tools=tool_schemas,
            temperature=0.7,
        )
        
        # Parse response
        if isinstance(response, dict) and "tool_calls" in response:
            # LLM wants to call tools
            ai_message = AIMessage(
                content=response.get("content", ""),
                tool_calls=[
                    {
                        "id": tc.get("id", str(uuid.uuid4())),
                        "name": tc["function"]["name"],
                        "args": json.loads(tc["function"]["arguments"]) if isinstance(tc["function"]["arguments"], str) else tc["function"]["arguments"],
                    }
                    for tc in response["tool_calls"]
                ]
            )
        else:
            # Regular response
            content = response if isinstance(response, str) else response.get("content", str(response))
            ai_message = AIMessage(content=content)
        
        return {"messages": [ai_message]}
        
    except Exception as e:
        # Return error in a helpful way
        error_msg = f"I encountered an issue: {str(e)}. Let me try a different approach."
        return {
            "messages": [AIMessage(content=error_msg)],
            "error": str(e),
        }


def should_continue(state: AgentState) -> Literal["continue", "end"]:
    """
    Determine if we should continue to tools or end.
    
    Checks the last AI message for tool calls.
    """
    messages = state.get("messages", [])
    
    if not messages:
        return "end"
    
    last_message = messages[-1]
    
    # Check if it's an AI message with tool calls
    if isinstance(last_message, AIMessage):
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "continue"
    
    return "end"


async def run_agent(
    user_message: str,
    user_id: str,
    session_id: str,
    user_name: str = None,
    conversation_history: List[Dict] = None,
) -> AsyncIterator[Dict[str, Any]]:
    """
    Run the agent and stream responses.
    
    This implements the chat runtime from backend-moneymind.md Phase 4.
    
    Args:
        user_message: The user's input message
        user_id: User identifier
        session_id: Session identifier
        user_name: Optional user name
        conversation_history: Previous messages in the conversation
    
    Yields:
        Response chunks with type and content
    """
    # Create initial state
    state = create_initial_state(
        user_id=user_id,
        session_id=session_id,
        user_name=user_name,
    )
    
    # Add conversation history if provided
    messages = []
    if conversation_history:
        for msg in conversation_history:
            if msg.get("role") == "user":
                messages.append(HumanMessage(content=msg["content"]))
            elif msg.get("role") == "assistant":
                messages.append(AIMessage(content=msg["content"]))
    
    # Add current user message
    messages.append(HumanMessage(content=user_message))
    state["messages"] = messages
    
    # Create graph
    graph = create_agent_graph()
    
    # Stream thinking status
    yield {"type": "status", "content": "Thinking..."}
    
    try:
        # Run the graph
        final_state = None
        async for event in graph.astream(state):
            final_state = event
            
            # Check for tool executions
            if "tools" in event:
                yield {"type": "status", "content": "Executing tools..."}
            
            # Check for agent responses
            if "agent" in event:
                agent_messages = event["agent"].get("messages", [])
                for msg in agent_messages:
                    if isinstance(msg, AIMessage):
                        if msg.tool_calls:
                            # Notify about tool calls
                            tool_names = [tc.get("name", "unknown") for tc in msg.tool_calls]
                            yield {"type": "status", "content": f"Using tools: {', '.join(tool_names)}"}
                        elif msg.content:
                            # Stream the response content
                            yield {"type": "stream", "content": msg.content}
        
        # Get final AI message
        if final_state:
            final_messages = None
            if "agent" in final_state:
                final_messages = final_state["agent"].get("messages", [])
            elif "messages" in final_state:
                final_messages = final_state["messages"]
            
            if final_messages:
                for msg in reversed(final_messages):
                    if isinstance(msg, AIMessage) and msg.content and not msg.tool_calls:
                        yield {"type": "complete", "content": msg.content}
                        return
        
        yield {"type": "complete", "content": ""}
        
    except Exception as e:
        yield {"type": "error", "content": f"Error: {str(e)}"}


async def run_agent_sync(
    user_message: str,
    user_id: str,
    session_id: str,
) -> str:
    """
    Run the agent synchronously and return the final response.
    
    Useful for non-streaming use cases.
    """
    response_parts = []
    async for chunk in run_agent(user_message, user_id, session_id):
        if chunk["type"] in ["stream", "complete"]:
            if chunk["content"]:
                response_parts.append(chunk["content"])
    
    return "".join(response_parts) if response_parts else "I couldn't process that request."
