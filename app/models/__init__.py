"""
Database Models Package
All SQLAlchemy models are defined here and exported for use throughout the application.

Usage:
    from app.models import User, Quiz, Sector, etc.
"""

# Import Base from core for model definitions
from app.core.database import Base

# Import all models for easy access
from app.models.sector import Sector, Branch, Specialization
from app.models.quiz import Quiz, Question, QuestionOption, QuizAttempt
from app.models.user import User
from app.models.benchmark import PeerBenchmark
from app.models.badge import Badge, UserBadge
from app.models.goal import Goal, JournalEntry

# Export all models
__all__ = [
    "Base",
    # Sector hierarchy
    "Sector",
    "Branch", 
    "Specialization",
    # Quiz system
    "Quiz",
    "Question",
    "QuestionOption",
    "QuizAttempt",
    # User
    "User",
    # Benchmarking
    "PeerBenchmark",
    # Badges
    "Badge",
    "UserBadge",
    # Goals & Journal
    "Goal",
    "JournalEntry",
]

