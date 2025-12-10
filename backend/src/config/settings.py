"""
MoneyMind Configuration Settings
Pydantic Settings for environment-based configuration
"""
from typing import List, Union
from pydantic_settings import BaseSettings
from pydantic import Field, field_validator


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    app_name: str = "MoneyMind Finance AI Agent"
    app_env: str = Field(default="development", alias="APP_ENV")
    debug: bool = Field(default=True, alias="DEBUG")
    secret_key: str = Field(default="change-me-in-production", alias="SECRET_KEY")
    
    # CORS
    allowed_origins: List[str] = Field(
        default=["http://localhost:3000", "http://127.0.0.1:3000"],
        alias="ALLOWED_ORIGINS"
    )
    
    @field_validator('allowed_origins', mode='before')
    @classmethod
    def parse_allowed_origins(cls, v):
        if isinstance(v, str):
            return [origin.strip() for origin in v.split(',') if origin.strip()]
        return v
    
    # PostgreSQL
    database_url: str = Field(
        default="postgresql+asyncpg://moneymind_user:moneymind_secure_password_2024@localhost:5432/moneymind",
        alias="DATABASE_URL"
    )
    
    # Redis
    redis_url: str = Field(
        default="redis://:moneymind_redis_password_2024@localhost:6379/0",
        alias="REDIS_URL"
    )
    
    # RabbitMQ
    rabbitmq_url: str = Field(
        default="amqp://moneymind_user:moneymind_rabbitmq_password_2024@localhost:5672//",
        alias="RABBITMQ_URL"
    )
    
    # Qdrant
    qdrant_url: str = Field(default="http://localhost:6333", alias="QDRANT_URL")
    qdrant_collection: str = Field(default="moneymind_docs", alias="QDRANT_COLLECTION")
    
    # Neo4j
    neo4j_uri: str = Field(default="bolt://localhost:7687", alias="NEO4J_URI")
    neo4j_user: str = Field(default="neo4j", alias="NEO4J_USER")
    neo4j_password: str = Field(default="moneymind_neo4j_password_2024", alias="NEO4J_PASSWORD")
    
    # JWT Authentication
    jwt_secret: str = Field(default="jwt-secret-change-in-production", alias="JWT_SECRET")
    jwt_algorithm: str = "HS256"
    jwt_expiration_hours: int = 24
    
    # Google OAuth
    google_client_id: str = Field(default="", alias="GOOGLE_CLIENT_ID")
    google_client_secret: str = Field(default="", alias="GOOGLE_CLIENT_SECRET")
    google_redirect_uri: str = Field(
        default="http://localhost:8000/api/auth/google/callback",
        alias="GOOGLE_REDIRECT_URI"
    )
    
    # Stripe
    stripe_secret_key: str = Field(default="", alias="STRIPE_SECRET_KEY")
    stripe_publishable_key: str = Field(default="", alias="STRIPE_PUBLISHABLE_KEY")
    stripe_webhook_secret: str = Field(default="", alias="STRIPE_WEBHOOK_SECRET")
    
    # LLM - Ollama
    ollama_base_url: str = Field(default="http://localhost:11434", alias="OLLAMA_BASE_URL")
    ollama_model: str = Field(default="gemma3:2b", alias="OLLAMA_MODEL")
    
    # LLM - HuggingFace
    huggingface_api_token: str = Field(default="", alias="HUGGINGFACE_API_TOKEN")
    huggingface_model: str = Field(
        default="mistralai/Mistral-7B-Instruct-v0.2",
        alias="HUGGINGFACE_MODEL"
    )
    
    # External APIs
    exchange_rate_api_key: str = Field(default="", alias="EXCHANGE_RATE_API_KEY")
    alpha_vantage_api_key: str = Field(default="", alias="ALPHA_VANTAGE_API_KEY")
    
    # Sandbox MCP
    sandbox_mcp_url: str = Field(default="http://localhost:8001", alias="SANDBOX_MCP_URL")
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"
        case_sensitive = False
        extra = "ignore"


# Global settings instance
settings = Settings()
