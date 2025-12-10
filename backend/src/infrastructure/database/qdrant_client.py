"""
Qdrant Vector Database Client
For document embeddings and semantic search
"""
from typing import Optional, List, Dict, Any
from qdrant_client import QdrantClient
from qdrant_client.http.models import (
    Distance,
    VectorParams,
    PointStruct,
    Filter,
    FieldCondition,
    MatchValue,
)

from src.config.settings import settings


class QdrantVectorClient:
    """Qdrant client wrapper for vector operations."""
    
    def __init__(self):
        self._client: Optional[QdrantClient] = None
        self.collection_name = settings.qdrant_collection
        self.vector_size = 384  # Default for sentence-transformers
    
    def connect(self):
        """Initialize Qdrant client."""
        self._client = QdrantClient(url=settings.qdrant_url)
    
    def disconnect(self):
        """Close Qdrant client."""
        if self._client:
            self._client.close()
    
    @property
    def client(self) -> QdrantClient:
        """Get Qdrant client instance."""
        if not self._client:
            raise RuntimeError("Qdrant not connected. Call connect() first.")
        return self._client
    
    def ensure_collection(self, vector_size: int = 384):
        """Create collection if it doesn't exist."""
        collections = self.client.get_collections().collections
        exists = any(c.name == self.collection_name for c in collections)
        
        if not exists:
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(
                    size=vector_size,
                    distance=Distance.COSINE,
                ),
            )
    
    def upsert_vectors(
        self,
        ids: List[str],
        vectors: List[List[float]],
        payloads: List[Dict[str, Any]],
    ):
        """Upsert vectors into collection."""
        points = [
            PointStruct(id=id_, vector=vector, payload=payload)
            for id_, vector, payload in zip(ids, vectors, payloads)
        ]
        self.client.upsert(
            collection_name=self.collection_name,
            points=points,
        )
    
    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        user_id: Optional[str] = None,
        document_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """Search for similar vectors."""
        filter_conditions = []
        
        if user_id:
            filter_conditions.append(
                FieldCondition(key="user_id", match=MatchValue(value=user_id))
            )
        
        if document_id:
            filter_conditions.append(
                FieldCondition(key="document_id", match=MatchValue(value=document_id))
            )
        
        query_filter = Filter(must=filter_conditions) if filter_conditions else None
        
        results = self.client.search(
            collection_name=self.collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=query_filter,
        )
        
        return [
            {
                "id": str(hit.id),
                "score": hit.score,
                "payload": hit.payload,
            }
            for hit in results
        ]
    
    def delete_by_document(self, document_id: str):
        """Delete all vectors for a document."""
        self.client.delete(
            collection_name=self.collection_name,
            points_selector=Filter(
                must=[
                    FieldCondition(
                        key="document_id",
                        match=MatchValue(value=document_id),
                    )
                ]
            ),
        )


# Global Qdrant client instance
qdrant_client = QdrantVectorClient()
