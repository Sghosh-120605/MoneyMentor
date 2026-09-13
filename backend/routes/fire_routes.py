"""
FIRE Planner routes — Financial Independence, Retire Early planning.
"""

from fastapi import APIRouter, HTTPException
from core.portfolio_schemas import FIRERequest, FIREPlan, FIREMilestone
from core.financial_models import calculate_fire_plan

router = APIRouter()


@router.post("/fire-plan", response_model=FIREPlan)
async def get_fire_plan(req: FIRERequest):
    """Generate a FIRE plan with milestone projections and asset allocation."""
    if req.annual_income <= 0:
        raise HTTPException(status_code=422, detail="Annual income must be greater than zero.")
    if req.fire_age <= req.age:
        raise HTTPException(status_code=422, detail="FIRE age must be greater than current age.")
    if req.fire_age > 80:
        raise HTTPException(status_code=422, detail="FIRE age must be 80 or below.")

    try:
        plan = calculate_fire_plan(
            age=req.age,
            annual_income=req.annual_income,
            annual_expenses=req.annual_expenses or req.annual_income * 0.70,
            current_savings=req.current_savings,
            monthly_sip=req.monthly_sip,
            risk_appetite=req.risk_appetite,
            fire_age=req.fire_age,
        )

        milestones = [FIREMilestone(**m) for m in plan.pop("milestones", [])]

        return FIREPlan(
            **plan,
            milestones=milestones,
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"FIRE plan calculation failed: {str(e)}")
