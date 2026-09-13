"""
Indian Tax Engine — Full implementation for FY 2025-26 (AY 2026-27).
Handles Old and New tax regimes with all major deductions.
"""

from typing import Tuple, Dict, List, Any
from core.schemas import TaxProfile, TaxComparison, MissedDeduction

# ===================================================================
# TAX SLABS — FY 2025-26
# ===================================================================

OLD_REGIME_SLABS = [
    (250_000, 0.00),
    (500_000, 0.05),
    (1_000_000, 0.20),
    (float("inf"), 0.30),
]

NEW_REGIME_SLABS = [
    (400_000, 0.00),
    (800_000, 0.05),
    (1_200_000, 0.10),
    (1_600_000, 0.15),
    (2_000_000, 0.20),
    (2_400_000, 0.25),
    (float("inf"), 0.30),
]

OLD_STD_DEDUCTION = 50_000
NEW_STD_DEDUCTION = 75_000

OLD_87A_LIMIT = 500_000
OLD_87A_MAX = 12_500
NEW_87A_LIMIT = 1_200_000
NEW_87A_MAX = 60_000

CESS = 0.04

LIMIT_80C = 150_000
LIMIT_80CCD1B = 50_000
LIMIT_80D_SELF = 25_000
LIMIT_80D_SELF_SR = 50_000
LIMIT_80D_PARENTS = 25_000
LIMIT_80D_PARENTS_SR = 50_000
LIMIT_24B = 200_000
LIMIT_80TTA = 10_000


# ===================================================================
# CORE CALCULATION FUNCTIONS
# ===================================================================


def _slab_tax(taxable: float, slabs: list) -> Tuple[float, list]:
    """Calculate tax from slabs. Returns (tax, breakdown)."""
    tax = 0.0
    remaining = taxable
    prev = 0
    breakdown = []
    for upper, rate in slabs:
        if remaining <= 0:
            break
        chunk = min(remaining, upper - prev)
        t = chunk * rate
        tax += t
        if chunk > 0:
            breakdown.append({
                "range": f"₹{prev:,.0f} – ₹{upper:,.0f}" if upper != float("inf") else f"Above ₹{prev:,.0f}",
                "amount": round(chunk),
                "rate": f"{rate * 100:.0f}%",
                "tax": round(t),
            })
        remaining -= chunk
        prev = upper
    return round(tax), breakdown


def calculate_hra_exemption(basic: float, hra: float, rent: float, metro: bool) -> float:
    """HRA exemption u/s 10(13A): min of actual HRA, 50/40% basic, rent-10% basic."""
    if rent <= 0 or hra <= 0:
        return 0.0
    pct = 0.50 if metro else 0.40
    return round(min(hra, basic * pct, max(0, rent - basic * 0.10)))


def _surcharge(tax: float, taxable: float, new_regime: bool) -> float:
    if taxable <= 5_000_000:
        return 0.0
    if taxable <= 10_000_000:
        r = 0.10
    elif taxable <= 20_000_000:
        r = 0.15
    elif taxable <= 50_000_000:
        r = 0.25
    else:
        r = 0.25 if new_regime else 0.37
    return round(tax * r)


# ===================================================================
# OLD REGIME
# ===================================================================


