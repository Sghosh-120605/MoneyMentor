from fastapi import APIRouter
from pydantic import BaseModel
from typing import Dict, Any
from services.ai_analyzer import determine_best_tool

router = APIRouter()

class OnboardingRequest(BaseModel):
    answers: Dict[str, str]

class OnboardingResponse(BaseModel):
    recommended_path: str
    tool_name: str
    reasoning: str

@router.post("/onboarding", response_model=OnboardingResponse)
async def analyze_onboarding(request: OnboardingRequest):
    """
    Analyzes the onboarding questionnaire and recommends the best tool.
    """
    result = determine_best_tool(request.answers)
    return result
