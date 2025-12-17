"""
API v1 Router Aggregator.
Combines all v1 route modules into a single router.
"""

from fastapi import APIRouter

from app.api.v1 import users, quizzes, sectors, goals, admin

api_router = APIRouter()

# Include all route modules with their prefixes and tags
api_router.include_router(
    users.router,
    prefix="/users",
    tags=["Users"]
)

api_router.include_router(
    quizzes.router,
    prefix="/quizzes",
    tags=["Quizzes"]
)

api_router.include_router(
    sectors.router,
    prefix="/sectors",
    tags=["Sectors"]
)

api_router.include_router(
    goals.router,
    prefix="/goals",
    tags=["Goals"]
)

api_router.include_router(
    admin.router,
    prefix="/admin",
    tags=["Admin"]
)