def compute_old_regime(profile: TaxProfile) -> Tuple[float, float, Dict[str, Any]]:
    s = profile.salary
    d = profile.deductions

    hra_exempt = calculate_hra_exemption(
        s.basic_salary, s.hra_received, profile.rent_paid, profile.is_metro
    )
    net_salary = s.gross_salary - hra_exempt
    std = min(OLD_STD_DEDUCTION, net_salary)
    prof_tax = s.professional_tax
    income_salary = max(0, net_salary - std - prof_tax)
    gti = income_salary + s.other_income

    # Chapter VI-A
    c80c = min(d.section_80c + s.epf_employee, LIMIT_80C)
    c80ccd = min(d.section_80ccd_1b, LIMIT_80CCD1B)
    max_80d = LIMIT_80D_SELF_SR if profile.age >= 60 else LIMIT_80D_SELF
    c80d = min(d.section_80d, max_80d + LIMIT_80D_PARENTS)
    c80e = d.section_80e
    c80g = d.section_80g
    c80tta = min(d.section_80tta, LIMIT_80TTA)
    c24b = min(d.section_24b, LIMIT_24B)
    emp_nps = min(profile.employer_nps, s.basic_salary * 0.10)

    total_ded = c80c + c80ccd + c80d + c80e + c80g + c80tta + c24b + emp_nps
    taxable = max(0, gti - total_ded)

    base_tax, slab_br = _slab_tax(taxable, OLD_REGIME_SLABS)
    rebate = min(base_tax, OLD_87A_MAX) if taxable <= OLD_87A_LIMIT else 0
    after_rebate = max(0, base_tax - rebate)
    sc = _surcharge(after_rebate, taxable, False)
    cess_amt = round((after_rebate + sc) * CESS)
    total_tax = after_rebate + sc + cess_amt

    breakdown = {
        "gross_salary": s.gross_salary,
        "hra_exemption": hra_exempt,
        "standard_deduction": std,
        "professional_tax": prof_tax,
        "income_from_salary": income_salary,
        "other_income": s.other_income,
        "gross_total_income": gti,
        "deductions": {
            "80C": c80c, "80CCD(1B)": c80ccd, "80D": c80d,
            "80E": c80e, "80G": c80g, "80TTA": c80tta,
            "24(b)": c24b, "80CCD(2)_employer": emp_nps,
            "total": total_ded,
        },
        "taxable_income": taxable,
        "slab_breakdown": slab_br,
        "base_tax": base_tax,
        "rebate_87a": rebate,
        "tax_after_rebate": after_rebate,
        "surcharge": sc,
        "cess": cess_amt,
        "total_tax": total_tax,
    }
    return total_tax, taxable, breakdown


# ===================================================================
# NEW REGIME
# ===================================================================


def compute_new_regime(profile: TaxProfile) -> Tuple[float, float, Dict[str, Any]]:
    s = profile.salary

    std = min(NEW_STD_DEDUCTION, s.gross_salary)
    prof_tax = s.professional_tax
    income_salary = max(0, s.gross_salary - std - prof_tax)
    gti = income_salary + s.other_income

    emp_nps = min(profile.employer_nps, s.basic_salary * 0.14)
    taxable = max(0, gti - emp_nps)

    base_tax, slab_br = _slab_tax(taxable, NEW_REGIME_SLABS)
    rebate = min(base_tax, NEW_87A_MAX) if taxable <= NEW_87A_LIMIT else 0
    after_rebate = max(0, base_tax - rebate)

    # Marginal relief
    if taxable > NEW_87A_LIMIT:
        excess = taxable - NEW_87A_LIMIT
        if after_rebate > excess:
            after_rebate = round(excess)

    sc = _surcharge(after_rebate, taxable, True)
    cess_amt = round((after_rebate + sc) * CESS)
    total_tax = after_rebate + sc + cess_amt

    breakdown = {
        "gross_salary": s.gross_salary,
        "standard_deduction": std,
        "professional_tax": prof_tax,
        "income_from_salary": income_salary,
        "other_income": s.other_income,
        "gross_total_income": gti,
        "employer_nps_deduction": emp_nps,
        "taxable_income": taxable,
        "slab_breakdown": slab_br,
        "base_tax": base_tax,
        "rebate_87a": rebate,
        "tax_after_rebate": after_rebate,
        "surcharge": sc,
        "cess": cess_amt,
        "total_tax": total_tax,
    }
    return total_tax, taxable, breakdown


# ===================================================================
# COMPARISON
# ===================================================================


def compare_regimes(profile: TaxProfile) -> TaxComparison:
    old_tax, old_ti, old_br = compute_old_regime(profile)
    new_tax, new_ti, new_br = compute_new_regime(profile)

    if old_tax <= new_tax:
        rec, sav = "old", new_tax - old_tax
    else:
        rec, sav = "new", old_tax - new_tax

    return TaxComparison(
        old_regime_tax=old_tax,
        new_regime_tax=new_tax,
        old_regime_taxable_income=old_ti,
        new_regime_taxable_income=new_ti,
        recommended_regime=rec,
        savings_amount=sav,
        old_regime_breakdown=old_br,
        new_regime_breakdown=new_br,
    )


