"""
Pydantic models for Resume Amplifier API request/response contracts.
"""

from pydantic import BaseModel, Field
from typing import Optional


# ── Shared base ───────────────────────────────────────────────────────────────

class BaseRequest(BaseModel):
    jd_text: str = Field(..., min_length=10, description="Full job description text")
    resume_text: str = Field(..., min_length=10, description="Full resume text")


# ── /score ────────────────────────────────────────────────────────────────────

class ScoreRequest(BaseRequest):
    pass

class ScoreBreakdown(BaseModel):
    skills_match: int
    experience_relevance: int
    education_fit: int
    keyword_coverage: int

class ScoreResponse(BaseModel):
    score: int
    label: str
    summary: str
    breakdown: ScoreBreakdown
    matched_keywords: list[str]
    missing_keywords: list[str]


# ── /strengths ────────────────────────────────────────────────────────────────

class StrengthsRequest(BaseRequest):
    pass

class StrengthItem(BaseModel):
    title: str
    detail: str

class WeaknessItem(BaseModel):
    title: str
    detail: str
    suggestion: str = ""

class StrengthsResponse(BaseModel):
    strengths: list[StrengthItem]
    weaknesses: list[WeaknessItem]
    critical_gaps: list[str]
    quick_wins: list[str]


# ── /qa ───────────────────────────────────────────────────────────────────────

class QARequest(BaseRequest):
    question: str = Field(..., min_length=3, description="Question about the JD or resume")

class QAResponse(BaseModel):
    answer: str


# ── /rewrite ──────────────────────────────────────────────────────────────────

class RewriteRequest(BaseRequest):
    pass

class RewriteResponse(BaseModel):
    improved_resume: str


# ── /interview ────────────────────────────────────────────────────────────────

class InterviewRequest(BaseRequest):
    pass

class InterviewQuestion(BaseModel):
    category: str
    question: str
    why_asked: str
    suggested_answer: str

class InterviewResponse(BaseModel):
    questions: list[InterviewQuestion]


# ── /cover-letter ─────────────────────────────────────────────────────────────

class CoverLetterRequest(BaseRequest):
    pass

class CoverLetterResponse(BaseModel):
    cover_letter: str


# ── /export ───────────────────────────────────────────────────────────────────

class ExportResumeRequest(BaseModel):
    improved_resume: str
    candidate_name: str = "Candidate"
    format: str = Field("pdf", pattern="^(pdf|docx)$")

class ExportCoverLetterRequest(BaseModel):
    cover_letter: str
    candidate_name: str = "Candidate"
    format: str = Field("pdf", pattern="^(pdf|docx)$")

class ExportInterviewRequest(BaseModel):
    interview_data: dict
    candidate_name: str = "Candidate"
    format: str = Field("docx", pattern="^(docx|txt)$")


# ── Error ─────────────────────────────────────────────────────────────────────

class ErrorResponse(BaseModel):
    detail: str
