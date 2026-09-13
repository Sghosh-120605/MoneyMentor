"""
Affordability Advisor — "Should I Buy This?"
Computes whether a user can afford a big purchase right now, or should wait.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
import math

router = APIRouter()


class AffordRequest(BaseModel):
    # What they want to buy
    item_name: str = "Car"
    item_cost: float = 0              # Total price in ₹
    down_payment_pct: float = 20      # % of cost paid upfront
    loan_tenure_years: float = 5      # EMI tenure
    loan_interest_rate: float = 9.0   # Annual interest rate %

    # Their financial profile
    monthly_income: float = 0
    monthly_expenses: float = 0       # Existing monthly expenses (excl EMIs)
    existing_emis: float = 0          # Current total EMI burden
    total_savings: float = 0          # Liquid savings
    emergency_fund_target_months: int = 6
    monthly_sip: float = 0            # Current SIP/investment
    age: int = 30
    retirement_age: int = 60


def _emi(principal: float, annual_rate: float, tenure_months: int) -> float:
    """Standard reducing-balance EMI formula."""
    if principal <= 0 or tenure_months <= 0:
        return 0
    if annual_rate <= 0:
        return principal / tenure_months
    r = annual_rate / 100 / 12
    return principal * r * (1 + r) ** tenure_months / ((1 + r) ** tenure_months - 1)


@router.post("/affordability-check")
async def affordability_check(req: AffordRequest):
    # ── Core calculations ──
    down_payment = req.item_cost * req.down_payment_pct / 100
    loan_amount = req.item_cost - down_payment
    tenure_months = int(req.loan_tenure_years * 12)
    monthly_emi = round(_emi(loan_amount, req.loan_interest_rate, tenure_months))
    total_interest = round(monthly_emi * tenure_months - loan_amount) if monthly_emi > 0 else 0
    total_cost = round(req.item_cost + total_interest)

    monthly_surplus = req.monthly_income - req.monthly_expenses - req.existing_emis
    new_surplus = monthly_surplus - monthly_emi

    # DTI (Debt-to-Income) ratio
    current_dti = round(req.existing_emis / req.monthly_income * 100, 1) if req.monthly_income > 0 else 0
    new_dti = round((req.existing_emis + monthly_emi) / req.monthly_income * 100, 1) if req.monthly_income > 0 else 0

    # Emergency fund check
    monthly_expenses_after = req.monthly_expenses + req.existing_emis + monthly_emi
    emergency_fund_needed = monthly_expenses_after * req.emergency_fund_target_months
    savings_after_down = req.total_savings - down_payment
    emergency_fund_covered = savings_after_down / monthly_expenses_after if monthly_expenses_after > 0 else 0
    emergency_fund_ok = savings_after_down >= emergency_fund_needed

    # Savings rate impact
    current_savings_rate = round((monthly_surplus / req.monthly_income) * 100, 1) if req.monthly_income > 0 else 0
    new_savings_rate = round((new_surplus / req.monthly_income) * 100, 1) if req.monthly_income > 0 else 0

    # SIP impact — can they continue investing?
    sip_sustainable = new_surplus >= req.monthly_sip
    sip_cut_needed = max(0, round(req.monthly_sip - max(0, new_surplus)))

    # FIRE delay estimation
    fire_delay_months = 0
    if req.monthly_sip > 0 and monthly_emi > 0:
        # Rough: each ₹ of SIP cut delays FIRE by proportional months
        sip_reduction_ratio = min(1.0, monthly_emi / (req.monthly_sip + monthly_surplus))
        fire_delay_months = round(sip_reduction_ratio * tenure_months * 0.3)  # ~30% impact factor

    # How long to wait to afford it comfortably
    months_to_save_down = 0
    if down_payment > savings_after_down and monthly_surplus > 0:
        months_to_save_down = math.ceil((down_payment - req.total_savings) / monthly_surplus)
    elif down_payment > req.total_savings and monthly_surplus > 0:
        months_to_save_down = math.ceil((down_payment - req.total_savings) / monthly_surplus)

    # Wait until DTI would be <= 35% (healthy)
    months_to_healthy_dti = 0
    if new_dti > 35 and monthly_surplus > 0:
        # Need to either increase income or reduce loan
        # Approximate: save more so you can put larger down payment
        target_emi = req.monthly_income * 0.35 - req.existing_emis
        if target_emi > 0 and target_emi < monthly_emi:
            needed_down = req.item_cost - (target_emi * ((1 + req.loan_interest_rate/100/12) ** tenure_months - 1) /
                                           (req.loan_interest_rate/100/12 * (1 + req.loan_interest_rate/100/12) ** tenure_months))
            extra_needed = max(0, needed_down - req.total_savings)
            months_to_healthy_dti = math.ceil(extra_needed / monthly_surplus) if monthly_surplus > 0 else 999

    wait_months = max(months_to_save_down, months_to_healthy_dti)

    # Suggested affordable amount (keep DTI <= 35%)
    max_affordable_emi = max(0, req.monthly_income * 0.35 - req.existing_emis)
    r = req.loan_interest_rate / 100 / 12
    if r > 0 and tenure_months > 0:
        max_loan = max_affordable_emi * ((1 + r) ** tenure_months - 1) / (r * (1 + r) ** tenure_months)
    else:
        max_loan = max_affordable_emi * tenure_months
    max_affordable_price = round(max_loan + req.total_savings * 0.5)  # Use half savings as down payment

    # ── VERDICT ──
    can_afford_down = req.total_savings >= down_payment * 1.2  # 20% buffer
    dti_healthy = new_dti <= 35
    surplus_positive = new_surplus > 0
    emergency_ok = emergency_fund_ok

    if can_afford_down and dti_healthy and surplus_positive and emergency_ok:
        verdict = "BUY NOW"
        verdict_detail = f"You can comfortably afford this {req.item_name}. Your DTI stays healthy at {new_dti}% and you retain emergency coverage."
        verdict_color = "green"
    elif can_afford_down and surplus_positive and new_dti <= 50:
        verdict = "BUY WITH CAUTION"
        verdict_detail = f"You can technically afford it, but your DTI of {new_dti}% is above the healthy 35% threshold. Consider a larger down payment or longer tenure."
        verdict_color = "amber"
    elif surplus_positive and wait_months > 0 and wait_months <= 24:
        verdict = f"WAIT {wait_months} MONTHS"
        verdict_detail = f"Save for {wait_months} more months to build a comfortable down payment and keep DTI under 35%."
        verdict_color = "amber"
    elif surplus_positive and wait_months > 24:
        verdict = "NOT AFFORDABLE YET"
        verdict_detail = f"At your current savings rate, you'd need {wait_months} months ({round(wait_months/12, 1)} years) to afford this comfortably. Consider a lower budget."
        verdict_color = "red"
    else:
        verdict = "SKIP THIS"
        verdict_detail = f"This purchase would put you in negative monthly cash flow (₹{abs(round(new_surplus)):,}/month deficit). Your finances need strengthening first."
        verdict_color = "red"

    # ── Actionable tips ──
    tips = []
    if not can_afford_down:
        tips.append(f"Build your down payment: you need ₹{round(down_payment):,} but only have ₹{round(req.total_savings):,} in savings.")
    if not dti_healthy:
        tips.append(f"Your EMI burden would be {new_dti}% of income. Try to keep it under 35% — consider a longer tenure ({int(req.loan_tenure_years + 2)} years) to reduce EMI to ~₹{round(_emi(loan_amount, req.loan_interest_rate, int((req.loan_tenure_years + 2) * 12))):,}/month.")
    if not emergency_ok:
        tips.append(f"After the down payment, you'd have only {emergency_fund_covered:.1f} months of emergency cover. Target {req.emergency_fund_target_months} months before buying.")
    if sip_cut_needed > 0:
        tips.append(f"You'd need to cut ₹{sip_cut_needed:,}/month from your investments — this delays wealth building.")
    if fire_delay_months > 0:
        tips.append(f"This purchase could delay your retirement goal by ~{fire_delay_months} months.")
    if max_affordable_price < req.item_cost and max_affordable_price > 0:
        tips.append(f"A budget of ₹{max_affordable_price:,} would keep your finances healthy (vs ₹{round(req.item_cost):,} requested).")
    if not tips:
        tips.append("Your finances are strong enough to handle this purchase without stress. Go ahead!")

    return {
        "verdict": verdict,
        "verdict_detail": verdict_detail,
        "verdict_color": verdict_color,

        "item": {
            "name": req.item_name,
            "cost": round(req.item_cost),
            "down_payment": round(down_payment),
            "loan_amount": round(loan_amount),
            "monthly_emi": monthly_emi,
            "total_interest": total_interest,
            "total_cost": total_cost,
            "tenure_months": tenure_months,
        },

        "impact": {
            "current_dti": current_dti,
            "new_dti": new_dti,
            "dti_healthy": dti_healthy,
            "current_surplus": round(monthly_surplus),
            "new_surplus": round(new_surplus),
            "current_savings_rate": current_savings_rate,
            "new_savings_rate": new_savings_rate,
            "emergency_fund_months_after": round(emergency_fund_covered, 1),
            "emergency_fund_ok": emergency_ok,
            "sip_sustainable": sip_sustainable,
            "sip_cut_needed": sip_cut_needed,
            "fire_delay_months": fire_delay_months,
        },

        "wait_months": wait_months,
        "max_affordable_price": max_affordable_price,
        "tips": tips,
    }
