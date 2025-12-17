"""
Pydantic Schemas Package
All request/response schemas are defined here and exported for use throughout the application.

Usage:
    from app.schemas import User, UserCreate, Quiz, Sector, Branch, Specialization, etc.
"""

# Import all schemas for easy access
from app.schemas.sector import (
    # Sector schemas
    SectorBase, SectorCreate, Sector, SectorsResponse,
    # Branch schemas
    BranchBase, BranchCreate, Branch, BranchesResponse,
    # Specialization schemas
    SpecializationBase, SpecializationCreate, Specialization, SpecializationsResponse,
    # Hierarchy schemas
    SpecializationInBranch, BranchWithSpecializations, SectorWithBranches, HierarchyResponse,
)
from app.schemas.user import (
    UserBase, UserCreate, UserLogin, User, UserUpdate, UserResponse, LoginResponse,
)
from app.schemas.quiz import (
    AnswerOptionBase, AnswerOption,
    QuestionBase, Question, QuestionResult,
    QuizBase, Quiz, QuizSummary, QuizzesResponse,
    QuizAnswer, AnswerSubmit, QuizSubmission,
    QuizAttemptBase, QuizAttempt,
    QuizResult, QuizResultExtended,
    QuizStartResponse,
    # Also export these from quiz.py (inline definitions)
    ReadinessSnapshot, FeedbackDetail, ScoreImpact,
)
from app.schemas.goal import (
    GoalBase, GoalCreate, Goal,
    JournalEntryBase, JournalEntryCreate, JournalEntry, JournalEntryUpdate,
)
from app.schemas.benchmark import (
    PeerComparison, CommonInsight, PeerBenchmarkData, PeerBenchmarkResponse,
)
from app.schemas.common import (
    RecentAttempt, DashboardResponse,
)

# Export all schemas
__all__ = [
    # Sector schemas
    "SectorBase", "SectorCreate", "Sector", "SectorsResponse",
    # Branch schemas
    "BranchBase", "BranchCreate", "Branch", "BranchesResponse",
    # Specialization schemas
    "SpecializationBase", "SpecializationCreate", "Specialization", "SpecializationsResponse",
    # Hierarchy schemas
    "SpecializationInBranch", "BranchWithSpecializations", "SectorWithBranches", "HierarchyResponse",
    # User schemas
    "UserBase", "UserCreate", "UserLogin", "User", "UserUpdate", "UserResponse", "LoginResponse",
    # Quiz schemas
    "AnswerOptionBase", "AnswerOption",
    "QuestionBase", "Question", "QuestionResult",
    "QuizBase", "Quiz", "QuizSummary", "QuizzesResponse",
    "QuizAnswer", "AnswerSubmit", "QuizSubmission",
    "QuizAttemptBase", "QuizAttempt",
    "QuizResult", "QuizResultExtended",
    "QuizStartResponse",
    # Goal schemas
    "GoalBase", "GoalCreate", "Goal",
    "JournalEntryBase", "JournalEntryCreate", "JournalEntry", "JournalEntryUpdate",
    # Benchmark schemas
    "PeerComparison", "CommonInsight", "PeerBenchmarkData", "PeerBenchmarkResponse",
    # Common schemas
    "ReadinessSnapshot", "FeedbackDetail", "ScoreImpact",
    "RecentAttempt", "DashboardResponse",
]