# ===================================================================
# MISSED DEDUCTIONS
# ===================================================================


def _marginal_rate(profile: TaxProfile) -> float:
    _, ti, _ = compute_old_regime(profile)
    if ti > 1_000_000:
        return 0.312  # 30% + 4% cess
    if ti > 500_000:
        return 0.2080  # 20% + 4% cess
    if ti > 250_000:
        return 0.052  # 5% + 4% cess
    return 0.0


def find_missed_deductions(profile: TaxProfile) -> List[MissedDeduction]:
    missed: List[MissedDeduction] = []
    s = profile.salary
    d = profile.deductions
    mr = _marginal_rate(profile)
    if mr == 0:
        return missed

    total_80c = d.section_80c + s.epf_employee
    if total_80c < LIMIT_80C:
        gap = LIMIT_80C - total_80c
        missed.append(MissedDeduction(
            section="80C", name="Section 80C Investment",
            description=f"Invest ₹{gap:,.0f} more in ELSS/PPF/NPS Tier-I to use full ₹1.5L limit.",
            max_limit=LIMIT_80C, currently_claimed=total_80c,
            potential_saving=round(gap * mr),
            priority="high" if gap > 50_000 else "medium",
        ))

    if d.section_80ccd_1b < LIMIT_80CCD1B:
        gap = LIMIT_80CCD1B - d.section_80ccd_1b
        missed.append(MissedDeduction(
            section="80CCD(1B)", name="NPS Contribution",
            description=f"Invest ₹{gap:,.0f} in NPS for additional deduction beyond 80C.",
            max_limit=LIMIT_80CCD1B, currently_claimed=d.section_80ccd_1b,
            potential_saving=round(gap * mr), priority="high",
        ))

    max_80d = LIMIT_80D_SELF_SR if profile.age >= 60 else LIMIT_80D_SELF
    if d.section_80d < max_80d:
        gap = max_80d - d.section_80d
        missed.append(MissedDeduction(
            section="80D", name="Health Insurance Premium",
            description=f"Health insurance premium up to ₹{max_80d:,.0f} (self). Parents: additional ₹{LIMIT_80D_PARENTS:,.0f}.",
            max_limit=max_80d + LIMIT_80D_PARENTS,
            currently_claimed=d.section_80d,
            potential_saving=round(gap * mr), priority="high",
        ))

    if s.hra_received > 0 and profile.rent_paid == 0:
        est = round(s.hra_received * 0.4)
        missed.append(MissedDeduction(
            section="10(13A)", name="HRA Exemption",
            description="You receive HRA but no rent is recorded. Submit rent receipts to claim HRA exemption.",
            max_limit=s.hra_received, currently_claimed=0,
            potential_saving=round(est * mr), priority="high",
        ))

    if profile.has_home_loan and d.section_24b < LIMIT_24B:
        gap = LIMIT_24B - d.section_24b
        missed.append(MissedDeduction(
            section="24(b)", name="Home Loan Interest",
            description=f"Claim up to ₹{LIMIT_24B:,.0f} home loan interest deduction.",
            max_limit=LIMIT_24B, currently_claimed=d.section_24b,
            potential_saving=round(min(gap, 100_000) * mr), priority="medium",
        ))

    if d.section_80tta < LIMIT_80TTA:
        gap = LIMIT_80TTA - d.section_80tta
        missed.append(MissedDeduction(
            section="80TTA", name="Savings Account Interest",
            description=f"Savings account interest up to ₹{LIMIT_80TTA:,.0f} is deductible.",
            max_limit=LIMIT_80TTA, currently_claimed=d.section_80tta,
            potential_saving=round(gap * mr), priority="low",
        ))

    missed.sort(key=lambda x: x.potential_saving, reverse=True)
    return missed


def total_savings(missed: List[MissedDeduction]) -> float:
    return round(sum(m.potential_saving for m in missed))
