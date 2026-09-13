"""
API routes for Portfolio X-Ray (CAMS upload + analysis).
"""

from fastapi import APIRouter, UploadFile, File, HTTPException
from core.portfolio_schemas import (
    PortfolioXRay, CAMSUploadResponse, OverlapAlert, RebalancingAction
)
from core.financial_models import (
    calculate_simple_cagr,
    detect_fund_overlap,
    get_overlap_alerts,
    calculate_expense_ratio_drag,
    benchmark_comparison,
    generate_rebalancing_plan,
)
from services.cams_parser import parse_cams_statement

router = APIRouter()


@router.post("/upload-cams", response_model=CAMSUploadResponse)
async def upload_cams(file: UploadFile = File(...)):
    """Upload CAMS/KFintech PDF → parse → return structured portfolio data."""
    if not file.filename or not file.filename.lower().endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files accepted.")

    pdf_bytes = await file.read()
    if len(pdf_bytes) > 15 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 15MB).")
    if len(pdf_bytes) < 100:
        raise HTTPException(status_code=400, detail="File appears empty or corrupted.")

    try:
        portfolio = parse_cams_statement(pdf_bytes)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Parsing failed: {str(e)}")

    return CAMSUploadResponse(
        success=True,
        portfolio=portfolio,
        message=f"Parsed {len(portfolio.holdings)} fund holdings successfully.",
    )


@router.post("/analyze-portfolio", response_model=PortfolioXRay)
async def analyze_portfolio(portfolio_data: dict):
    """
    Full portfolio analysis: XIRR, overlap, expense drag, rebalancing.
    Accepts portfolio JSON (output from /upload-cams).
    """
    from core.portfolio_schemas import PortfolioData, MutualFundHolding

    try:
        holdings_raw = portfolio_data.get("holdings", [])
        holdings = [MutualFundHolding(**h) for h in holdings_raw]
        total_current = sum(h.current_value for h in holdings)
        total_invested = sum(h.invested_amount for h in holdings)
        portfolio = PortfolioData(
            holdings=holdings,
            total_current_value=total_current,
            total_invested=total_invested,
        )
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid portfolio data: {str(e)}")

    holdings_dicts = [h.model_dump() for h in holdings]

    # XIRR / simple CAGR
    portfolio_xirr = None
    if total_invested > 0 and total_current > 0:
        # Rough CAGR assuming 3-year average holding
        portfolio_xirr = calculate_simple_cagr(total_invested, total_current, 3)

    # Per-fund XIRR
    for h in holdings:
        if h.invested_amount > 0 and h.current_value > 0:
            h.xirr = calculate_simple_cagr(h.invested_amount, h.current_value, 3)
    holdings_dicts = [h.model_dump() for h in holdings]

    # Overlap
    fund_names = [h.name for h in holdings]
    overlap_matrix = detect_fund_overlap(fund_names) if len(fund_names) > 1 else {}
    raw_alerts = get_overlap_alerts(overlap_matrix) if overlap_matrix else []
    overlap_alerts = [OverlapAlert(**a) for a in raw_alerts]

    # Expense drag
    expense_drag = calculate_expense_ratio_drag(holdings_dicts)

    # Benchmark
    bench = benchmark_comparison(holdings_dicts)
    portfolio_xirr = bench.get("portfolio_xirr", portfolio_xirr)
    alpha = bench.get("alpha")

    # Rebalancing
    raw_rebal = generate_rebalancing_plan(holdings_dicts)
    rebalancing_plan = [RebalancingAction(**r) for r in raw_rebal]

    # Summary
    summary_parts = []
    if portfolio_xirr is not None:
        summary_parts.append(
            f"Your portfolio has returned ~{portfolio_xirr:.1f}% CAGR"
        )
    if bench.get("outperforming"):
        summary_parts.append(f"outperforming NIFTY 50 by {abs(alpha):.1f}%")
    elif alpha is not None:
        summary_parts.append(f"underperforming NIFTY 50 by {abs(alpha):.1f}%")
    if overlap_alerts:
        summary_parts.append(
            f"{len(overlap_alerts)} fund pairs have high overlap — consider consolidating"
        )
    if expense_drag.get("total_annual_drag", 0) > 0:
        summary_parts.append(
            f"you're paying ₹{expense_drag['total_annual_drag']:,.0f}/year in excess fees"
        )

    summary = ". ".join(summary_parts) + "." if summary_parts else "Portfolio analysis complete."

    return PortfolioXRay(
        portfolio=portfolio,
        portfolio_xirr=portfolio_xirr,
        nifty50_return=12.5,
        alpha=alpha,
        overlap_matrix=overlap_matrix,
        overlap_alerts=overlap_alerts,
        expense_drag=expense_drag,
        rebalancing_plan=rebalancing_plan,
        summary=summary,
    )
