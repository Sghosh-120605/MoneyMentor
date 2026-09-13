"""
Health Score routes — 6-dimension financial health scoring.
"""

from fastapi import APIRouter, HTTPException
from core.portfolio_schemas import HealthScoreRequest, HealthScoreResult, HealthDimension
from core.financial_models import (
    score_emergency_fund,
    score_insurance_coverage,
    score_diversification,
    score_debt_health,
    score_tax_efficiency,
    score_retirement_readiness,
)

router = APIRouter()


def _grade(score: int) -> str:
    if score >= 80: return "A"
    if score >= 65: return "B"
    if score >= 50: return "C"
    if score >= 35: return "D"
    return "F"


@router.post("/health-score", response_model=HealthScoreResult)
async def calculate_health_score(req: HealthScoreRequest):
    """Calculate 6-dimension money health score."""
    try:
        # 1. Emergency Fund
        ef = score_emergency_fund(req.monthly_expenses, req.emergency_fund)
        ef_dim = HealthDimension(
            name="Emergency Fund",
            score=ef["score"],
            details=ef,
            improvement_tip=(
                f"Build ₹{ef.get('gap_amount', 0):,.0f} more in liquid funds to reach 6-month cover."
                if ef["score"] < 80 else "Great! You have 6+ months covered."
            ),
        )

        # 2. Insurance Coverage
        ins = score_insurance_coverage(
            req.annual_income, req.life_cover, req.health_cover, req.dependants
        )
        ins_dim = HealthDimension(
            name="Insurance Coverage",
            score=ins["score"],
            details=ins,
            improvement_tip=(
                f"Increase term life cover by ₹{ins.get('life_gap', 0):,.0f} (target: 10x income)."
                if ins.get("life_gap", 0) > 500_000 else
                "Your life cover looks adequate. Consider topping up health cover."
            ),
        )

        # 3. Investment Diversification
        holdings = []
        if req.total_investments > 0:
            if req.equity_pct > 0:
                holdings.append({"category": "equity", "current_value": req.total_investments * req.equity_pct / 100})
            if req.debt_pct > 0:
                holdings.append({"category": "debt", "current_value": req.total_investments * req.debt_pct / 100})
            if req.gold_pct > 0:
                holdings.append({"category": "gold", "current_value": req.total_investments * req.gold_pct / 100})
            other = 100 - req.equity_pct - req.debt_pct - req.gold_pct
            if other > 0:
                holdings.append({"category": "other", "current_value": req.total_investments * other / 100})

        div = score_diversification(holdings)
        div_dim = HealthDimension(
            name="Investment Diversification",
            score=div["score"],
            details=div,
            improvement_tip=(
                "Add debt/gold to your portfolio for better diversification."
                if div["score"] < 60 else "Good spread across asset classes!"
            ),
        )

        # 4. Debt Health
        debt = score_debt_health(
            req.annual_income,
            req.monthly_emi,
            [req.avg_loan_rate] if req.avg_loan_rate > 0 else [],
        )
        debt_dim = HealthDimension(
            name="Debt Health",
            score=debt["score"],
            details=debt,
            improvement_tip=(
                f"Your EMI-to-income ratio is {debt.get('dti_ratio', 0):.1f}%. Target below 35%."
                if debt["score"] < 70 else "Your debt load is manageable!"
            ),
        )

        # 5. Tax Efficiency
        tax = score_tax_efficiency(
            req.missed_deductions_count,
            req.tax_potential_savings,
            req.annual_income,
        )
        tax_dim = HealthDimension(
            name="Tax Efficiency",
            score=tax["score"],
            details=tax,
            improvement_tip=(
                f"Claim {req.missed_deductions_count} missed deductions to save ₹{req.tax_potential_savings:,.0f}/year."
                if req.missed_deductions_count > 0 else "You're claiming all major deductions!"
            ),
        )

        # 6. Retirement Readiness
        ret = score_retirement_readiness(
            req.age,
            req.annual_income,
            req.current_corpus,
            req.monthly_sip,
            req.retirement_age,
        )
        ret_dim = HealthDimension(
            name="Retirement Readiness",
            score=ret["score"],
            details=ret,
            improvement_tip=(
                f"Increase SIP by ₹{max(0, ret.get('monthly_sip_required', 0) - req.monthly_sip):,.0f}/month to stay on track."
                if ret["score"] < 70 else "You're on track for retirement!"
            ),
        )

        dimensions = [ef_dim, ins_dim, div_dim, debt_dim, tax_dim, ret_dim]

        # Weighted overall score
        weights = [0.20, 0.20, 0.15, 0.15, 0.15, 0.15]
        overall = int(sum(d.score * w for d, w in zip(dimensions, weights)))

        # Top 3 improvements — sort by lowest score
        sorted_dims = sorted(dimensions, key=lambda d: d.score)
        improvement_actions = [
            {
                "dimension": d.name,
                "current_score": d.score,
                "tip": d.improvement_tip,
                "score_impact": min(20, 100 - d.score),
            }
            for d in sorted_dims[:3]
        ]

        projected = min(100, overall + sum(a["score_impact"] for a in improvement_actions) // 3)

        return HealthScoreResult(
            overall_score=overall,
            dimensions=dimensions,
            grade=_grade(overall),
            improvement_actions=improvement_actions,
            projected_score_after_actions=projected,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Health score calculation failed: {str(e)}")
