from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
import datetime


class InterviewQuestion(BaseModel):
    question: str
    objectif: Optional[str] = None
    reponse_attendue: Optional[str] = None
    conseil_recruteur: Optional[str] = None


class AnalysisData(BaseModel):
    score_global: Optional[int] = Field(None, ge=0, le=100)
    verdict: Optional[str] = None
    score_justification: Optional[str] = None
    hiring_recommendation: Optional[str] = None
    seniority_level: Optional[str] = None
    years_of_experience: Optional[str] = None
    resume_executif: Optional[str] = None
    points_forts: Optional[List[str]] = None
    points_amelioration: Optional[List[str]] = None
    competences_cles: Optional[Dict[str, Any]] = None
    matching_keywords: Optional[List[str]] = None
    missing_keywords: Optional[List[str]] = None
    red_flags: Optional[List[str]] = None
    technical_gaps: Optional[List[str]] = None
    cover_letter_tips: Optional[List[str]] = None
    experience_gap: Optional[str] = None
    alternative_jobs: Optional[List[str]] = None
    interview_questions: Optional[List[InterviewQuestion]] = None

    class Config:
        extra = "allow"


class AnalysisCreate(BaseModel):
    job_title: str = Field(..., min_length=1, max_length=255)
    cv_filename: str = Field(..., min_length=1, max_length=255)
    analysis_data: Dict[str, Any]


class AnalysisResult(BaseModel):
    id: int
    job_title: str
    cv_filename: str
    analysis_data: Dict[str, Any]
    created_at: datetime.datetime

    class Config:
        from_attributes = True