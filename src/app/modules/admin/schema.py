"""
Admin API response schemas.
Pydantic models for admin endpoints.
"""

from pydantic import BaseModel
from typing import Optional, List

# Import common response schemas from utils
from src.app.utils.schema import SuccessResponse


# ============================================================
# STATISTICS SCHEMAS
# ============================================================


class AdminStatsResponse(BaseModel):
    """Response schema for database statistics."""

    sectors: int
    active_sectors: int
    branches: int
    active_branches: int
    specializations: int
    active_specializations: int
    quizzes: int
    users: int
    active_users: int
    quiz_attempts: int
    avg_readiness_score: float


# ============================================================
# SECTOR ADMIN SCHEMAS
# ============================================================


class AdminSectorItem(BaseModel):
    """Sector item in admin list response."""

    sector_id: str
    name: str
    description: Optional[str] = None
    is_active: bool
    branch_count: int
    created_at: Optional[str] = None


class AdminSectorCreateResponse(BaseModel):
    """Response schema for creating a sector."""

    success: bool
    sector_id: str
    message: str


# Use SuccessResponse from utils for update/delete operations
AdminSectorUpdateResponse = SuccessResponse
AdminSectorDeleteResponse = SuccessResponse


# ============================================================
# BRANCH ADMIN SCHEMAS
# ============================================================


class AdminBranchItem(BaseModel):
    """Branch item in admin list response."""

    branch_id: str
    name: str
    description: Optional[str] = None
    sector_id: str
    sector_name: Optional[str] = None
    is_active: bool
    specialization_count: int


class AdminBranchCreateResponse(BaseModel):
    """Response schema for creating a branch."""

    success: bool
    branch_id: str
    message: str


# Use SuccessResponse from utils for update/delete operations
AdminBranchUpdateResponse = SuccessResponse
AdminBranchDeleteResponse = SuccessResponse


# ============================================================
# SPECIALIZATION ADMIN SCHEMAS
# ============================================================


class AdminSpecializationItem(BaseModel):
    """Specialization item in admin list response."""

    specialization_id: str
    name: str
    description: Optional[str] = None
    branch_id: str
    branch_name: Optional[str] = None
    sector_name: Optional[str] = None
    is_active: bool
    quiz_count: int


class AdminSpecializationCreateResponse(BaseModel):
    """Response schema for creating a specialization."""

    success: bool
    specialization_id: str
    message: str


# Use SuccessResponse from utils for update/delete operations
AdminSpecializationUpdateResponse = SuccessResponse
AdminSpecializationDeleteResponse = SuccessResponse


# ============================================================
# USER ADMIN SCHEMAS
# ============================================================


class AdminUserItem(BaseModel):
    """User item in admin list response."""

    user_id: str
    name: str
    email: str
    is_active: bool
    readiness_score: Optional[float] = None
    technical_score: Optional[float] = None
    soft_skills_score: Optional[float] = None
    preferred_specialization_id: Optional[str] = None
    specialization_name: Optional[str] = None
    created_at: Optional[str] = None


# Use SuccessResponse from utils for update operations
AdminUserUpdateResponse = SuccessResponse

