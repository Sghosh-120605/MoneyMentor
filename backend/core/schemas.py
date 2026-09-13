"""Pydantic data models for MoneyMentor AI."""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum


class TaxRegime(str, Enum):
    OLD = "old"
    NEW = "new"


class SalaryComponents(BaseModel):
    gross_salary: float = Field(0, description="Total gross salary")
    basic_salary: float = Field(0, description="Basic salary component")
    hra_received: float = Field(0, description="HRA received from employer")
    special_allowance: float = Field(0, description="Special allowance")
    lta: float = Field(0, description="Leave Travel Allowance")
    professional_tax: float = Field(0, description="Professional tax paid")
    epf_employee: float = Field(0, description="Employee EPF contribution")
    other_income: float = Field(0, description="Any other income")


class DeductionsClaimed(BaseModel):
    section_80c: float = Field(0, description="80C deductions (EPF, PPF, ELSS, LIC, etc.)")
    section_80ccd_1b: float = Field(0, description="80CCD(1B) NPS contribution")
    section_80d: float = Field(0, description="80D health insurance premium")
    section_80e: float = Field(0, description="80E education loan interest")
    section_80g: float = Field(0, description="80G donations")
    section_80tta: float = Field(0, description="80TTA savings account interest")
    section_24b: float = Field(0, description="Section 24(b) home loan interest")
    hra_exemption: float = Field(0, description="HRA exemption claimed")


class TaxProfile(BaseModel):
    salary: SalaryComponents = Field(default_factory=SalaryComponents)
    deductions: DeductionsClaimed = Field(default_factory=DeductionsClaimed)
    rent_paid: float = Field(0, description="Annual rent paid")
    is_metro: bool = Field(True, description="Metro city (Delhi/Mumbai/Kolkata/Chennai)")
    tds_deducted: float = Field(0, description="TDS already deducted")
    age: int = Field(30, description="Age of taxpayer")
    has_health_insurance: bool = Field(False)
    has_nps: bool = Field(False)
    has_home_loan: bool = Field(False)
    employer_nps: float = Field(0, description="Employer NPS contribution 80CCD(2)")


class TaxComparison(BaseModel):
    old_regime_tax: float
    new_regime_tax: float
    old_regime_taxable_income: float
    new_regime_taxable_income: float
    recommended_regime: TaxRegime
    savings_amount: float
    old_regime_breakdown: Dict[str, Any]
    new_regime_breakdown: Dict[str, Any]


class MissedDeduction(BaseModel):
    section: str
    name: str
    description: str
    max_limit: float
    currently_claimed: float
    potential_saving: float
    priority: str  # high, medium, low


class ActionItem(BaseModel):
    action: str
    saving_amount: float
    deadline: str
    difficulty: str  # easy, medium, hard
    explanation: str


class TaxAnalysisResult(BaseModel):
    tax_profile: TaxProfile
    comparison: TaxComparison
    missed_deductions: List[MissedDeduction]
    action_plan: List[ActionItem]
    total_potential_savings: float
    summary: str


class UploadResponse(BaseModel):
    success: bool
    tax_profile: Optional[TaxProfile] = None
    message: str
    raw_extracted: Optional[Dict[str, Any]] = None


class AnalysisRequest(BaseModel):
    tax_profile: TaxProfile
    rent_paid: float = 0
    is_metro: bool = True
    age: int = 30
    has_health_insurance: bool = False
    has_nps: bool = False
    has_home_loan: bool = False


class ErrorResponse(BaseModel):
    success: bool = False
    error: str
    detail: Optional[str] = None
