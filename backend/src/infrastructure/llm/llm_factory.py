"""
LLM Factory - REAL IMPLEMENTATION
Abstraction layer with actual tool calling support
"""
from typing import Optional, AsyncIterator, List, Dict, Any
from enum import Enum
import json

from src.config.settings import settings
from .ollama_client import OllamaClient, ollama_client
from .huggingface_client import HuggingFaceClient, huggingface_client


class LLMProvider(str, Enum):
    """Available LLM providers."""
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    AUTO = "auto"


class LLMFactory:
    """Factory for creating and managing LLM clients with tool support."""
    
    def __init__(self):
        self._ollama = ollama_client
        self._huggingface = huggingface_client
        self._active_provider: Optional[LLMProvider] = None
        self._initialized = False
    
    async def initialize(self):
        """Initialize and detect available providers."""
        if self._initialized:
            return
        
        # Check Ollama first (preferred for local inference)
        if await self._ollama.is_available():
            self._active_provider = LLMProvider.OLLAMA
            print("✅ Using Ollama for LLM inference")
        elif await self._huggingface.is_available():
            self._active_provider = LLMProvider.HUGGINGFACE
            print("✅ Using HuggingFace for LLM inference")
        else:
            print("⚠️ No LLM provider available - using fallback responses")
        
        self._initialized = True
    
    async def close(self):
        """Close all clients."""
        await self._ollama.close()
        await self._huggingface.close()
    
    @property
    def provider(self) -> Optional[LLMProvider]:
        """Get active provider."""
        return self._active_provider
    
    @property
    def is_available(self) -> bool:
        """Check if any LLM is available."""
        return self._active_provider is not None
    
    async def chat(
        self,
        messages: List[Dict[str, str]],
        provider: LLMProvider = LLMProvider.AUTO,
        temperature: float = 0.7,
    ) -> str:
        """Chat completion using available provider."""
        if not self._initialized:
            await self.initialize()
        
        if provider == LLMProvider.AUTO:
            provider = self._active_provider
        
        if provider == LLMProvider.OLLAMA:
            return await self._ollama.chat(
                messages=messages,
                temperature=temperature,
            )
        elif provider == LLMProvider.HUGGINGFACE:
            return await self._huggingface.chat(
                messages=messages,
                temperature=temperature,
            )
        else:
            # Fallback: simple response based on last message
            return self._generate_fallback_response(messages)
    
    async def chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float = 0.7,
    ) -> Dict[str, Any]:
        """
        Chat completion with tool calling support.
        
        Returns either a content response or tool calls.
        """
        if not self._initialized:
            await self.initialize()
        
        provider = self._active_provider
        
        if provider == LLMProvider.OLLAMA:
            return await self._ollama_chat_with_tools(messages, tools, temperature)
        elif provider == LLMProvider.HUGGINGFACE:
            return await self._huggingface_chat_with_tools(messages, tools, temperature)
        else:
            # Fallback: parse intent and generate tool call
            return self._parse_intent_fallback(messages, tools)
    
    async def _ollama_chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float,
    ) -> Dict[str, Any]:
        """Ollama chat with tool calling."""
        try:
            # Format messages for Ollama
            formatted_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                
                if role == "tool":
                    # Convert tool results to assistant context
                    formatted_messages.append({
                        "role": "user",
                        "content": f"Tool result: {content}"
                    })
                else:
                    formatted_messages.append({
                        "role": role,
                        "content": content
                    })
            
            # Add tool descriptions to system prompt
            tool_desc = self._format_tool_descriptions(tools)
            if formatted_messages and formatted_messages[0]["role"] == "system":
                formatted_messages[0]["content"] += f"\n\nAvailable tools:\n{tool_desc}"
            
            # Get response
            response = await self._ollama.chat(
                messages=formatted_messages,
                temperature=temperature,
            )
            
            # Try to parse tool calls from response
            tool_call = self._parse_tool_call_from_response(response, tools)
            if tool_call:
                return {
                    "content": "",
                    "tool_calls": [tool_call],
                }
            
            return {"content": response}
            
        except Exception as e:
            return {"content": f"Error: {str(e)}"}
    
    async def _huggingface_chat_with_tools(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
        temperature: float,
    ) -> Dict[str, Any]:
        """HuggingFace chat with tool calling."""
        try:
            # Format for HuggingFace
            formatted_messages = []
            for msg in messages:
                role = msg.get("role", "user")
                content = msg.get("content", "")
                formatted_messages.append({"role": role, "content": content})
            
            # Add tool descriptions
            tool_desc = self._format_tool_descriptions(tools)
            if formatted_messages and formatted_messages[0]["role"] == "system":
                formatted_messages[0]["content"] += f"\n\nYou have these tools:\n{tool_desc}"
            
            response = await self._huggingface.chat(
                messages=formatted_messages,
                temperature=temperature,
            )
            
            # Parse tool calls
            tool_call = self._parse_tool_call_from_response(response, tools)
            if tool_call:
                return {
                    "content": "",
                    "tool_calls": [tool_call],
                }
            
            return {"content": response}
            
        except Exception as e:
            return {"content": f"Error: {str(e)}"}
    
    def _format_tool_descriptions(self, tools: List[Dict[str, Any]]) -> str:
        """Format tool descriptions for prompt injection."""
        lines = []
        for tool in tools:
            func = tool.get("function", {})
            name = func.get("name", "unknown")
            desc = func.get("description", "")
            params = func.get("parameters", {})
            
            param_str = ", ".join(params.get("properties", {}).keys())
            lines.append(f"- {name}({param_str}): {desc[:100]}")
        
        return "\n".join(lines[:15])  # Limit to 15 tools in prompt
    
    def _parse_tool_call_from_response(
        self,
        response: str,
        tools: List[Dict[str, Any]],
    ) -> Optional[Dict[str, Any]]:
        """
        Parse tool calls from LLM response.
        
        Looks for patterns like:
        - Tool: tool_name(arg1=value1, arg2=value2)
        - I'll use tool_name with {"arg": "value"}
        - <tool_call>{"name": "...", "args": {...}}</tool_call>
        """
        import re
        
        response_lower = response.lower()
        tool_names = [t["function"]["name"] for t in tools]
        
        # Check for JSON tool call format
        json_pattern = r'\{[^{}]*"name"\s*:\s*"(\w+)"[^{}]*"args"\s*:\s*(\{[^{}]*\})[^{}]*\}'
        json_match = re.search(json_pattern, response)
        if json_match:
            try:
                name = json_match.group(1)
                args = json.loads(json_match.group(2))
                if name in tool_names:
                    return {
                        "id": f"call_{name}",
                        "function": {
                            "name": name,
                            "arguments": args,
                        }
                    }
            except:
                pass
        
        # Check for function call pattern: tool_name(args)
        for tool_name in tool_names:
            pattern = rf'{tool_name}\s*\(([^)]*)\)'
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                args_str = match.group(1)
                args = self._parse_args_string(args_str)
                return {
                    "id": f"call_{tool_name}",
                    "function": {
                        "name": tool_name,
                        "arguments": args,
                    }
                }
        
        # Check for intent keywords
        intent_to_tool = {
            "convert": "convert_currency",
            "exchange": "convert_currency",
            "currency": "convert_currency",
            "stock": "get_stock_price",
            "price of": "get_stock_price",
            "expense": "create_expense",
            "spent": "create_expense",
            "bought": "create_expense",
            "paid": "create_expense",
            "subscription": "create_subscription",
            "bill": "create_bill",
            "goal": "create_goal",
            "spending": "get_spending_by_category",
            "chart": "generate_chart",
        }
        
        for keyword, tool_name in intent_to_tool.items():
            if keyword in response_lower and tool_name in tool_names:
                # Extract potential arguments from context
                args = self._extract_args_from_context(response, tool_name)
                if args:
                    return {
                        "id": f"call_{tool_name}",
                        "function": {
                            "name": tool_name,
                            "arguments": args,
                        }
                    }
        
        return None
    
    def _parse_args_string(self, args_str: str) -> Dict[str, Any]:
        """Parse arguments from string like 'arg1=value1, arg2=value2'."""
        args = {}
        for part in args_str.split(","):
            if "=" in part:
                key, value = part.split("=", 1)
                key = key.strip()
                value = value.strip().strip('"\'')
                try:
                    args[key] = float(value)
                except ValueError:
                    args[key] = value
        return args
    
    def _extract_args_from_context(self, text: str, tool_name: str) -> Optional[Dict[str, Any]]:
        """Extract arguments from natural language context."""
        import re
        
        text_lower = text.lower()
        
        if tool_name == "convert_currency":
            # Look for patterns like "100 USD to EUR"
            pattern = r'(\d+(?:\.\d+)?)\s*([a-zA-Z]{3})\s*(?:to|into)\s*([a-zA-Z]{3})'
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                return {
                    "amount": float(match.group(1)),
                    "from_currency": match.group(2).upper(),
                    "to_currency": match.group(3).upper(),
                }
        
        elif tool_name == "get_stock_price":
            # Look for stock symbols
            symbols = re.findall(r'\b([A-Z]{1,5})\b', text.upper())
            common_stocks = ["AAPL", "GOOGL", "MSFT", "TSLA", "AMZN", "META", "NVDA", "AMD"]
            for sym in symbols:
                if sym in common_stocks:
                    return {"symbol": sym}
        
        elif tool_name == "create_expense":
            # Look for amount and merchant
            amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:usd|thb|eur|\$|฿)?', text_lower)
            if amount_match:
                amount = float(amount_match.group(1))
                # Try to find merchant
                words = text.split()
                merchant = "Unknown"
                for word in words:
                    if word[0].isupper() and word.lower() not in ["i", "the", "a"]:
                        merchant = word
                        break
                return {
                    "amount": amount,
                    "merchant": merchant,
                    "category": "general",
                }
        
        return None
    
    def _parse_intent_fallback(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Fallback intent parsing when no LLM is available."""
        last_message = messages[-1].get("content", "") if messages else ""
        
        # Parse tool call from user message
        tool_call = self._parse_tool_call_from_response(last_message, tools)
        if tool_call:
            return {
                "content": "",
                "tool_calls": [tool_call],
            }
        
        return {
            "content": "I understand you want to manage your finances. Please make sure an LLM (Ollama or HuggingFace) is configured for full functionality."
        }
    
    def _generate_fallback_response(self, messages: List[Dict[str, str]]) -> str:
        """Generate simple fallback response."""
        return "I'm MoneyMind, your finance assistant. Please configure Ollama or HuggingFace API for full functionality."


# Global LLM factory instance
llm_factory = LLMFactory()


async def get_llm() -> LLMFactory:
    """Get the LLM factory instance."""
    if not llm_factory._initialized:
        await llm_factory.initialize()
    return llm_factory
