from pydantic import BaseModel
from typing import List, Dict, Any
import datetime

class AnalysisCreate(BaseModel):
    job_title: str
    cv_filename: str
    analysis_data: Dict[str, Any]

class AnalysisResult(AnalysisCreate):
    id: int
    created_at: datetime.datetime

    class Config:
        from_attributes = True