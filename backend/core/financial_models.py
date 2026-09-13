"""
Financial models for MoneyMentor AI.
XIRR, fund overlap detection, expense ratio drag, benchmark comparison, portfolio metrics.
"""

from typing import List, Dict, Tuple, Optional
import math
from datetime import date, datetime


# ===================================================================
# DATA STRUCTURES (dicts for simplicity — schemas in schemas.py)
# ===================================================================


# Expense ratios for direct vs regular plans (approx industry averages)
CATEGORY_EXPENSE_RATIOS = {
    "large_cap": {"regular": 1.50, "direct": 0.80},
    "mid_cap": {"regular": 1.80, "direct": 0.90},
    "small_cap": {"regular": 2.00, "direct": 1.00},
    "flexi_cap": {"regular": 1.60, "direct": 0.85},
    "index": {"regular": 0.50, "direct": 0.20},
    "elss": {"regular": 1.70, "direct": 0.90},
    "debt": {"regular": 0.80, "direct": 0.30},
    "liquid": {"regular": 0.25, "direct": 0.10},
    "hybrid": {"regular": 1.40, "direct": 0.75},
    "unknown": {"regular": 1.50, "direct": 0.75},
}

NIFTY50_ANNUAL_RETURN = 12.5  # 10-year CAGR approximation


# ===================================================================
# XIRR — Newton-Raphson Method
# ===================================================================


def _xirr_npv(rate: float, cashflows: List[float], days: List[int]) -> float:
    """Net Present Value for given rate."""
    return sum(cf / (1 + rate) ** (d / 365.0) for cf, d in zip(cashflows, days))


def _xirr_dnpv(rate: float, cashflows: List[float], days: List[int]) -> float:
    """Derivative of NPV — for Newton-Raphson."""
    return sum(
        -cf * (d / 365.0) / (1 + rate) ** (d / 365.0 + 1)
        for cf, d in zip(cashflows, days)
    )


def calculate_xirr(
    cashflows: List[float],
    dates: List[date],
    guess: float = 0.10,
    max_iter: int = 100,
    tol: float = 1e-6,
) -> Optional[float]:
    """
    Calculate XIRR (Extended Internal Rate of Return).
    cashflows: negative = investment (outflow), positive = redemption/current value
    dates: corresponding dates
    Returns annualised return as a decimal (e.g., 0.13 = 13%).
    """
    if not cashflows or not dates or len(cashflows) != len(dates):
        return None
    if not any(cf < 0 for cf in cashflows) or not any(cf > 0 for cf in cashflows):
        return None

    base_date = min(dates)
    days = [(d - base_date).days for d in dates]

    rate = guess
    for _ in range(max_iter):
        npv = _xirr_npv(rate, cashflows, days)
        dnpv = _xirr_dnpv(rate, cashflows, days)
        if abs(dnpv) < 1e-12:
            break
        new_rate = rate - npv / dnpv
        if abs(new_rate - rate) < tol:
            return round(new_rate * 100, 2)
        rate = new_rate
        # Keep rate bounded to avoid divergence
        if rate < -0.999:
            rate = -0.999
        if rate > 100:
            break

    return round(rate * 100, 2)


def calculate_simple_cagr(
    invested: float, current_value: float, years: float
) -> Optional[float]:
    """Simple CAGR when exact cash flow dates are unavailable."""
    if invested <= 0 or current_value <= 0 or years <= 0:
        return None
    return round(((current_value / invested) ** (1 / years) - 1) * 100, 2)


# ===================================================================
# FUND OVERLAP DETECTION
# ===================================================================

