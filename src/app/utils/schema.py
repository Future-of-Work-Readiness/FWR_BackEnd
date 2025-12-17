"""
Common/shared schemas for API responses.
Pydantic models used across multiple modules.
"""

from enum import Enum
from typing import Any, Generic, List, Optional, TypeVar
from uuid import UUID

from pydantic import BaseModel, constr


# ============================================================
# GENERIC RESPONSE SCHEMAS
# ============================================================


class SuccessResponse(BaseModel):
    """Standard success response schema."""

    message: str = "Success"
    success: bool = True
    data: Optional[dict] = None


class ErrorResponse(BaseModel):
    """Standard error response schema."""

    message: str
    success: bool = False
    error_code: Optional[str] = None
    details: Optional[dict] = None


# Generic type for paginated data
T = TypeVar("T")


class PaginatedResponse(BaseModel, Generic[T]):
    """Generic paginated response schema."""

    data: List[T]
    pagination: "Pagination"


class Pagination(BaseModel):
    """Pagination metadata schema."""

    total_results: int
    current_results_on_page: int
    current_page: int
    next_page: Optional[int] = None
    previous_page: Optional[int] = None
    total_pages: int


# ============================================================
# VERIFICATION/STATUS ENUMS
# ============================================================


class VerificationStatus(str, Enum):
    """User verification status enum."""

    not_started = "not_started"
    pending = "pending"
    completed = "completed"
    failed = "failed"
    confirming = "confirming"
    kyc_tier_1 = "kyc_tier_1"
    cancel = "cancel"


class AccountStatus(str, Enum):
    """User account status enum."""

    active = "active"
    inactive = "inactive"
    suspended = "suspended"
    pending = "pending"


# ============================================================
# COMMON INPUT SCHEMAS
# ============================================================


class TransactionPin(BaseModel):
    """Schema for transaction PIN input."""

    transaction_pin: constr(max_length=255)


class AccountUserSearch(BaseModel):
    """Schema for user account search response."""

    entity_id: UUID
    account_name: str
    username: str
    selfie_image: Optional[str] = None


# ============================================================
# HELPER FUNCTIONS
# ============================================================


def create_pagination(
    total_results: int,
    page: int,
    page_size: int,
) -> Pagination:
    """
    Create pagination metadata from query results.

    :param total_results: Total number of results in the database.
    :param page: Current page number (1-indexed).
    :param page_size: Number of items per page.
    :return: Pagination object with calculated metadata.
    """
    total_pages = (total_results + page_size - 1) // page_size if page_size > 0 else 0
    current_results = min(page_size, total_results - (page - 1) * page_size)
    current_results = max(0, current_results)

    return Pagination(
        total_results=total_results,
        current_results_on_page=current_results,
        current_page=page,
        next_page=page + 1 if page < total_pages else None,
        previous_page=page - 1 if page > 1 else None,
        total_pages=total_pages,
    )


def success_response(
    message: str = "Success",
    data: Optional[dict] = None,
) -> SuccessResponse:
    """
    Create a standard success response.

    :param message: Success message.
    :param data: Optional data to include in response.
    :return: SuccessResponse object.
    """
    return SuccessResponse(message=message, success=True, data=data)


def error_response(
    message: str,
    error_code: Optional[str] = None,
    details: Optional[dict] = None,
) -> ErrorResponse:
    """
    Create a standard error response.

    :param message: Error message.
    :param error_code: Optional error code for client handling.
    :param details: Optional additional error details.
    :return: ErrorResponse object.
    """
    return ErrorResponse(
        message=message,
        success=False,
        error_code=error_code,
        details=details,
    )

