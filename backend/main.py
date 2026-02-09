from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from backend.config import settings
from backend.api.v1 import api_v1_router
from backend.models import HealthResponse, ErrorResponse


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application lifespan handler.
    
    Startup: Initialize services (vector store, LLM connection)
    Shutdown: Clean up resources
    """
    # === STARTUP ===
    print(f"Starting {settings.app_name} v{settings.app_version}")
    print(f"Debug mode: {settings.debug}")
    print(f"API prefix: {settings.api_prefix}")
    
    # TODO: Initialize ChromaDB connection
    # TODO: Initialize Ollama connection
    # TODO: Verify data directories exist
    
    for dir_path in [
        settings.documents_dir,
        settings.chats_dir,
        settings.kiro_dir,
        settings.invoices_dir,
        settings.vectordb_dir,
    ]:
        dir_path.mkdir(parents=True, exist_ok=True)
        print(f"Ensured directory exists: {dir_path}")
    
    yield
    
    # === SHUTDOWN ===
    print("Shutting down application...")
    # TODO: Clean up connections


# Create FastAPI application
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    Personal Documentation Agent API
    
    A local-first agentic system for managing and querying personal documents:
    - General documents (PDF, DOCX, TXT, MD)
    - AI chat histories (Claude, Copilot, Gemini, Perplexity)
    - Kiro IDE logs
    - Car maintenance invoices
    """,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Handle unexpected exceptions."""
    return JSONResponse(
        status_code=500,
        content=ErrorResponse(
            error="Internal server error",
            detail=str(exc) if settings.debug else None,
            timestamp=datetime.now(timezone.utc)
        ).model_dump(mode="json")
    )


# Health check endpoint (root level)
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["Health"]
)
async def health_check():
    """
    Health check endpoint.
    
    Returns service status and version information.
    """
    # TODO: Check actual service connectivity
    
    return HealthResponse(
        status="healthy",
        version=settings.app_version,
        timestamp=datetime.now(timezone.utc),
        services={
            "api": "healthy",
            "vectorstore": "not_checked",  # TODO
            "llm": "not_checked",  # TODO
        }
    )


# Root endpoint
@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with API information."""
    return {
        "name": settings.app_name,
        "version": settings.app_version,
        "docs": "/docs",
        "health": "/health",
        "api": settings.api_prefix,
    }


# Include API v1 router
app.include_router(
    api_v1_router,
    prefix=settings.api_prefix
)