# Sample top holdings for popular funds (ISIN — company name)
# In production this would come from AMFI/Morningstar. Here we use representative data.
FUND_HOLDINGS_DB: Dict[str, List[str]] = {
    "HDFC Top 100": [
        "HDFCBANK", "RELIANCE", "ICICIBANK", "INFY", "TCS",
        "BHARTIARTL", "AXISBANK", "KOTAKBANK", "LT", "SBIN",
    ],
    "ICICI Pru Bluechip": [
        "HDFCBANK", "ICICIBANK", "RELIANCE", "INFY", "BHARTIARTL",
        "TCS", "KOTAKBANK", "MARUTI", "AXISBANK", "TITAN",
    ],
    "SBI Bluechip": [
        "HDFCBANK", "RELIANCE", "ICICIBANK", "INFY", "TCS",
        "BHARTIARTL", "KOTAKBANK", "AXISBANK", "HINDUNILVR", "LT",
    ],
    "Mirae Asset Large Cap": [
        "HDFCBANK", "RELIANCE", "ICICIBANK", "INFY", "TCS",
        "AXISBANK", "BHARTIARTL", "KOTAKBANK", "TITAN", "MARUTI",
    ],
    "Parag Parikh Flexi Cap": [
        "BAJFINANCE", "HDFCBANK", "ICICIBANK", "ITC", "POWERGRID",
        "COALINDIA", "INFY", "PIRAMALENT", "MARCBENZ", "ALPHABET",
    ],
    "Axis Bluechip": [
        "HDFCBANK", "INFY", "TCS", "BAJFINANCE", "ICICIBANK",
        "BHARTIARTL", "KOTAKBANK", "TITAN", "ASIANPAINT", "ULTRACEMCO",
    ],
    "Nippon India Large Cap": [
        "HDFCBANK", "RELIANCE", "ICICIBANK", "TCS", "INFY",
        "BHARTIARTL", "KOTAKBANK", "AXISBANK", "MARUTI", "BAJFINANCE",
    ],
    "UTI Nifty 50 Index": [
        "HDFCBANK", "RELIANCE", "ICICIBANK", "INFY", "TCS",
        "BHARTIARTL", "KOTAKBANK", "AXISBANK", "LT", "HINDUNILVR",
    ],
}


