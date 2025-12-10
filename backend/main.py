"""
MoneyMind Finance AI Agent - FastAPI Backend
Main application entry point with real database initialization
"""
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import logging

from src.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO if not settings.debug else logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan handler for startup/shutdown events."""
    # Startup
    logger.info("🚀 Starting MoneyMind Backend...")
    
    # Initialize database connections
    try:
        from src.infrastructure.database.postgres import init_db
        await init_db()
        logger.info("✅ PostgreSQL database initialized")
    except Exception as e:
        logger.warning(f"⚠️ PostgreSQL not available: {e}")
    
    # Initialize Redis
    try:
        from src.infrastructure.database.redis_client import redis_client
        await redis_client.connect()
        logger.info("✅ Redis connected")
    except Exception as e:
        logger.warning(f"⚠️ Redis not available: {e}")
    
    # Initialize Qdrant
    try:
        from src.infrastructure.database.qdrant_client import qdrant_client
        qdrant_client.connect()
        qdrant_client.ensure_collection()
        logger.info("✅ Qdrant vector database connected")
    except Exception as e:
        logger.warning(f"⚠️ Qdrant not available: {e}")
    
    # Initialize Neo4j
    try:
        from src.infrastructure.database.neo4j_client import neo4j_driver
        neo4j_driver.connect()
        logger.info("✅ Neo4j knowledge graph connected")
    except Exception as e:
        logger.warning(f"⚠️ Neo4j not available: {e}")
    
    # Initialize LLM
    try:
        from src.infrastructure.llm import get_llm
        llm = await get_llm()
        if llm.is_available:
            logger.info(f"✅ LLM ready ({llm.provider.value})")
        else:
            logger.warning("⚠️ No LLM provider available")
    except Exception as e:
        logger.warning(f"⚠️ LLM initialization failed: {e}")
    
    logger.info("🎉 MoneyMind Backend started successfully!")
    
    yield
    
    # Shutdown
    logger.info("👋 Shutting down MoneyMind Backend...")
    
    try:
        from src.infrastructure.database.postgres import close_db
        await close_db()
    except:
        pass
    
    try:
        from src.infrastructure.database.redis_client import redis_client
        await redis_client.disconnect()
    except:
        pass
    
    try:
        from src.infrastructure.database.qdrant_client import qdrant_client
        qdrant_client.disconnect()
    except:
        pass
    
    try:
        from src.infrastructure.database.neo4j_client import neo4j_driver
        neo4j_driver.disconnect()
    except:
        pass
    
    logger.info("✅ Cleanup complete")


app = FastAPI(
    title="MoneyMind Finance AI Agent",
    description="AI-powered personal finance assistant with natural language interface",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for WebSocket compatibility
    allow_credentials=False,  # Must be False when allow_origins is ["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    """Global exception handler for unhandled errors."""
    logger.error(f"Unhandled error: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)},
    )


# Import and include routers
from src.interfaces.api.routes import auth, health, chat, documents, payments, gmail, expenses

app.include_router(health.router, tags=["Health"])
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(chat.router, prefix="/ws", tags=["Chat"])
app.include_router(documents.router, prefix="/api/documents", tags=["Documents"])
app.include_router(payments.router, prefix="/api/payments", tags=["Payments"])
app.include_router(gmail.router, prefix="/api/gmail", tags=["Gmail"])
app.include_router(expenses.router, prefix="/api/expenses", tags=["Expenses"])


@app.get("/")
async def root():
    """Root endpoint - API info."""
    return {
        "name": "MoneyMind Finance AI Agent",
        "version": "1.0.0",
        "status": "running",
        "docs": "/docs",
        "websocket": "/ws/chat",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        workers=1 if settings.debug else 4,
    )
