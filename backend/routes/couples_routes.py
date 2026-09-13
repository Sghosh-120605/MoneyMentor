"""
Couple's Money Planner — Joint tax optimization for married couples.
Determines which partner should claim shared deductions for maximum savings.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List

router = APIRouter()


class PartnerProfile(BaseModel):
    name: str = "Partner A"
    annual_income: float = 0
    section_80c: float = 0          # EPF + ELSS + PPF etc.
    section_80ccd_1b: float = 0     # NPS
    section_80d_self: float = 0     # Health insurance — self
    section_80d_parents: float = 0  # Health insurance — parents
    hra_received: float = 0
    rent_paid: float = 0
    is_metro: bool = True
    basic_salary: float = 0
    standard_deduction: float = 75000
    professional_tax: float = 2400
    age: int = 30


class CouplesRequest(BaseModel):
    partner_a: PartnerProfile
    partner_b: PartnerProfile
    # Shared deductions — system decides who claims each
    home_loan_interest: float = 0      # Section 24(b)
    home_loan_principal: float = 0     # Part of 80C
    education_loan_interest: float = 0 # Section 80E
    health_insurance_family: float = 0 # Shared family floater


# ── Tax Engine (FY 2025-26 Old Regime) ─────────────────────────────────────────

OLD_SLABS = [
    (250000, 0.00),
    (500000, 0.05),
    (1000000, 0.20),
    (float("inf"), 0.30),
]

NEW_SLABS = [
    (400000, 0.00),
    (800000, 0.05),
    (1200000, 0.10),
    (1600000, 0.15),
    (2000000, 0.20),
    (2400000, 0.25),
    (float("inf"), 0.30),
]


def _compute_slab_tax(income: float, slabs: list) -> float:
    """Compute tax from slab structure."""
    tax = 0
    prev = 0
    for limit, rate in slabs:
        if income <= prev:
            break
        taxable_in_slab = min(income, limit) - prev
        tax += taxable_in_slab * rate
        prev = limit
    return tax


def _old_regime_tax(income: float, deductions: float, hra_exempt: float) -> float:
    """Full Old Regime tax calculation."""
    gross = income
    net = gross - hra_exempt - 50000 - 2400  # std ded + prof tax
    taxable = max(0, net - deductions)
    base_tax = _compute_slab_tax(taxable, OLD_SLABS)

    # Section 87A rebate (Old: up to Rs 5L taxable income, rebate up to Rs 12,500)
    if taxable <= 500000:
        base_tax = max(0, base_tax - 12500)

    # Surcharge
    surcharge = 0
    if taxable > 5000000:
        surcharge = base_tax * 0.10
    elif taxable > 10000000:
        surcharge = base_tax * 0.15

    # Cess
    total = base_tax + surcharge
    total += total * 0.04
    return round(total)


def _new_regime_tax(income: float, employer_nps: float = 0) -> float:
    """Full New Regime tax calculation."""
    gross = income
    net = gross - 75000 - 2400 - employer_nps  # std ded + prof tax + employer NPS
    taxable = max(0, net)
    base_tax = _compute_slab_tax(taxable, NEW_SLABS)

    # Section 87A rebate (New: up to Rs 12L taxable income, rebate up to Rs 60,000)
    if taxable <= 1200000:
        base_tax = max(0, base_tax - 60000)

    # Surcharge
    surcharge = 0
    if taxable > 5000000:
        surcharge = base_tax * 0.10

    total = base_tax + surcharge
    total += total * 0.04
    return round(total)


def _hra_exemption(basic: float, hra_received: float, rent_paid: float, is_metro: bool) -> float:
    """Calculate HRA exemption under Old Regime."""
    if rent_paid <= 0 or hra_received <= 0:
        return 0
    metro_pct = 0.50 if is_metro else 0.40
    return min(
        hra_received,
        rent_paid - 0.10 * basic,
        metro_pct * basic,
    )


def _optimise_deduction(amount: float, partner_a_bracket: float, partner_b_bracket: float, label: str):
    """Decide which partner should claim a shared deduction for max savings."""
    if amount <= 0:
        return None

    a_saving = amount * partner_a_bracket
    b_saving = amount * partner_b_bracket

    if a_saving >= b_saving:
        assigned_to = "A"
        saving = a_saving
        reason = f"Partner A is in the {int(partner_a_bracket*100)}% bracket — claiming here saves Rs. {int(saving):,}"
    else:
        assigned_to = "B"
        saving = b_saving
        reason = f"Partner B is in the {int(partner_b_bracket*100)}% bracket — claiming here saves Rs. {int(saving):,}"

    extra_saving = abs(a_saving - b_saving)

    return {
        "deduction": label,
        "amount": amount,
        "assigned_to": assigned_to,
        "saving": round(saving),
        "extra_saving_vs_wrong_partner": round(extra_saving),
        "reason": reason,
    }


def _get_bracket(income: float) -> float:
    """Get marginal tax bracket for Old Regime."""
    taxable = income - 50000 - 2400  # rough
    if taxable <= 250000:
        return 0.00
    elif taxable <= 500000:
        return 0.05
    elif taxable <= 1000000:
        return 0.20
    else:
        return 0.30


# ── Route ──────────────────────────────────────────────────────────────────────

@router.post("/couples-plan")
async def couples_plan(req: CouplesRequest):
    a = req.partner_a
    b = req.partner_b

    # Compute individual HRA
    a_hra = _hra_exemption(a.basic_salary, a.hra_received, a.rent_paid, a.is_metro)
    b_hra = _hra_exemption(b.basic_salary, b.hra_received, b.rent_paid, b.is_metro)

    # Individual deductions (before shared ones)
    a_ded = a.section_80c + a.section_80ccd_1b + a.section_80d_self + a.section_80d_parents
    b_ded = b.section_80c + b.section_80ccd_1b + b.section_80d_self + b.section_80d_parents

    # Marginal brackets
    a_bracket = _get_bracket(a.annual_income)
    b_bracket = _get_bracket(b.annual_income)

    # ── Optimise shared deductions ──
    optimisations = []
    a_shared = 0
    b_shared = 0

    shared_items = [
        (req.home_loan_interest, "Home Loan Interest (Section 24b)"),
        (req.home_loan_principal, "Home Loan Principal (Section 80C)"),
        (req.education_loan_interest, "Education Loan Interest (Section 80E)"),
        (req.health_insurance_family, "Family Health Insurance (Section 80D)"),
    ]

    for amount, label in shared_items:
        opt = _optimise_deduction(amount, a_bracket, b_bracket, label)
        if opt:
            optimisations.append(opt)
            if opt["assigned_to"] == "A":
                a_shared += amount
            else:
                b_shared += amount

    # ── Compute taxes ──
    a_total_ded = a_ded + a_shared
    b_total_ded = b_ded + b_shared

    a_old_tax = _old_regime_tax(a.annual_income, a_total_ded, a_hra)
    a_new_tax = _new_regime_tax(a.annual_income)
    b_old_tax = _old_regime_tax(b.annual_income, b_total_ded, b_hra)
    b_new_tax = _new_regime_tax(b.annual_income)

    a_best = "old" if a_old_tax <= a_new_tax else "new"
    b_best = "old" if b_old_tax <= b_new_tax else "new"

    a_tax = min(a_old_tax, a_new_tax)
    b_tax = min(b_old_tax, b_new_tax)

    # ── Naive comparison (what if all shared deductions went to wrong partner) ──
    naive_a_ded = a_ded + sum(amt for amt, _ in shared_items)
    naive_a_old = _old_regime_tax(a.annual_income, naive_a_ded, a_hra)
    naive_b_old = _old_regime_tax(b.annual_income, b_ded, b_hra)
    naive_total = min(naive_a_old, a_new_tax) + min(naive_b_old, b_new_tax)

    optimised_total = a_tax + b_tax
    joint_savings = max(0, naive_total - optimised_total)

    # ── Build actionable tips ──
    tips = []
    if a_bracket != b_bracket:
        higher = "A" if a_bracket > b_bracket else "B"
        tips.append(f"Partner {higher} is in a higher tax bracket — route all shared deductions through them for maximum savings.")

    if a_best != b_best:
        tips.append(f"Interestingly, Partner A benefits from the {a_best.upper()} regime while Partner B benefits from the {b_best.upper()} regime. Each should opt for their respective best regime with their employer.")

    if req.home_loan_interest > 0 and a_bracket != b_bracket:
        tips.append(f"Home loan interest of Rs. {int(req.home_loan_interest):,} should be claimed by the higher-bracket partner to maximise the Rs. {int(req.home_loan_interest * max(a_bracket, b_bracket)):,} deduction benefit.")

    if a.section_80c < 150000 and a_bracket > 0:
        gap = 150000 - a.section_80c
        tips.append(f"Partner A has Rs. {int(gap):,} unused 80C limit — invest in ELSS/PPF/NPS to save Rs. {int(gap * a_bracket):,} in tax.")

    if b.section_80c < 150000 and b_bracket > 0:
        gap = 150000 - b.section_80c
        tips.append(f"Partner B has Rs. {int(gap):,} unused 80C limit — invest in ELSS/PPF/NPS to save Rs. {int(gap * b_bracket):,} in tax.")

    if a.section_80ccd_1b == 0 and a_bracket >= 0.20:
        tips.append(f"Partner A should invest Rs. 50,000 in NPS (80CCD(1B)) — saves Rs. {int(50000 * a_bracket):,} exclusively.")

    if b.section_80ccd_1b == 0 and b_bracket >= 0.20:
        tips.append(f"Partner B should invest Rs. 50,000 in NPS (80CCD(1B)) — saves Rs. {int(50000 * b_bracket):,} exclusively.")

    return {
        "partner_a": {
            "name": a.name,
            "income": a.annual_income,
            "bracket": f"{int(a_bracket * 100)}%",
            "old_regime_tax": a_old_tax,
            "new_regime_tax": a_new_tax,
            "recommended_regime": a_best,
            "total_deductions": a_total_ded,
            "hra_exemption": a_hra,
            "tax_payable": a_tax,
        },
        "partner_b": {
            "name": b.name,
            "income": b.annual_income,
            "bracket": f"{int(b_bracket * 100)}%",
            "old_regime_tax": b_old_tax,
            "new_regime_tax": b_new_tax,
            "recommended_regime": b_best,
            "total_deductions": b_total_ded,
            "hra_exemption": b_hra,
            "tax_payable": b_tax,
        },
        "joint_summary": {
            "combined_tax": optimised_total,
            "savings_from_optimisation": joint_savings,
            "combined_income": a.annual_income + b.annual_income,
        },
        "deduction_assignments": optimisations,
        "tips": tips,
    }
