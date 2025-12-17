"""
Future Work Readiness API
Main FastAPI application entry point
"""

import logging
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware

# Import core configuration and database
from app.core.config import settings
from app.core.database import engine, Base

# Import versioned API router
from app.api.v1 import api_router

# Configure logging
logging.basicConfig(
    level=logging.INFO if settings.DEBUG else logging.WARNING,
    format="%(asctime)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)


def create_application() -> FastAPI:
    """
    Application factory function.
    Creates and configures the FastAPI application.
    """
    application = FastAPI(
        title=settings.PROJECT_NAME,
        description=settings.DESCRIPTION,
        version=settings.VERSION,
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        docs_url="/docs",
        redoc_url="/redoc",
    )

    # CORS Middleware - Allow frontend to communicate with backend
    application.add_middleware(
        CORSMiddleware,
        allow_origins=settings.CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include v1 API router
    application.include_router(api_router, prefix=settings.API_V1_PREFIX)

    return application


# Create the application instance
app = create_application()


@app.on_event("startup")
async def startup_event():
    """
    Runs on application startup.
    Creates database tables if they don't exist and seeds initial data.
    """
    logger.info(f"Starting {settings.PROJECT_NAME} v{settings.VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")
    logger.info(f"API available at: {settings.API_V1_PREFIX}")

    # Import all models to register them with Base
    from app.models import (
        Sector,
        Branch,
        Specialization,
        Quiz,
        Question,
        QuestionOption,
        QuizAttempt,
        User,
        PeerBenchmark,
        Badge,
        UserBadge,
        Goal,
        JournalEntry,
    )

    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created/verified")

    # Auto-seed database if empty
    from app.seeds.base import auto_seed_if_empty

    auto_seed_if_empty()


@app.on_event("shutdown")
async def shutdown_event():
    """
    Runs on application shutdown.
    """
    logger.info("Application shutting down")


# Root endpoints
@app.get("/", tags=["Root"])
def root():
    """
    Root endpoint - Welcome message
    """
    return {
        "message": f"Welcome to {settings.PROJECT_NAME}",
        "version": settings.VERSION,
        "api": settings.API_V1_PREFIX,
        "docs": "/docs",
        "redoc": "/redoc",
    }


@app.get("/health", tags=["Health"])
def health_check():
    """
    Health check endpoint for container orchestration
    """
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "environment": settings.ENVIRONMENT,
    }


@app.get("/welcome", tags=["Root"])
def welcome(request: Request):
    """
    Welcome endpoint that logs requests and returns a welcome message
    """
    logger.info(f"Request received: {request.method} {request.url.path}")
    return {"message": f"Welcome to the {settings.PROJECT_NAME}"}
