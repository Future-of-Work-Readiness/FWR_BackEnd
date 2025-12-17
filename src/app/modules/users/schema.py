"""
User schemas.
Pydantic models for user authentication and profile.
"""

from pydantic import BaseModel
from typing import Optional, List, Any
from datetime import datetime
from uuid import UUID

from src.app.utils.tokens import Tokens


class UserBase(BaseModel):
    """Base schema for User data."""

    email: str
    name: str


class UserCreate(UserBase):
    """Schema for user registration."""

    password: str


class UserLogin(BaseModel):
    """Schema for user login."""

    email: str
    password: str


class User(UserBase):
    """Schema for User response."""

    user_id: UUID
    preferred_specialization_id: Optional[UUID] = None
    readiness_score: Optional[float] = None
    technical_score: Optional[float] = None
    soft_skills_score: Optional[float] = None
    leadership_score: Optional[float] = None
    created_at: datetime

    class Config:
        from_attributes = True


class UserUpdate(BaseModel):
    """Schema for updating user profile."""

    preferred_specialization_id: Optional[UUID] = None


# ============================================================
# RESPONSE SCHEMAS
# ============================================================


class UserDataResponse(BaseModel):
    """User data in responses (with string IDs for JSON compatibility)."""

    user_id: str
    email: str
    name: str
    preferred_specialization_id: Optional[str] = None
    readiness_score: Optional[float] = None
    technical_score: Optional[float] = None
    soft_skills_score: Optional[float] = None
    leadership_score: Optional[float] = None
    created_at: str


class UserResponse(BaseModel):
    """Response schema for user operations (register)."""

    success: bool
    message: str
    user: UserDataResponse


class LoginResponse(BaseModel):
    """Response schema for login with JWT tokens."""

    success: bool
    message: str
    user: UserDataResponse
    tokens: Tokens


class UserSpecializationUpdateResponse(BaseModel):
    """Response schema for specialization update."""

    success: bool
    user: dict


class UserProfileResponse(BaseModel):
    """Response schema for GET user profile."""

    user_id: str
    email: str
    name: str
    preferred_specialization_id: Optional[str] = None
    readiness_score: Optional[float] = None
    technical_score: Optional[float] = None
    soft_skills_score: Optional[float] = None
    leadership_score: Optional[float] = None
    created_at: datetime


# Peer Benchmark Response Schemas
class PeerComparison(BaseModel):
    """Comparison of user score vs peer average."""

    category: str
    your_score: float
    peer_average: float
    difference: float
    percentile: int
    status: str


class CommonInsight(BaseModel):
    """Common strength or gap insight."""

    area: str
    percentage: float
    description: str


class PeerBenchmarkData(BaseModel):
    """Peer benchmark data."""

    specialization_name: str
    total_peers: int
    comparisons: List[PeerComparison]
    overall_percentile: int
    common_strengths: List[CommonInsight]
    common_gaps: List[CommonInsight]
    last_updated: str


class PeerBenchmarkResponse(BaseModel):
    """Response schema for peer benchmark endpoint."""

    success: bool
    data: PeerBenchmarkData


# Dashboard Response Schemas
class QuizHistoryItem(BaseModel):
    """Quiz attempt history item."""

    quiz_id: str
    quiz_title: str
    score: float
    passed: bool
    completed_at: str


class ActiveGoalItem(BaseModel):
    """Active goal item."""

    goal_id: str
    title: str
    category: str
    target_value: float
    current_value: float
    progress_percentage: float


class ReadinessScores(BaseModel):
    """User readiness scores."""

    overall: float
    technical: float
    soft_skills: float
    leadership: float


class DashboardSummary(BaseModel):
    """Dashboard summary response schema."""

    user_id: str
    name: str
    email: str
    specialization_name: Optional[str] = None
    readiness_scores: ReadinessScores
    quiz_stats: dict
    recent_quizzes: List[QuizHistoryItem]
    active_goals: List[ActiveGoalItem]
    last_activity: Optional[str] = None
