"""
Quiz, Question, and Attempt schemas.
Pydantic models for the quiz system.
"""

from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID


# Answer Option schemas
class AnswerOptionBase(BaseModel):
    """Base schema for answer options."""

    option_text: str


class AnswerOption(AnswerOptionBase):
    """Schema for answer option response."""

    option_id: UUID
    question_id: UUID

    class Config:
        from_attributes = True


# Question schemas
class QuestionBase(BaseModel):
    """Base schema for questions."""

    question_text: str
    correct_answer: str
    order: int


class Question(QuestionBase):
    """Schema for question response."""

    question_id: UUID
    quiz_id: UUID
    answer_options: List[AnswerOption] = []

    class Config:
        from_attributes = True


class QuestionResult(BaseModel):
    """Schema for individual question results."""

    question_id: UUID
    question_text: str
    user_answer: str
    correct_answer: Optional[str]
    is_correct: bool
    points: int
    earned_points: int
    explanation: Optional[str]
    options: Dict[str, Any]


# Quiz schemas
class QuizBase(BaseModel):
    """Base schema for Quiz data."""

    title: str
    description: Optional[str] = None
    duration: int
    difficulty: str
    specialization_id: UUID


class Quiz(QuizBase):
    """Schema for Quiz response with questions."""

    quiz_id: UUID
    questions: List[Question] = []

    class Config:
        from_attributes = True


class QuizSummary(BaseModel):
    """Schema for Quiz listing (without questions)."""

    quiz_id: UUID
    title: str
    description: Optional[str] = None
    duration: int
    difficulty: int  # Difficulty level as integer
    question_count: int
    specialization_id: Optional[UUID] = None
    specialization_name: Optional[str] = None

    class Config:
        from_attributes = True


class QuizzesResponse(BaseModel):
    """Response schema for list of quizzes."""

    quizzes: List[QuizSummary]


# Quiz Answer/Submission schemas
class QuizAnswer(BaseModel):
    """Schema for a single quiz answer."""

    question_id: UUID
    selected_answer: str


# Alias for backward compatibility
AnswerSubmit = QuizAnswer


class QuizSubmission(BaseModel):
    """Schema for submitting quiz answers."""

    answers: List[QuizAnswer]


# Quiz Attempt schemas
class QuizAttemptBase(BaseModel):
    """Base schema for quiz attempt."""

    user_id: UUID
    quiz_id: UUID


class QuizAttempt(QuizAttemptBase):
    """Schema for quiz attempt response."""

    attempt_id: UUID
    started_at: datetime
    completed_at: Optional[datetime] = None
    score: Optional[float] = None
    is_completed: bool = False

    class Config:
        from_attributes = True


class QuizStartResponse(BaseModel):
    """Response schema for starting a quiz."""

    attempt_id: str
    quiz_id: str
    message: str


# Quiz Result schemas
class ReadinessSnapshot(BaseModel):
    """Snapshot of user's readiness scores."""

    overall: float
    technical: float
    soft: float


class FeedbackDetail(BaseModel):
    """Detailed feedback for quiz performance."""

    overall: str
    strengths: str
    weaknesses: str
    recommendations: List[str]


class ScoreImpact(BaseModel):
    """Impact of quiz on user scores."""

    category: str
    old_score: float
    new_score: float
    increase: float


class QuizResult(BaseModel):
    """Schema for basic quiz result."""

    success: bool
    score: float
    correct: int
    total: int
    passed: bool
    message: str


class QuizResultExtended(QuizResult):
    """Extended quiz result with detailed feedback."""

    readiness: ReadinessSnapshot
    feedback: Optional[FeedbackDetail] = None
    question_results: Optional[List[QuestionResult]] = None
    score_impact: Optional[ScoreImpact] = None
    quiz_title: Optional[str] = None
    passing_score: Optional[float] = None
    raw_score: Optional[float] = None
    max_score: Optional[float] = None


# ============================================================
# RESPONSE SCHEMAS FOR ENDPOINTS
# ============================================================


class QuizListItem(BaseModel):
    """Individual quiz item in list responses."""

    quiz_id: str
    title: str
    description: Optional[str] = None
    specialization_id: str
    specialization_name: Optional[str] = None
    duration: Optional[int] = None
    question_count: int
    difficulty: Optional[int] = None


class QuizListResponse(BaseModel):
    """Response schema for GET /quizzes/."""

    quizzes: List[QuizListItem]


class QuestionOptionResponse(BaseModel):
    """Option in a quiz question."""

    text: str
    is_correct: bool


class QuizQuestionResponse(BaseModel):
    """Question in quiz detail response."""

    question_id: str
    question: str
    options: List[QuestionOptionResponse]
    correct_index: Optional[int] = None
    explanation: Optional[str] = None


class QuizDetailResponse(BaseModel):
    """Response schema for GET /quizzes/{quiz_id}."""

    quiz_id: str
    title: str
    description: Optional[str] = None
    duration: Optional[int] = None
    question_count: int
    difficulty: Optional[int] = None
    specialization_id: str
    questions: List[QuizQuestionResponse]


class UpdatedGoalItem(BaseModel):
    """Auto-updated goal after quiz submission."""

    goal_id: str
    title: str
    old_value: float
    new_value: float
    is_completed: bool


class QuizSubmitResponse(BaseModel):
    """Response schema for POST /quizzes/attempts/{attempt_id}/submit."""

    success: bool
    score: float
    correct: int
    total: int
    passed: bool
    message: str
    readiness: ReadinessSnapshot
    feedback: Optional[FeedbackDetail] = None
    question_results: Optional[List[Dict[str, Any]]] = None
    score_impact: Optional[Dict[str, Any]] = None
    quiz_title: Optional[str] = None
    passing_score: Optional[float] = None
    raw_score: Optional[float] = None
    max_score: Optional[float] = None
    updated_goals: List[UpdatedGoalItem] = []


class AttemptInfo(BaseModel):
    """Attempt information in result response."""

    attempt_id: str
    quiz_id: str
    score: Optional[float] = None
    passed: Optional[bool] = None
    completed_at: Optional[str] = None


class QuizInfo(BaseModel):
    """Quiz information in result response."""

    quiz_id: str
    title: str
    description: Optional[str] = None


class AttemptResultResponse(BaseModel):
    """Response schema for GET /quizzes/attempts/{attempt_id}/results."""

    attempt: AttemptInfo
    quiz: QuizInfo
    readiness: ReadinessSnapshot
