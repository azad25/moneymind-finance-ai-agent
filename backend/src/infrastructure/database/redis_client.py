"""
Redis Client
Connection pool and pub/sub messaging
"""
from typing import Optional
import redis.asyncio as redis
from redis.asyncio import Redis

from src.config.settings import settings


class RedisClient:
    """Redis client wrapper with connection pool."""
    
    def __init__(self):
        self._pool: Optional[redis.ConnectionPool] = None
        self._client: Optional[Redis] = None
    
    async def connect(self):
        """Initialize Redis connection pool."""
        self._pool = redis.ConnectionPool.from_url(
            settings.redis_url,
            max_connections=20,
            decode_responses=True,
        )
        self._client = redis.Redis(connection_pool=self._pool)
    
    async def disconnect(self):
        """Close Redis connections."""
        if self._client:
            await self._client.close()
        if self._pool:
            await self._pool.disconnect()
    
    @property
    def client(self) -> Redis:
        """Get Redis client instance."""
        if not self._client:
            raise RuntimeError("Redis not connected. Call connect() first.")
        return self._client
    
    # Cache operations
    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.client.get(key)
    
    async def set(self, key: str, value: str, expire: int = 3600):
        """Set value in cache with expiration."""
        await self.client.set(key, value, ex=expire)
    
    async def delete(self, key: str):
        """Delete key from cache."""
        await self.client.delete(key)
    
    # Session operations
    async def get_session(self, session_id: str) -> Optional[dict]:
        """Get session data."""
        data = await self.client.hgetall(f"session:{session_id}")
        return data if data else None
    
    async def set_session(self, session_id: str, data: dict, expire: int = 86400):
        """Store session data."""
        key = f"session:{session_id}"
        await self.client.hset(key, mapping=data)
        await self.client.expire(key, expire)
    
    async def delete_session(self, session_id: str):
        """Delete session."""
        await self.client.delete(f"session:{session_id}")
    
    # Pub/Sub operations
    async def publish(self, channel: str, message: str):
        """Publish message to channel."""
        await self.client.publish(channel, message)
    
    def subscribe(self, channel: str):
        """Subscribe to channel."""
        pubsub = self.client.pubsub()
        return pubsub


# Global Redis client instance
redis_client = RedisClient()
