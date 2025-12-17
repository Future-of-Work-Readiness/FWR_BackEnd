"""
Goal and JournalEntry schemas.
Pydantic models for user goals and journal.
"""

from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime
from uuid import UUID

# Import common response schemas from utils
from src.app.utils.schema import SuccessResponse


# Goal schemas
class GoalBase(BaseModel):
    """Base schema for Goal data."""

    title: str
    description: Optional[str] = None
    category: str  # 'readiness', 'technical', 'soft_skills', 'leadership'
    target_value: float
    target_date: Optional[datetime] = None


class GoalCreate(GoalBase):
    """Schema for creating a new Goal."""

    pass


class Goal(GoalBase):
    """Schema for Goal response."""

    goal_id: UUID
    user_id: UUID
    current_value: float
    is_completed: bool
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


# Journal Entry schemas
class JournalEntryBase(BaseModel):
    """Base schema for JournalEntry data."""

    content: str
    prompt: Optional[str] = None


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a new JournalEntry."""

    pass


class JournalEntry(JournalEntryBase):
    """Schema for JournalEntry response."""

    entry_id: UUID
    user_id: UUID
    entry_date: datetime
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True


class JournalEntryUpdate(BaseModel):
    """Schema for updating a JournalEntry."""

    content: str


# ============================================================
# ENDPOINT RESPONSE SCHEMAS
# ============================================================


class GoalResponse(BaseModel):
    """Response schema for a single goal."""

    goal_id: str
    user_id: str
    title: str
    description: Optional[str] = None
    category: str
    target_value: float
    current_value: float
    is_completed: bool
    target_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


class GoalProgressResponse(BaseModel):
    """Response schema for goal progress update."""

    goal_id: str
    user_id: str
    title: str
    current_value: float
    target_value: float
    is_completed: bool


# Use SuccessResponse from utils for delete operations
GoalDeleteResponse = SuccessResponse


class JournalEntryResponse(BaseModel):
    """Response schema for a single journal entry."""

    entry_id: str
    user_id: str
    content: str
    prompt: Optional[str] = None
    entry_date: Optional[str] = None
    created_at: Optional[str] = None
    updated_at: Optional[str] = None


# Use SuccessResponse from utils for delete operations
JournalEntryDeleteResponse = SuccessResponse

