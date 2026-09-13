"""
Proactive Alerts routes — personalized policy/market event alerts.
"""

from fastapi import APIRouter
from typing import List, Optional
from core.portfolio_schemas import ProactiveAlert, AlertSeverity

router = APIRouter()


# ===================================================================
# SIMULATED POLICY EVENTS DATABASE
# ===================================================================

POLICY_EVENTS = [
    {
        "id": "rbi_rate_cut_feb25",
        "title": "RBI Repo Rate Cut — Feb 2025",
        "event_type": "rbi_rate",
        "base_impact_summary": "RBI reduced repo rate by 25 bps to 6.25%. Home loan EMIs set to fall.",
        "severity": "high",
        "source": "RBI Monetary Policy Committee",
        "deadline": "Renegotiate loan by June 2026",
    },
    {
        "id": "budget25_nps_change",
        "title": "Budget 2025: NPS Section 80CCD(2) Enhanced",
        "event_type": "budget",
        "base_impact_summary": "Employer NPS contribution deduction raised from 10% to 14% of basic salary under New Regime.",
        "severity": "medium",
        "source": "Union Budget 2025-26",
        "deadline": "Verify with HR for FY 2025-26",
    },
    {
        "id": "budget25_tds_threshold",
        "title": "Budget 2025: TDS Threshold Raised",
        "event_type": "budget",
        "base_impact_summary": "TDS on FD interest threshold raised from ₹40,000 to ₹50,000 for regular citizens.",
        "severity": "low",
        "source": "Union Budget 2025-26",
        "deadline": None,
    },
    {
        "id": "sebi_mf_recat_2024",
        "title": "SEBI MF Recategorisation — Small Cap Limits",
        "event_type": "sebi",
        "base_impact_summary": "SEBI has tightened small-cap allocation limits. Funds may rebalance holdings, affecting NAVs.",
        "severity": "medium",
        "source": "SEBI Circular",
        "deadline": None,
    },
    {
        "id": "new_regime_default_fy26",
        "title": "New Tax Regime — Default from FY 2025-26",
        "event_type": "budget",
        "base_impact_summary": "New Tax Regime is now the default. Employees must actively opt for Old Regime with employer.",
        "severity": "high",
        "source": "Finance Act 2023",
        "deadline": "April 1, 2026 (start of new TDS cycle)",
    },
    {
        "id": "elss_lock_in_clarity",
        "title": "ELSS Clarity: 3-Year Lock-In Per SIP Instalment",
        "event_type": "sebi",
        "base_impact_summary": "SEBI clarified that each ELSS SIP instalment has its own 3-year lock-in, not the first investment date.",
        "severity": "low",
        "source": "SEBI FAQ",
        "deadline": None,
    },
    {
        "id": "section87a_rebate_confusion",
        "title": "Section 87A Rebate — New Regime ₹12L Zero Tax",
        "event_type": "budget",
        "base_impact_summary": "Under New Regime, taxable income up to ₹12L attracts zero income tax due to ₹60,000 rebate u/s 87A.",
        "severity": "high",
        "source": "Union Budget 2025-26",
        "deadline": "File ITR by July 31, 2026",
    },
]


def _personalise_alert(
    event: dict,
    annual_income: float = 0,
    has_home_loan: bool = False,
    has_nps: bool = False,
    monthly_emi: float = 0,
    portfolio_value: float = 0,
) -> Optional[ProactiveAlert]:
    """Add personalised impact to a policy event."""
    eid = event["id"]
    personal_impact = ""
    savings = 0.0

    if eid == "rbi_rate_cut_feb25":
        if not has_home_loan:
            return None  # Not relevant
        emi_saving = round(monthly_emi * 0.025)  # ~2.5% EMI reduction
        personal_impact = f"Your EMI may reduce by ~₹{emi_saving:,}/month. Ask your bank to reset rate."
        savings = emi_saving * 12

    elif eid == "budget25_nps_change":
        if not has_nps:
            personal_impact = "Start NPS now — you can claim up to 14% of basic salary as employer contribution deduction."
            savings = min(annual_income * 0.04 * 0.312, 50_000)
        else:
            personal_impact = "Ask your HR to increase employer NPS contribution from 10% to 14% of basic."
            savings = round(annual_income * 0.04 * 0.312 / 12)  # Rough

    elif eid == "budget25_tds_threshold":
        personal_impact = "Check if your FD interest now falls below ₹50,000 — you may not need to submit Form 15G."
        savings = annual_income * 0.001  # Minimal

    elif eid == "sebi_mf_recat_2024":
        if portfolio_value <= 0:
            return None
        personal_impact = f"Review your small-cap holdings. Your portfolio of ₹{portfolio_value:,.0f} may see NAV impacts."
        savings = 0

    elif eid == "new_regime_default_fy26":
        personal_impact = "Submit your regime preference to HR before April 1. Wrong default = higher TDS all year."
        savings = round(annual_income * 0.02)  # Wrong regime can cost ~2%

    elif eid == "elss_lock_in_clarity":
        if portfolio_value <= 0:
            return None
        personal_impact = "Each ELSS SIP instalment matures 3 years from its investment date — stagger redemptions accordingly."
        savings = 0

    elif eid == "section87a_rebate_confusion":
        if annual_income > 1_500_000:
            return None  # Not relevant for high income
        if annual_income <= 1_200_000:
            personal_impact = "Great news — your income may qualify for zero tax under New Regime! Verify with your CA."
            savings = round(annual_income * 0.05)  # Approximate
        else:
            personal_impact = "You're just above the ₹12L threshold. Check if deductions under Old Regime save more."
            savings = 0

    else:
        personal_impact = event.get("base_impact_summary", "")

    return ProactiveAlert(
        id=eid,
        title=event["title"],
        event_type=event["event_type"],
        impact_summary=event["base_impact_summary"],
        personal_impact=personal_impact or event["base_impact_summary"],
        action_required=event.get("deadline", "Review and take action") or "Review and take action",
        potential_saving_or_impact=savings,
        severity=AlertSeverity(event["severity"]),
        deadline=event.get("deadline"),
        source=event.get("source", "Policy Update"),
    )


@router.get("/alerts", response_model=List[ProactiveAlert])
async def get_alerts(
    annual_income: float = 0,
    has_home_loan: bool = False,
    has_nps: bool = False,
    monthly_emi: float = 0,
    portfolio_value: float = 0,
):
    """
    Return personalised proactive alerts based on user's financial profile.
    Pass query params to filter and personalise alerts.
    """
    alerts = []
    for event in POLICY_EVENTS:
        alert = _personalise_alert(
            event,
            annual_income=annual_income,
            has_home_loan=has_home_loan,
            has_nps=has_nps,
            monthly_emi=monthly_emi,
            portfolio_value=portfolio_value,
        )
        if alert:
            alerts.append(alert)

    # Sort: high first, then by savings impact
    severity_order = {"high": 0, "medium": 1, "low": 2}
    alerts.sort(key=lambda a: (severity_order.get(a.severity, 3), -a.potential_saving_or_impact))

    return alerts
