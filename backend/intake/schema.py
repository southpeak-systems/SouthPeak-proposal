from pydantic import BaseModel
from typing import Optional

class IntakeAnalysis(BaseModel):
    business_name: Optional[str] = None
    industry: Optional[str] = None
    pain_points: list[str]
    budget_range: Optional[str] = None
    urgency: str  # low | medium | high
    fit_score: int  # 1-10
    recommended_service: str
    summary: str