def detect_fund_overlap(fund_names: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Detect overlap between funds based on their top holdings.
    Returns a matrix of overlap percentages.
    """
    overlap_matrix: Dict[str, Dict[str, float]] = {}

    for i, fund_a in enumerate(fund_names):
        overlap_matrix[fund_a] = {}
        holdings_a = set(FUND_HOLDINGS_DB.get(fund_a, []))

        for j, fund_b in enumerate(fund_names):
            if i == j:
                overlap_matrix[fund_a][fund_b] = 100.0
                continue

            holdings_b = set(FUND_HOLDINGS_DB.get(fund_b, []))
            if not holdings_a or not holdings_b:
                # Estimate overlap by category similarity
                overlap_matrix[fund_a][fund_b] = 40.0  # Unknown — assume moderate
                continue

            intersection = holdings_a & holdings_b
            union = holdings_a | holdings_b
            jaccard = len(intersection) / len(union)
            # Scale to percentage of common holdings
            pct = round(len(intersection) / max(len(holdings_a), len(holdings_b)) * 100, 1)
            overlap_matrix[fund_a][fund_b] = pct

    return overlap_matrix


def get_overlap_alerts(overlap_matrix: Dict[str, Dict[str, float]]) -> List[Dict]:
    """Identify fund pairs with high overlap (>50%) — signals redundancy."""
    alerts = []
    seen = set()
    for fund_a, row in overlap_matrix.items():
        for fund_b, pct in row.items():
            if fund_a == fund_b:
                continue
            pair = tuple(sorted([fund_a, fund_b]))
            if pair in seen:
                continue
            seen.add(pair)
            if pct >= 50:
                alerts.append({
                    "fund_a": fund_a,
                    "fund_b": fund_b,
                    "overlap_pct": pct,
                    "severity": "high" if pct >= 70 else "medium",
                    "message": f"{fund_a} and {fund_b} share {pct:.0f}% of top holdings — consider consolidating.",
                })
    return sorted(alerts, key=lambda x: -x["overlap_pct"])


# ===================================================================
# EXPENSE RATIO DRAG
# ===================================================================


def calculate_expense_ratio_drag(
    holdings: List[Dict],  # [{name, current_value, plan_type, category}]
    years: int = 10,
) -> Dict:
    """
    Calculate the annual + 10-year cost of regular vs direct plans.
    Returns drag amount in ₹ and recommendations.
    """
    total_value = sum(h.get("current_value", 0) for h in holdings)
    annual_drag = 0.0
    details = []

    for h in holdings:
        val = h.get("current_value", 0)
        cat = h.get("category", "unknown").lower().replace(" ", "_")
        plan = h.get("plan_type", "regular").lower()

        ratios = CATEGORY_EXPENSE_RATIOS.get(cat, CATEGORY_EXPENSE_RATIOS["unknown"])
        current_er = ratios.get(plan, ratios["regular"])
        direct_er = ratios["direct"]
        saving_pct = max(0, current_er - direct_er)
        annual_saving = val * saving_pct / 100

        if plan != "direct" and annual_saving > 0:
            annual_drag += annual_saving
            details.append({
                "fund": h.get("name", "Unknown Fund"),
                "current_value": val,
                "current_er": current_er,
                "direct_er": direct_er,
                "annual_saving": round(annual_saving),
                "ten_year_saving": round(annual_saving * years),
            })

    # Compound effect over years
    ten_year_drag = round(annual_drag * years)

    return {
        "total_portfolio_value": round(total_value),
        "total_annual_drag": round(annual_drag),
        "total_ten_year_drag": ten_year_drag,
        "regular_plan_funds": len(details),
        "details": sorted(details, key=lambda x: -x["annual_saving"]),
        "tip": f"Switching to direct plans saves ₹{annual_drag:,.0f}/year — ₹{ten_year_drag:,.0f} over 10 years.",
    }


# ===================================================================
# BENCHMARK COMPARISON
# ===================================================================


def benchmark_comparison(holdings: List[Dict]) -> Dict:
    """
    Compare portfolio returns vs NIFTY 50 benchmark.
    holdings: [{name, xirr, current_value, category}]
    """
    if not holdings:
        return {}

    total_value = sum(h.get("current_value", 0) for h in holdings)
    weighted_xirr = sum(
        h.get("xirr", 0) * h.get("current_value", 0)
        for h in holdings
        if h.get("xirr") is not None
    ) / max(total_value, 1)

    alpha = round(weighted_xirr - NIFTY50_ANNUAL_RETURN, 2)

    return {
        "portfolio_xirr": round(weighted_xirr, 2),
        "nifty50_return": NIFTY50_ANNUAL_RETURN,
        "alpha": alpha,
        "outperforming": alpha > 0,
        "message": (
            f"Your portfolio returned {weighted_xirr:.1f}% vs NIFTY 50's {NIFTY50_ANNUAL_RETURN}% — "
            f"{'outperforming' if alpha > 0 else 'underperforming'} by {abs(alpha):.1f}%."
        ),
    }


# ===================================================================
# REBALANCING RECOMMENDATIONS
# ===================================================================


def generate_rebalancing_plan(
    holdings: List[Dict],
    target_allocation: Optional[Dict] = None,
) -> List[Dict]:
    """
    Generate buy/sell recommendations to reach target allocation.
    holdings: [{name, current_value, category}]
    target_allocation: {category: target_pct} — defaults to age-based if None
    """
    if not holdings:
        return []

    total_value = sum(h.get("current_value", 0) for h in holdings)
    if total_value == 0:
        return []

    # Current allocation by category
    current: Dict[str, float] = {}
    for h in holdings:
        cat = h.get("category", "equity")
        current[cat] = current.get(cat, 0) + h.get("current_value", 0)

    current_pct = {k: round(v / total_value * 100, 1) for k, v in current.items()}

    if target_allocation is None:
        # Default balanced target
        target_allocation = {"equity": 60.0, "debt": 30.0, "gold": 10.0}

    recommendations = []
    for cat, target_pct in target_allocation.items():
        current_p = current_pct.get(cat, 0)
        diff = target_pct - current_p
        diff_value = round(diff * total_value / 100)

        if abs(diff) >= 5:  # Only suggest if difference is meaningful
            recommendations.append({
                "category": cat,
                "current_pct": current_p,
                "target_pct": target_pct,
                "action": "buy" if diff > 0 else "sell",
                "amount": abs(diff_value),
                "message": (
                    f"{'Add' if diff > 0 else 'Reduce'} ₹{abs(diff_value):,.0f} in {cat} funds "
                    f"(currently {current_p:.0f}%, target {target_pct:.0f}%)."
                ),
            })

    return recommendations


# ===================================================================
# MONEY HEALTH SCORING
# ===================================================================


def score_emergency_fund(monthly_expenses: float, emergency_fund: float) -> Dict:
    """Score emergency fund adequacy (0-100). 6 months = 100."""
    if monthly_expenses <= 0:
        return {"score": 50, "months_covered": 0, "target_months": 6}
    months = emergency_fund / monthly_expenses
    score = min(100, int(months / 6 * 100))
    return {
        "score": score,
        "months_covered": round(months, 1),
        "target_months": 6,
        "gap_amount": max(0, round(6 * monthly_expenses - emergency_fund)),
    }


def score_insurance_coverage(
    annual_income: float,
    life_cover: float,
    health_cover: float,
    dependants: int = 1,
) -> Dict:
    """Score insurance adequacy. Life = 10x income, Health = ₹5L+ min."""
    target_life = annual_income * 10
    target_health = max(500_000, dependants * 300_000)

    life_score = min(100, int(life_cover / target_life * 100)) if target_life > 0 else 0
    health_score = min(100, int(health_cover / target_health * 100))
    combined = int((life_score * 0.6 + health_score * 0.4))

    return {
        "score": combined,
        "life_cover": life_cover,
        "target_life_cover": target_life,
        "health_cover": health_cover,
        "target_health_cover": target_health,
        "life_gap": max(0, target_life - life_cover),
        "health_gap": max(0, target_health - health_cover),
    }


def score_diversification(holdings: List[Dict]) -> Dict:
    """Score portfolio diversification across asset classes (0-100)."""
    if not holdings:
        return {"score": 0, "asset_classes": {}}

    total = sum(h.get("current_value", 0) for h in holdings)
    if total == 0:
        return {"score": 0, "asset_classes": {}}

    cats: Dict[str, float] = {}
    for h in holdings:
        c = h.get("category", "equity")
        cats[c] = cats.get(c, 0) + h.get("current_value", 0) / total * 100

    # Ideal: equity 50-70%, debt 20-30%, gold 5-15%
    num_classes = len(cats)
    concentration = max(cats.values()) if cats else 100
    # Penalise over-concentration
    conc_score = max(0, 100 - max(0, concentration - 70) * 3)
    class_score = min(100, num_classes * 25)
    score = int((conc_score + class_score) / 2)

    return {
        "score": score,
        "asset_classes": {k: round(v, 1) for k, v in cats.items()},
        "largest_allocation": round(concentration, 1),
        "num_asset_classes": num_classes,
    }


def score_debt_health(
    annual_income: float,
    total_emi: float,
    interest_rates: List[float] = None,
) -> Dict:
    """Score debt health. EMI < 35% of income = good."""
    if annual_income <= 0:
        return {"score": 50, "dti_ratio": 0}

    monthly_income = annual_income / 12
    dti = total_emi / monthly_income * 100 if monthly_income > 0 else 0

    if dti <= 0:
        score = 100
    elif dti <= 20:
        score = 90
    elif dti <= 35:
        score = 70
    elif dti <= 50:
        score = 40
    else:
        score = 10

    avg_rate = sum(interest_rates) / len(interest_rates) if interest_rates else 0

    return {
        "score": score,
        "dti_ratio": round(dti, 1),
        "monthly_emi": round(total_emi),
        "monthly_income": round(monthly_income),
        "avg_interest_rate": round(avg_rate, 1),
        "status": "Good" if dti <= 35 else "High" if dti <= 50 else "Dangerous",
    }


def score_tax_efficiency(
    missed_deductions_count: int,
    total_potential_savings: float,
    annual_income: float,
) -> Dict:
    """Score tax efficiency based on missed deductions."""
    if annual_income <= 0:
        return {"score": 50}

    loss_pct = total_potential_savings / annual_income * 100
    if missed_deductions_count == 0:
        score = 100
    elif loss_pct <= 1:
        score = 80
    elif loss_pct <= 3:
        score = 60
    elif loss_pct <= 5:
        score = 40
    else:
        score = 20

    return {
        "score": score,
        "missed_count": missed_deductions_count,
        "annual_loss": round(total_potential_savings),
        "loss_pct_of_income": round(loss_pct, 1),
    }


def score_retirement_readiness(
    age: int,
    annual_income: float,
    current_corpus: float,
    monthly_sip: float,
    retirement_age: int = 60,
    expected_return: float = 10.0,
) -> Dict:
    """Score retirement readiness — projected vs required corpus."""
    years_to_retire = max(1, retirement_age - age)

    # Required corpus — 25x annual expenses (4% rule), expenses = 70% of income
    annual_expenses = annual_income * 0.70
    required_corpus = annual_expenses * 25  # Inflation-adjusted roughly

    # Project current corpus + SIP
    r_monthly = expected_return / 100 / 12
    sip_future = (
        monthly_sip * ((1 + r_monthly) ** (years_to_retire * 12) - 1) / r_monthly
        if r_monthly > 0 else monthly_sip * years_to_retire * 12
    )
    corpus_future = current_corpus * (1 + expected_return / 100) ** years_to_retire
    projected = corpus_future + sip_future

    pct_covered = min(100, projected / required_corpus * 100) if required_corpus > 0 else 0
    score = int(pct_covered)

    return {
        "score": score,
        "projected_corpus": round(projected),
        "required_corpus": round(required_corpus),
        "coverage_pct": round(pct_covered, 1),
        "years_to_retire": years_to_retire,
        "monthly_sip_required": round(
            (required_corpus - corpus_future) * r_monthly /
            ((1 + r_monthly) ** (years_to_retire * 12) - 1)
        ) if r_monthly > 0 and years_to_retire > 0 else 0,
    }


# ===================================================================
# FIRE PLANNER
# ===================================================================


def calculate_fire_plan(
    age: int,
    annual_income: float,
    annual_expenses: float,
    current_savings: float,
    monthly_sip: float,
    risk_appetite: str = "moderate",  # conservative, moderate, aggressive
    fire_age: int = 45,
) -> Dict:
    """
    Generate a FIRE (Financial Independence, Retire Early) plan.
    """
    years = max(1, fire_age - age)
    inflation = 0.06

    return_rates = {
        "conservative": {"equity": 0.09, "debt": 0.065, "gold": 0.07},
        "moderate": {"equity": 0.12, "debt": 0.07, "gold": 0.08},
        "aggressive": {"equity": 0.15, "debt": 0.065, "gold": 0.07},
    }.get(risk_appetite, {"equity": 0.12, "debt": 0.07, "gold": 0.08})

    # Inflation-adjusted target corpus (4% withdrawal rule)
    adj_expenses = annual_expenses * (1 + inflation) ** years
    target_corpus = adj_expenses * 25

    # Asset allocation glide path
    equity_pct = max(30, 100 - age - 10)  # Reduces as age increases
    debt_pct = max(20, 100 - equity_pct - 10)
    gold_pct = max(5, 100 - equity_pct - debt_pct)

    blended_return = (
        equity_pct / 100 * return_rates["equity"] +
        debt_pct / 100 * return_rates["debt"] +
        gold_pct / 100 * return_rates["gold"]
    )

    r_monthly = blended_return / 12
    months = years * 12

    # Projected corpus
    sip_fv = (
        monthly_sip * ((1 + r_monthly) ** months - 1) / r_monthly
        if r_monthly > 0 else monthly_sip * months
    )
    current_fv = current_savings * (1 + blended_return) ** years
    projected = current_fv + sip_fv

    shortfall = max(0, target_corpus - projected)

    # Required SIP to meet target
    required_sip = 0
    if shortfall > 0 and r_monthly > 0:
        required_sip = shortfall * r_monthly / ((1 + r_monthly) ** months - 1)

    # Monthly projections for chart (every 6 months)
    milestones = []
    for y in range(0, years + 1, 1):
        m = y * 12
        sip_v = (
            monthly_sip * ((1 + r_monthly) ** m - 1) / r_monthly
            if r_monthly > 0 and m > 0 else 0
        )
        corpus_v = current_savings * (1 + blended_return) ** y
        milestones.append({
            "year": age + y,
            "projected_corpus": round(corpus_v + sip_v),
            "target_line": round(target_corpus * (y / years) if years > 0 else target_corpus),
        })

    savings_rate = round((annual_income - annual_expenses) / annual_income * 100, 1) if annual_income > 0 else 0

    return {
        "fire_age": fire_age,
        "years_to_fire": years,
        "target_corpus": round(target_corpus),
        "projected_corpus": round(projected),
        "shortfall": round(shortfall),
        "monthly_sip_current": round(monthly_sip),
        "monthly_sip_required": round(required_sip),
        "blended_return_pct": round(blended_return * 100, 1),
        "asset_allocation": {
            "equity": equity_pct,
            "debt": debt_pct,
            "gold": gold_pct,
        },
        "savings_rate_pct": savings_rate,
        "adj_annual_expenses": round(adj_expenses),
        "milestones": milestones,
        "on_track": projected >= target_corpus * 0.9,
    }
