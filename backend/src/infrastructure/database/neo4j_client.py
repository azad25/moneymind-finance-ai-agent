"""
Neo4j Knowledge Graph Client
For intent routing and relationship queries
"""
from typing import Optional, List, Dict, Any
from contextlib import contextmanager
from neo4j import GraphDatabase, Driver

from src.config.settings import settings


class Neo4jClient:
    """Neo4j client wrapper for knowledge graph operations."""
    
    def __init__(self):
        self._driver: Optional[Driver] = None
    
    def connect(self):
        """Initialize Neo4j driver."""
        self._driver = GraphDatabase.driver(
            settings.neo4j_uri,
            auth=(settings.neo4j_user, settings.neo4j_password),
        )
    
    def disconnect(self):
        """Close Neo4j driver."""
        if self._driver:
            self._driver.close()
    
    @property
    def driver(self) -> Driver:
        """Get Neo4j driver instance."""
        if not self._driver:
            raise RuntimeError("Neo4j not connected. Call connect() first.")
        return self._driver
    
    def execute_read(self, query: str, parameters: Dict[str, Any] = None) -> List[Dict]:
        """Execute a read query."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return [record.data() for record in result]
    
    def execute_write(self, query: str, parameters: Dict[str, Any] = None) -> Dict:
        """Execute a write query."""
        with self.driver.session() as session:
            result = session.run(query, parameters or {})
            return result.single().data() if result.peek() else {}
    
    # Knowledge graph operations
    def get_tool_for_intent(self, intent: str) -> Optional[Dict]:
        """Get the tool associated with an intent."""
        query = """
        MATCH (i:Intent {name: $intent})-[:USES]->(t:Tool)
        OPTIONAL MATCH (t)-[:CALLS]->(a:API)
        RETURN t.name as tool_name, t.description as tool_description,
               collect(a.name) as apis
        """
        results = self.execute_read(query, {"intent": intent})
        return results[0] if results else None
    
    def get_all_intents(self) -> List[Dict]:
        """Get all registered intents."""
        query = """
        MATCH (i:Intent)
        OPTIONAL MATCH (i)-[:USES]->(t:Tool)
        RETURN i.name as intent, i.description as description,
               collect(t.name) as tools
        """
        return self.execute_read(query)
    
    def add_intent(self, name: str, description: str, tool_name: str):
        """Register a new intent with its tool."""
        query = """
        MERGE (i:Intent {name: $name})
        SET i.description = $description
        WITH i
        MERGE (t:Tool {name: $tool_name})
        MERGE (i)-[:USES]->(t)
        RETURN i, t
        """
        return self.execute_write(query, {
            "name": name,
            "description": description,
            "tool_name": tool_name,
        })
    
    def get_spending_patterns(self, user_id: str) -> List[Dict]:
        """Get user's spending patterns from graph."""
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_EXPENSE]->(e:Expense)-[:CATEGORY]->(c:Category)
        WITH c.name as category, count(e) as count, sum(e.amount) as total
        RETURN category, count, total
        ORDER BY total DESC
        """
        return self.execute_read(query, {"user_id": user_id})
    
    def get_card_recommendations(self, user_id: str) -> List[Dict]:
        """Get card recommendations based on spending patterns."""
        query = """
        MATCH (u:User {id: $user_id})-[:HAS_EXPENSE]->(:Expense)-[:CATEGORY]->(c:Category)
        WITH c, count(*) as spend_count
        ORDER BY spend_count DESC
        LIMIT 3
        MATCH (card:Card)-[:BEST_FOR]->(c)
        RETURN DISTINCT card.name as card_name, card.benefits as benefits,
               collect(c.name) as categories
        """
        return self.execute_read(query, {"user_id": user_id})


# Global Neo4j client instance
neo4j_driver = Neo4jClient()
