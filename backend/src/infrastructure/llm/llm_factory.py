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
            tool_calls = self._parse_tool_call_from_response(response, tools)
            if tool_calls:
                return {
                    "content": "",
                    "tool_calls": tool_calls,
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
            tool_calls = self._parse_tool_call_from_response(response, tools)
            if tool_calls:
                return {
                    "content": "",
                    "tool_calls": tool_calls,
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
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Parse tool calls from LLM response.
        
        Looks for patterns like:
        - Tool: tool_name(arg1=value1, arg2=value2)
        - I'll use tool_name with {"arg": "value"}
        - <tool_call>{"name": "...", "args": {...}}</tool_call>
        
        Returns a list of tool calls to support multiple intents in one message.
        """
        import re
        
        response_lower = response.lower()
        tool_names = [t["function"]["name"] for t in tools]
        tool_calls = []
        
        # Check for JSON tool call format
        json_pattern = r'\{[^{}]*"name"\s*:\s*"(\w+)"[^{}]*"args"\s*:\s*(\{[^{}]*\})[^{}]*\}'
        json_match = re.search(json_pattern, response)
        if json_match:
            try:
                name = json_match.group(1)
                args = json.loads(json_match.group(2))
                if name in tool_names:
                    return [{
                        "id": f"call_{name}",
                        "function": {
                            "name": name,
                            "arguments": args,
                        }
                    }]
            except:
                pass
        
        # Check for function call pattern: tool_name(args)
        for tool_name in tool_names:
            pattern = rf'{tool_name}\s*\(([^)]*)\)'
            match = re.search(pattern, response, re.IGNORECASE)
            if match:
                args_str = match.group(1)
                args = self._parse_args_string(args_str)
                return [{
                    "id": f"call_{tool_name}",
                    "function": {
                        "name": tool_name,
                        "arguments": args,
                    }
                }]
        
        # Check for intent keywords - support multiple intents
        intent_to_tool = {
            "subscription": "create_subscription",
            "subscribe": "create_subscription",
            "recurring fee": "create_subscription",
            "monthly fee": "create_subscription",
            "bill": "create_bill",
            "payment": "create_bill",
            "due": "create_bill",
            "convert": "convert_currency",
            "exchange": "convert_currency",
            "currency": "convert_currency",
            "stock": "get_stock_price",
            "price of": "get_stock_price",
            "expense": "create_expense",
            "spent": "create_expense",
            "bought": "create_expense",
            "goal": "create_goal",
            "save for": "create_goal",
            "spending": "get_spending_by_category",
            "chart": "generate_chart",
            "balance": "get_balance",
            "how much": "get_balance",
            "income": "create_income",
            "salary": "create_income",
            "earned": "create_income",
        }
        
        # Track which tools we've added to avoid duplicates
        added_tools = set()
        
        # For multi-intent messages (e.g., "subscription AND bill")
        # Split by "and" to process each part separately
        if " and " in response_lower:
            parts = response.split(" and ")
        else:
            parts = [response]
        
        for part in parts:
            part_lower = part.lower()
            for keyword, tool_name in intent_to_tool.items():
                if keyword in part_lower and tool_name in tool_names and tool_name not in added_tools:
                    # Extract potential arguments from context
                    args = self._extract_args_from_context(part, tool_name)
                    if args:
                        tool_calls.append({
                            "id": f"call_{tool_name}_{len(tool_calls)}",
                            "function": {
                                "name": tool_name,
                                "arguments": args,
                            }
                        })
                        added_tools.add(tool_name)
                        break  # Move to next part after finding a match
        
        return tool_calls if tool_calls else None
    
    def _parse_relative_date(self, text: str) -> Optional[str]:
        """Parse relative date expressions to YYYY-MM-DD format."""
        from datetime import date, timedelta
        import re
        
        today = date.today()
        text_lower = text.lower()
        
        # "tomorrow"
        if "tomorrow" in text_lower:
            return (today + timedelta(days=1)).strftime('%Y-%m-%d')
        
        # "next week"
        if "next week" in text_lower:
            return (today + timedelta(weeks=1)).strftime('%Y-%m-%d')
        
        # "in X days" or "X days later" or "X days from now"
        days_match = re.search(r'(\d+)\s*days?\s*(?:later|from now)?', text_lower)
        if days_match:
            days = int(days_match.group(1))
            return (today + timedelta(days=days)).strftime('%Y-%m-%d')
        
        # "in X weeks" or "X weeks later" or "X week later"
        weeks_match = re.search(r'(\d+)\s*weeks?\s*(?:later|from now)?', text_lower)
        if weeks_match:
            weeks = int(weeks_match.group(1))
            return (today + timedelta(weeks=weeks)).strftime('%Y-%m-%d')
        
        # "next month"
        if "next month" in text_lower:
            next_month = today.replace(day=1)
            if today.month == 12:
                next_month = next_month.replace(year=today.year + 1, month=1)
            else:
                next_month = next_month.replace(month=today.month + 1)
            return next_month.strftime('%Y-%m-%d')
        
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
            # Improved expense parsing
            amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:usd|dollars?|\$|฿|thb|eur|€)?', text_lower)
            if not amount_match:
                return None
            
            amount = float(amount_match.group(1))
            
            # Extract currency
            currency = "USD"
            currency_match = re.search(r'(?:usd|dollars?|\$|฿|thb|eur|€)', text_lower)
            if currency_match:
                curr_text = currency_match.group(0)
                if curr_text in ['฿', 'thb']:
                    currency = "THB"
                elif curr_text in ['€', 'eur']:
                    currency = "EUR"
                else:
                    currency = "USD"
            
            # Extract merchant name - look for common patterns
            merchant = "Unknown"
            
            # Pattern 1: "spent $X at MERCHANT"
            at_match = re.search(r'(?:spent|paid|bought).*?(?:at|from)\s+([A-Za-z][A-Za-z0-9\s&\'.-]+?)(?:\s+for|\s+on|\s+in|$)', text, re.IGNORECASE)
            if at_match:
                merchant = at_match.group(1).strip()
            else:
                # Pattern 2: "MERCHANT $X" or "$X MERCHANT"
                # Look for capitalized words near the amount
                words = text.split()
                amount_idx = -1
                for i, word in enumerate(words):
                    if re.search(r'\d+(?:\.\d+)?', word):
                        amount_idx = i
                        break
                
                if amount_idx >= 0:
                    # Check words around the amount
                    for offset in [-2, -1, 1, 2]:
                        idx = amount_idx + offset
                        if 0 <= idx < len(words):
                            word = words[idx]
                            # Skip common words
                            if word.lower() not in ['spent', 'paid', 'bought', 'at', 'for', 'on', 'the', 'a', 'an', 'in', 'to', 'from', '$', '฿', '€']:
                                # Clean the word
                                clean_word = re.sub(r'[^\w\s&\'-]', '', word)
                                if clean_word and len(clean_word) > 1:
                                    merchant = clean_word.title()
                                    break
            
            # Extract category - look for common expense categories
            category = "other"
            category_keywords = {
                "food": ["food", "restaurant", "lunch", "dinner", "breakfast", "meal", "eat", "cafe", "coffee"],
                "transport": ["uber", "taxi", "bus", "train", "gas", "fuel", "parking", "transport"],
                "shopping": ["shopping", "store", "mall", "amazon", "bought", "purchase"],
                "entertainment": ["movie", "cinema", "game", "concert", "show", "entertainment"],
                "bills": ["bill", "utility", "electric", "water", "internet", "phone"],
                "groceries": ["grocery", "groceries", "supermarket", "market"],
                "health": ["doctor", "hospital", "pharmacy", "medicine", "health"],
            }
            
            for cat, keywords in category_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    category = cat
                    break
            
            # Return parsed expense data
            return {
                "amount": amount,
                "merchant": merchant,
                "category": category,
                "currency": currency,
            }
        
        elif tool_name == "create_subscription":
            # Pattern: "$50 gym subscription" or "gym subscription for $50"
            from datetime import date
            
            amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\$|usd|dollars?)?', text_lower)
            if not amount_match:
                # Try with $ before the number
                amount_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', text_lower)
            if not amount_match:
                return None
            
            amount = float(amount_match.group(1))
            
            # Extract name - look for subscription keywords
            name = "Subscription"
            name_patterns = [
                r'(\w+)\s+subscription',  # "gym subscription"
                r'subscribe\s+(?:to\s+)?(\w+)',  # "subscribe to netflix"
                r'(\w+)\s+for\s+\$?\d+',  # "netflix for $15"
            ]
            for pattern in name_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    name = match.group(1).title()
                    break
            
            # Detect billing cycle
            billing_cycle = "monthly"  # default
            if any(w in text_lower for w in ["weekly", "every week", "per week"]):
                billing_cycle = "weekly"
            elif any(w in text_lower for w in ["yearly", "annual", "per year"]):
                billing_cycle = "yearly"
            elif any(w in text_lower for w in ["daily", "every day", "per day"]):
                billing_cycle = "daily"
            
            # Get next billing date
            next_billing_date = self._parse_relative_date(text) or date.today().strftime('%Y-%m-%d')
            
            return {
                "name": name,
                "amount": amount,
                "billing_cycle": billing_cycle,
                "next_billing_date": next_billing_date,
            }
        
        elif tool_name == "create_bill":
            # Pattern: "$40 bill to pay in 1 week" or "electric bill $100"
            from datetime import date
            
            amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\$|usd|dollars?)?', text_lower)
            if not amount_match:
                # Try with $ before the number
                amount_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', text_lower)
            if not amount_match:
                return None
            
            amount = float(amount_match.group(1))
            
            # Extract name
            name = "Bill"
            bill_patterns = [
                r'(\w+)\s+bill',  # "electric bill"
                r'bill\s+(?:for\s+)?(\w+)',  # "bill for rent"
            ]
            for pattern in bill_patterns:
                match = re.search(pattern, text_lower)
                if match:
                    extracted = match.group(1)
                    # Skip common non-name words
                    if extracted not in ['a', 'the', '40', '50', 'my', 'to', 'be', 'and']:
                        name = extracted.title()
                        break
            
            # Get due date
            due_date = self._parse_relative_date(text) or date.today().strftime('%Y-%m-%d')
            
            # Check if recurring
            is_recurring = any(w in text_lower for w in ["recurring", "monthly", "every month", "each month"])
            
            return {
                "name": name,
                "amount": amount,
                "due_date": due_date,
                "is_recurring": is_recurring,
            }
        
        elif tool_name == "create_income":
            # Pattern: "add $5000 salary" or "received $1000 from freelance"
            amount_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:\$|usd|dollars?)?', text_lower)
            if not amount_match:
                amount_match = re.search(r'\$\s*(\d+(?:\.\d+)?)', text_lower)
            if not amount_match:
                return None
            
            amount = float(amount_match.group(1))
            
            # Extract source
            source = "Income"
            source_keywords = {
                "salary": ["salary", "paycheck", "wages"],
                "freelance": ["freelance", "contract", "gig"],
                "investment": ["investment", "dividend", "interest"],
                "bonus": ["bonus"],
                "rental": ["rent", "rental"],
            }
            
            for src, keywords in source_keywords.items():
                if any(kw in text_lower for kw in keywords):
                    source = src.title()
                    break
            
            return {
                "amount": amount,
                "source": source,
            }
        
        # No args extracted for this tool
        return None
    
    def _parse_intent_fallback(
        self,
        messages: List[Dict[str, Any]],
        tools: List[Dict[str, Any]],
    ) -> Dict[str, Any]:
        """Fallback intent parsing when no LLM is available."""
        last_message = messages[-1].get("content", "") if messages else ""
        
        # Parse tool calls from user message
        tool_calls = self._parse_tool_call_from_response(last_message, tools)
        if tool_calls:
            return {
                "content": "",
                "tool_calls": tool_calls,
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
