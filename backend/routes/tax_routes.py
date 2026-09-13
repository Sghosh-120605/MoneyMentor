"""API routes for MoneyMentor — Form 16 upload and tax analysis."""

from fastapi import APIRouter, UploadFile, File, HTTPException
from core.schemas import (
    TaxProfile, TaxAnalysisResult, UploadResponse,
    AnalysisRequest, ErrorResponse,
)
from core.tax_engine import compare_regimes, find_missed_deductions, total_savings
from services.parser import parse_form16
from services.ai_analyzer import generate_action_plan, generate_summary

router = APIRouter()


@router.post("/upload-form16", response_model=UploadResponse)
async def upload_form16(file: UploadFile = File(...)):
    """
    Upload a Form 16 PDF → parse → return structured tax profile.
    """
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are accepted.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 10 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large. Max 10MB.")
    if len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="File appears to be empty or corrupted.")

    try:
        profile = parse_form16(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    return UploadResponse(
        success=True,
        tax_profile=profile,
        message="Form 16 parsed successfully.",
        raw_extracted={
            "gross_salary": profile.salary.gross_salary,
            "basic_salary": profile.salary.basic_salary,
            "hra_received": profile.salary.hra_received,
            "epf_employee": profile.salary.epf_employee,
            "professional_tax": profile.salary.professional_tax,
            "section_80c": profile.deductions.section_80c,
            "section_80ccd_1b": profile.deductions.section_80ccd_1b,
            "section_80d": profile.deductions.section_80d,
            "tds_deducted": profile.tds_deducted,
        },
    )


@router.post("/analyze-tax", response_model=TaxAnalysisResult)
async def analyze_tax(request: AnalysisRequest):
    """
    Full tax analysis: comparison, missed deductions, action plan, summary.
    """
    profile = request.tax_profile
    profile.rent_paid = request.rent_paid
    profile.is_metro = request.is_metro
    profile.age = request.age
    profile.has_health_insurance = request.has_health_insurance
    profile.has_nps = request.has_nps
    profile.has_home_loan = request.has_home_loan

    try:
        comparison = compare_regimes(profile)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Tax calculation failed: {str(e)}")

    missed = find_missed_deductions(profile)
    savings = total_savings(missed)

    try:
        action_plan = generate_action_plan(profile, comparison, missed)
        summary = generate_summary(profile, comparison, missed, savings)
    except Exception as e:
        action_plan = []
        summary = (
            f"Based on your gross salary of ₹{profile.salary.gross_salary:,.0f}, "
            f"the {comparison.recommended_regime} regime saves you ₹{comparison.savings_amount:,.0f}. "
            f"You have {len(missed)} unused deductions worth ₹{savings:,.0f} in potential tax savings."
        )

    return TaxAnalysisResult(
        tax_profile=profile,
        comparison=comparison,
        missed_deductions=missed,
        action_plan=action_plan,
        total_potential_savings=savings,
        summary=summary,
    )


@router.post("/quick-analyze", response_model=TaxAnalysisResult)
async def quick_analyze(profile: TaxProfile):
    """
    Quick analysis from a manually entered tax profile (no PDF upload).
    Uses tax engine only — no AI call, faster response.
    """
    comparison = compare_regimes(profile)
    missed = find_missed_deductions(profile)
    savings = total_savings(missed)

    summary = (
        f"On a gross salary of ₹{profile.salary.gross_salary:,.0f}, "
        f"the {comparison.recommended_regime} regime saves you ₹{comparison.savings_amount:,.0f}. "
        f"You have {len(missed)} unused deductions worth ₹{savings:,.0f} in potential savings."
    )

    return TaxAnalysisResult(
        tax_profile=profile,
        comparison=comparison,
        missed_deductions=missed,
        action_plan=[],
        total_potential_savings=savings,
        summary=summary,
    )
