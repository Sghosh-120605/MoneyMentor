"""
Extended Pydantic schemas for MoneyMentor AI — Portfolio, Health, FIRE, Alerts.
Adds to existing tax schemas without modifying them.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


# ===================================================================
# PORTFOLIO / MUTUAL FUND SCHEMAS
# ===================================================================


class MutualFundHolding(BaseModel):
    name: str = Field(description="Fund scheme name")
    folio: str = Field(default="", description="Folio number")
    units: float = Field(default=0)
    nav: float = Field(default=0, description="Current NAV")
    current_value: float = Field(default=0)
    invested_amount: float = Field(default=0)
    category: str = Field(default="equity", description="large_cap/mid_cap/debt/etc")
    plan_type: str = Field(default="regular", description="direct/regular")
    xirr: Optional[float] = Field(default=None, description="Annualised return %")


class PortfolioData(BaseModel):
    holdings: List[MutualFundHolding] = Field(default_factory=list)
    total_current_value: float = Field(default=0)
    total_invested: float = Field(default=0)
    absolute_return_pct: Optional[float] = None


class OverlapAlert(BaseModel):
    fund_a: str
    fund_b: str
    overlap_pct: float
    severity: str
    message: str


class ExpenseRagDetail(BaseModel):
    fund: str
    current_value: float
    current_er: float
    direct_er: float
    annual_saving: float
    ten_year_saving: float


class RebalancingAction(BaseModel):
    category: str
    current_pct: float
    target_pct: float
    action: str  # buy/sell
    amount: float
    message: str


class PortfolioXRay(BaseModel):
    portfolio: PortfolioData
    portfolio_xirr: Optional[float] = None
    nifty50_return: float = 12.5
    alpha: Optional[float] = None
    overlap_matrix: Dict[str, Dict[str, float]] = Field(default_factory=dict)
    overlap_alerts: List[OverlapAlert] = Field(default_factory=list)
    expense_drag: Dict[str, Any] = Field(default_factory=dict)
    rebalancing_plan: List[RebalancingAction] = Field(default_factory=list)
    summary: str = ""


class CAMSUploadResponse(BaseModel):
    success: bool
    portfolio: Optional[PortfolioData] = None
    message: str
    raw_text_preview: Optional[str] = None


# ===================================================================
# HEALTH SCORE SCHEMAS
# ===================================================================


class HealthDimension(BaseModel):
    name: str
    score: int = Field(ge=0, le=100)
    details: Dict[str, Any] = Field(default_factory=dict)
    improvement_tip: str = ""


class HealthScoreResult(BaseModel):
    overall_score: int = Field(ge=0, le=100)
    dimensions: List[HealthDimension]
    grade: str  # A/B/C/D/F
    improvement_actions: List[Dict[str, Any]] = Field(default_factory=list)
    projected_score_after_actions: Optional[int] = None


class HealthScoreRequest(BaseModel):
    # Income & Expenses
    annual_income: float = Field(default=0)
    monthly_expenses: float = Field(default=0)
    # Emergency Fund
    emergency_fund: float = Field(default=0)
    # Insurance
    life_cover: float = Field(default=0)
    health_cover: float = Field(default=0)
    dependants: int = Field(default=1)
    # Investments (simplified)
    total_investments: float = Field(default=0)
    equity_pct: float = Field(default=0)
    debt_pct: float = Field(default=0)
    gold_pct: float = Field(default=0)
    # Debt
    monthly_emi: float = Field(default=0)
    avg_loan_rate: float = Field(default=0)
    # Tax
    missed_deductions_count: int = Field(default=0)
    tax_potential_savings: float = Field(default=0)
    # Retirement
    current_corpus: float = Field(default=0)
    monthly_sip: float = Field(default=0)
    age: int = Field(default=30)
    retirement_age: int = Field(default=60)


# ===================================================================
# FIRE PLANNER SCHEMAS
# ===================================================================


class FIRERequest(BaseModel):
    age: int = Field(default=30)
    annual_income: float = Field(default=0)
    annual_expenses: float = Field(default=0)
    current_savings: float = Field(default=0)
    monthly_sip: float = Field(default=0)
    risk_appetite: str = Field(default="moderate")  # conservative/moderate/aggressive
    fire_age: int = Field(default=45)


class FIREMilestone(BaseModel):
    year: int
    projected_corpus: float
    target_line: float


class FIREPlan(BaseModel):
    fire_age: int
    years_to_fire: int
    target_corpus: float
    projected_corpus: float
    shortfall: float
    monthly_sip_current: float
    monthly_sip_required: float
    blended_return_pct: float
    asset_allocation: Dict[str, float]
    savings_rate_pct: float
    adj_annual_expenses: float
    milestones: List[FIREMilestone]
    on_track: bool


# ===================================================================
# PROACTIVE ALERTS SCHEMAS
# ===================================================================


class AlertSeverity(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class ProactiveAlert(BaseModel):
    id: str
    title: str
    event_type: str  # rbi_rate/budget/sebi/market
    impact_summary: str
    personal_impact: str
    action_required: str
    potential_saving_or_impact: float = Field(default=0)
    severity: AlertSeverity
    deadline: Optional[str] = None
    source: str = "Policy Update"
