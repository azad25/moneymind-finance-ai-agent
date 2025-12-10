"""
Intent Router Service
Maps user intents to tools using Neo4j knowledge graph
"""
from typing import Optional, List, Dict, Any

from src.infrastructure.database.neo4j_client import neo4j_driver


class IntentRouter:
    """
    Routes user intents to appropriate tools using Neo4j knowledge graph.
    
    This implements the Neo4j Router from README.md/backend-moneymind.md.
    """
    
    def __init__(self):
        self.driver = neo4j_driver
    
    async def initialize_knowledge_graph(self):
        """
        Initialize the knowledge graph with intents, tools, and APIs.
        
        Creates the base structure for intent routing.
        """
        # Create constraints
        self.driver.execute_write("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (i:Intent) REQUIRE i.name IS UNIQUE
        """)
        self.driver.execute_write("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (t:Tool) REQUIRE t.name IS UNIQUE
        """)
        self.driver.execute_write("""
            CREATE CONSTRAINT IF NOT EXISTS FOR (a:API) REQUIRE a.name IS UNIQUE
        """)
        
        # Create intents and tool mappings
        intent_tool_mappings = [
            # Currency conversion
            {
                "intent": "currency_conversion",
                "description": "Convert between currencies",
                "tool": "convert_currency",
                "api": "ExchangeRateAPI",
            },
            {
                "intent": "exchange_rate",
                "description": "Get exchange rate between currencies",
                "tool": "get_exchange_rate",
                "api": "ExchangeRateAPI",
            },
            # Stock prices
            {
                "intent": "stock_price",
                "description": "Get current stock price",
                "tool": "get_stock_price",
                "api": "AlphaVantage",
            },
            {
                "intent": "stock_quote",
                "description": "Get detailed stock quote",
                "tool": "get_stock_quote",
                "api": "AlphaVantage",
            },
            {
                "intent": "crypto_price",
                "description": "Get cryptocurrency price",
                "tool": "get_crypto_price",
                "api": "AlphaVantage",
            },
            # Expense management
            {
                "intent": "create_expense",
                "description": "Create a new expense",
                "tool": "create_expense",
                "api": "PostgreSQL",
            },
            {
                "intent": "list_expenses",
                "description": "List expenses with filters",
                "tool": "list_expenses",
                "api": "PostgreSQL",
            },
            {
                "intent": "spending_by_category",
                "description": "Get spending breakdown by category",
                "tool": "get_spending_by_category",
                "api": "PostgreSQL",
            },
            # Subscriptions
            {
                "intent": "create_subscription",
                "description": "Create a recurring subscription",
                "tool": "create_subscription",
                "api": "PostgreSQL",
            },
            {
                "intent": "list_subscriptions",
                "description": "List active subscriptions",
                "tool": "list_subscriptions",
                "api": "PostgreSQL",
            },
            # Bills
            {
                "intent": "create_bill",
                "description": "Create a bill reminder",
                "tool": "create_bill",
                "api": "PostgreSQL",
            },
            {
                "intent": "list_bills",
                "description": "List upcoming bills",
                "tool": "list_upcoming_bills",
                "api": "PostgreSQL",
            },
            # Goals
            {
                "intent": "create_goal",
                "description": "Create a savings goal",
                "tool": "create_goal",
                "api": "PostgreSQL",
            },
            {
                "intent": "list_goals",
                "description": "List financial goals",
                "tool": "list_goals",
                "api": "PostgreSQL",
            },
            # Charts
            {
                "intent": "generate_chart",
                "description": "Generate a chart visualization",
                "tool": "generate_chart",
                "api": None,
            },
            # Documents
            {
                "intent": "search_documents",
                "description": "Search uploaded documents",
                "tool": "search_documents",
                "api": "Qdrant",
            },
            # Email
            {
                "intent": "search_emails",
                "description": "Search Gmail inbox",
                "tool": "search_emails",
                "api": "Gmail",
            },
            {
                "intent": "banking_emails",
                "description": "Get banking transaction emails",
                "tool": "get_banking_emails",
                "api": "Gmail",
            },
            {
                "intent": "summarize_emails",
                "description": "Summarize selected emails",
                "tool": "summarize_emails",
                "api": "Gmail",
            },
        ]
        
        for mapping in intent_tool_mappings:
            self.driver.execute_write("""
                MERGE (i:Intent {name: $intent})
                SET i.description = $description
                WITH i
                MERGE (t:Tool {name: $tool})
                MERGE (i)-[:USES]->(t)
            """, {
                "intent": mapping["intent"],
                "description": mapping["description"],
                "tool": mapping["tool"],
            })
            
            if mapping.get("api"):
                self.driver.execute_write("""
                    MATCH (t:Tool {name: $tool})
                    MERGE (a:API {name: $api})
                    MERGE (t)-[:CALLS]->(a)
                """, {
                    "tool": mapping["tool"],
                    "api": mapping["api"],
                })
    
    def get_tool_for_intent(self, intent: str) -> Optional[Dict[str, Any]]:
        """
        Get the tool associated with an intent.
        
        Uses Cypher query to find the right tool.
        """
        query = """
        MATCH (i:Intent {name: $intent})-[:USES]->(t:Tool)
        OPTIONAL MATCH (t)-[:CALLS]->(a:API)
        RETURN t.name as tool_name, i.description as description,
               collect(a.name) as apis
        """
        results = self.driver.execute_read(query, {"intent": intent})
        return results[0] if results else None
    
    def classify_intent(self, message: str) -> str:
        """
        Classify user message into an intent.
        
        Uses keyword matching for fast classification.
        Returns the most likely intent.
        """
        message_lower = message.lower()
        
        # Intent patterns
        patterns = {
            "currency_conversion": [
                "convert", "exchange", "to usd", "to eur", "to thb", 
                "how much is", "what is", "in dollars", "in euros"
            ],
            "stock_price": [
                "stock", "price of", "aapl", "googl", "msft", "tsla",
                "share price", "market price"
            ],
            "crypto_price": [
                "bitcoin", "btc", "ethereum", "eth", "crypto", "doge"
            ],
            "create_expense": [
                "spent", "bought", "paid", "add expense", "track expense",
                "expense of", "cost me"
            ],
            "list_expenses": [
                "list expense", "show expense", "my expense", "view expense"
            ],
            "spending_by_category": [
                "spending by", "category", "breakdown", "analyze spending"
            ],
            "create_subscription": [
                "subscribe", "subscription", "recurring", "netflix", "spotify"
            ],
            "list_subscriptions": [
                "my subscription", "list subscription", "show subscription"
            ],
            "create_bill": [
                "bill", "due", "payment due", "remind me to pay"
            ],
            "list_bills": [
                "upcoming bill", "list bill", "what bills", "due soon"
            ],
            "create_goal": [
                "save for", "saving goal", "target", "want to save"
            ],
            "list_goals": [
                "my goal", "progress", "show goal", "list goal"
            ],
            "generate_chart": [
                "chart", "graph", "visualize", "pie chart", "bar chart"
            ],
            "search_documents": [
                "document", "find in", "search my files", "uploaded"
            ],
            "search_emails": [
                "email", "inbox", "search mail", "find email"
            ],
            "banking_emails": [
                "banking email", "bank statement", "transaction email"
            ],
        }
        
        # Find best matching intent
        best_intent = None
        best_score = 0
        
        for intent, keywords in patterns.items():
            score = sum(1 for kw in keywords if kw in message_lower)
            if score > best_score:
                best_score = score
                best_intent = intent
        
        return best_intent or "general_query"
    
    def get_all_intents(self) -> List[Dict[str, Any]]:
        """Get all registered intents with their tools."""
        query = """
        MATCH (i:Intent)
        OPTIONAL MATCH (i)-[:USES]->(t:Tool)
        RETURN i.name as intent, i.description as description,
               collect(t.name) as tools
        ORDER BY i.name
        """
        return self.driver.execute_read(query)


# Global intent router instance
intent_router = IntentRouter()
