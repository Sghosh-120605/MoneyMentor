"""
Demo routes — pre-built realistic mock data for hackathon demos.
No OpenAI API key required. Returns complete, realistic results instantly.

Three demo personas:
  - sunita: Teacher, Delhi, ₹8L salary, simple portfolio
  - arjun:  Software Engineer, Bengaluru, ₹24L salary, aggressive portfolio
  - kavita: Business Owner, Mumbai, ₹50L salary, large portfolio
"""

from fastapi import APIRouter, HTTPException
from typing import Literal

router = APIRouter()

# ───────────────────────────────────────────────────────────────────────────────
# DEMO DATA
# ───────────────────────────────────────────────────────────────────────────────

DEMO_TAX = {
    "sunita": {
        "tax_profile": {
            "salary": {
                "gross_salary": 800000, "basic_salary": 320000, "hra_received": 128000,
                "special_allowance": 256000, "lta": 16000, "professional_tax": 2400,
                "epf_employee": 38400, "other_income": 12000,
            },
            "deductions": {
                "section_80c": 11600, "section_80ccd_1b": 0, "section_80d": 0,
                "section_80e": 0, "section_80g": 0, "section_80tta": 4200, "section_24b": 0,
                "hra_exemption": 0,
            },
            "rent_paid": 180000, "is_metro": True, "tds_deducted": 28000,
            "age": 34, "has_health_insurance": False, "has_nps": False, "has_home_loan": False,
            "employer_nps": 0,
        },
        "comparison": {
            "old_regime_tax": 21736, "new_regime_tax": 0,
            "old_regime_taxable_income": 462400, "new_regime_taxable_income": 712600,
            "recommended_regime": "new", "savings_amount": 21736,
            "old_regime_breakdown": {
                "gross_salary": 800000, "hra_exemption": 64000, "standard_deduction": 50000,
                "professional_tax": 2400, "income_from_salary": 683600, "other_income": 12000,
                "gross_total_income": 695600,
                "deductions": {"80C": 50000, "80CCD(1B)": 0, "80D": 0, "80E": 0, "80G": 0, "80TTA": 4200, "24(b)": 0, "80CCD(2)_employer": 0, "total": 54200},
                "taxable_income": 462400, "slab_breakdown": [{"range": "₹0–₹2,50,000", "amount": 250000, "rate": "0%", "tax": 0}, {"range": "₹2,50,000–₹5,00,000", "amount": 212400, "rate": "5%", "tax": 10620}],
                "base_tax": 10620, "rebate_87a": 10620, "tax_after_rebate": 0, "surcharge": 0, "cess": 0, "total_tax": 0,
            },
            "new_regime_breakdown": {
                "gross_salary": 800000, "standard_deduction": 75000, "professional_tax": 2400,
                "income_from_salary": 722600, "other_income": 12000, "gross_total_income": 734600,
                "employer_nps_deduction": 0, "taxable_income": 734600,
                "slab_breakdown": [{"range": "₹0–₹4,00,000", "amount": 400000, "rate": "0%", "tax": 0}, {"range": "₹4,00,000–₹8,00,000", "amount": 334600, "rate": "5%", "tax": 16730}],
                "base_tax": 16730, "rebate_87a": 16730, "tax_after_rebate": 0, "surcharge": 0, "cess": 0, "total_tax": 0,
            },
        },
        "missed_deductions": [
            {"section": "80CCD(1B)", "name": "NPS Contribution", "description": "Invest ₹50,000 in NPS for additional deduction beyond 80C.", "max_limit": 50000, "currently_claimed": 0, "potential_saving": 2600, "priority": "high"},
            {"section": "80D", "name": "Health Insurance Premium", "description": "Health insurance premium up to ₹25,000. Parents: additional ₹25,000.", "max_limit": 50000, "currently_claimed": 0, "potential_saving": 1300, "priority": "high"},
            {"section": "80C", "name": "Section 80C Investment", "description": "Invest ₹88,400 more in ELSS/PPF/NPS to use full ₹1.5L limit.", "max_limit": 150000, "currently_claimed": 50000, "potential_saving": 4600, "priority": "high"},
        ],
        "action_plan": [
            {"action": "Switch to New Tax Regime immediately", "saving_amount": 21736, "deadline": "April 1, 2026", "difficulty": "easy", "explanation": "Under the New Regime, your ₹7.35L taxable income falls under the ₹7L 87A rebate threshold — making your tax ₹0. Submit Form 12B to your employer before April."},
            {"action": "Buy health insurance for yourself and parents", "saving_amount": 6500, "deadline": "March 31, 2026", "difficulty": "easy", "explanation": "A ₹5L family floater costs ~₹12,000/year. You save ₹1,300 in tax (Old Regime) and get critical health protection."},
            {"action": "Open NPS account and invest ₹50,000", "saving_amount": 2600, "deadline": "March 31, 2026", "difficulty": "medium", "explanation": "Exclusive ₹50,000 deduction under 80CCD(1B) beyond your 80C limit. Open online at nps.co.in in 15 minutes."},
        ],
        "total_potential_savings": 8500,
        "summary": "Great news, Sunita! Under the New Tax Regime, your tax liability is ₹0 — saving you ₹21,736 vs the Old Regime. You've already paid ₹28,000 in TDS, so you're due a refund of ₹28,000. Additionally, getting health insurance and opening an NPS account can save you ₹8,500 more in future tax years.",
    },
    "arjun": {
        "tax_profile": {
            "salary": {
                "gross_salary": 2400000, "basic_salary": 960000, "hra_received": 384000,
                "special_allowance": 768000, "lta": 48000, "professional_tax": 2400,
                "epf_employee": 115200, "other_income": 85000,
            },
            "deductions": {
                "section_80c": 34800, "section_80ccd_1b": 0, "section_80d": 18000,
                "section_80e": 0, "section_80g": 5000, "section_80tta": 0, "section_24b": 0,
                "hra_exemption": 0,
            },
            "rent_paid": 360000, "is_metro": False, "tds_deducted": 320000,
            "age": 29, "has_health_insurance": True, "has_nps": False, "has_home_loan": False,
            "employer_nps": 0,
        },
        "comparison": {
            "old_regime_tax": 335894, "new_regime_tax": 364428,
            "old_regime_taxable_income": 1559600, "new_regime_taxable_income": 2212600,
            "recommended_regime": "old", "savings_amount": 28534,
            "old_regime_breakdown": {
                "gross_salary": 2400000, "hra_exemption": 230400, "standard_deduction": 50000,
                "professional_tax": 2400, "income_from_salary": 2117200, "other_income": 85000,
                "gross_total_income": 2202200,
                "deductions": {"80C": 150000, "80CCD(1B)": 0, "80D": 18000, "80E": 0, "80G": 5000, "80TTA": 0, "24(b)": 0, "80CCD(2)_employer": 0, "total": 173000},
                "taxable_income": 1559600,
                "slab_breakdown": [{"range": "₹0–₹2,50,000", "amount": 250000, "rate": "0%", "tax": 0}, {"range": "₹2,50,000–₹5,00,000", "amount": 250000, "rate": "5%", "tax": 12500}, {"range": "₹5,00,000–₹10,00,000", "amount": 500000, "rate": "20%", "tax": 100000}, {"range": "Above ₹10,00,000", "amount": 559600, "rate": "30%", "tax": 167880}],
                "base_tax": 280380, "rebate_87a": 0, "tax_after_rebate": 280380, "surcharge": 0, "cess": 11215, "total_tax": 291595,
            },
            "new_regime_breakdown": {
                "gross_salary": 2400000, "standard_deduction": 75000, "professional_tax": 2400,
                "income_from_salary": 2322600, "other_income": 85000, "gross_total_income": 2407600,
                "employer_nps_deduction": 0, "taxable_income": 2407600,
                "slab_breakdown": [{"range": "₹0–₹4,00,000", "amount": 400000, "rate": "0%", "tax": 0}, {"range": "₹4,00,000–₹8,00,000", "amount": 400000, "rate": "5%", "tax": 20000}, {"range": "₹8,00,000–₹12,00,000", "amount": 400000, "rate": "10%", "tax": 40000}, {"range": "₹12,00,000–₹16,00,000", "amount": 400000, "rate": "15%", "tax": 60000}, {"range": "₹16,00,000–₹20,00,000", "amount": 400000, "rate": "20%", "tax": 80000}, {"range": "₹20,00,000–₹24,00,000", "amount": 407600, "rate": "25%", "tax": 101900}],
                "base_tax": 301900, "rebate_87a": 0, "tax_after_rebate": 301900, "surcharge": 0, "cess": 12076, "total_tax": 313976,
            },
        },
        "missed_deductions": [
            {"section": "80CCD(1B)", "name": "NPS Contribution", "description": "Invest ₹50,000 in NPS for additional deduction beyond 80C.", "max_limit": 50000, "currently_claimed": 0, "potential_saving": 15600, "priority": "high"},
            {"section": "80C", "name": "Section 80C Investment", "description": "Invest ₹100,200 more in ELSS/PPF/NPS Tier-I to use full ₹1.5L limit.", "max_limit": 150000, "currently_claimed": 50000, "potential_saving": 31262, "priority": "high"},
            {"section": "10(13A)", "name": "HRA Exemption", "description": "You receive HRA but living in non-metro. Ensure rent receipts are submitted.", "max_limit": 384000, "currently_claimed": 0, "potential_saving": 8624, "priority": "high"},
        ],
        "action_plan": [
            {"action": "Stay on Old Regime — claim all deductions", "saving_amount": 28534, "deadline": "April 1, 2026", "difficulty": "easy", "explanation": "Your high 80C + HRA deductions make Old Regime ₹28,534 cheaper. Ensure you've explicitly opted in with your employer."},
            {"action": "Invest ₹1,00,200 more in ELSS to max 80C", "saving_amount": 31262, "deadline": "March 31, 2026", "difficulty": "medium", "explanation": "Your current 80C is only ₹50,000. Invest ₹1,00,200 more in ELSS (tax saving mutual funds) to hit the ₹1.5L ceiling and save ₹31,262 in tax."},
            {"action": "Open NPS Tier-I and invest ₹50,000", "saving_amount": 15600, "deadline": "March 31, 2026", "difficulty": "medium", "explanation": "Section 80CCD(1B) gives you an exclusive ₹50,000 deduction on top of 80C. At 30% bracket, that's ₹15,600 saved instantly."},
        ],
        "total_potential_savings": 55486,
        "summary": "Arjun, stick with the Old Regime — it saves you ₹28,534 vs New Regime. You've paid ₹3,20,000 TDS but owe ₹2,91,595, so expect a ₹28,405 refund. Bigger opportunity: filling your 80C gap and opening NPS could save an additional ₹46,862 next year.",
    },
    "kavita": {
        "tax_profile": {
            "salary": {
                "gross_salary": 5000000, "basic_salary": 2000000, "hra_received": 600000,
                "special_allowance": 1800000, "lta": 100000, "professional_tax": 2400,
                "epf_employee": 180000, "other_income": 300000,
            },
            "deductions": {
                "section_80c": 150000, "section_80ccd_1b": 50000, "section_80d": 50000,
                "section_80e": 0, "section_80g": 25000, "section_80tta": 0, "section_24b": 200000,
                "hra_exemption": 0,
            },
            "rent_paid": 0, "is_metro": True, "tds_deducted": 1200000,
            "age": 42, "has_health_insurance": True, "has_nps": True, "has_home_loan": True,
            "employer_nps": 200000,
        },
        "comparison": {
            "old_regime_tax": 1124388, "new_regime_tax": 1348940,
            "old_regime_taxable_income": 3842600, "new_regime_taxable_income": 4772600,
            "recommended_regime": "old", "savings_amount": 224552,
            "old_regime_breakdown": {
                "gross_salary": 5000000, "hra_exemption": 0, "standard_deduction": 50000,
                "professional_tax": 2400, "income_from_salary": 4947600, "other_income": 300000,
                "gross_total_income": 5247600,
                "deductions": {"80C": 150000, "80CCD(1B)": 50000, "80D": 50000, "80E": 0, "80G": 25000, "80TTA": 0, "24(b)": 200000, "80CCD(2)_employer": 180000, "total": 655000},
                "taxable_income": 3842600,
                "slab_breakdown": [{"range": "₹0–₹2,50,000", "amount": 250000, "rate": "0%", "tax": 0}, {"range": "₹2,50,000–₹5,00,000", "amount": 250000, "rate": "5%", "tax": 12500}, {"range": "₹5,00,000–₹10,00,000", "amount": 500000, "rate": "20%", "tax": 100000}, {"range": "Above ₹10,00,000", "amount": 2842600, "rate": "30%", "tax": 852780}],
                "base_tax": 965280, "rebate_87a": 0, "tax_after_rebate": 965280, "surcharge": 96528, "cess": 42473, "total_tax": 1104281,
            },
            "new_regime_breakdown": {
                "gross_salary": 5000000, "standard_deduction": 75000, "professional_tax": 2400,
                "income_from_salary": 4922600, "other_income": 300000, "gross_total_income": 5222600,
                "employer_nps_deduction": 200000, "taxable_income": 5022600,
                "slab_breakdown": [],
                "base_tax": 1162650, "rebate_87a": 0, "tax_after_rebate": 1162650, "surcharge": 116265, "cess": 51156, "total_tax": 1330071,
            },
        },
        "missed_deductions": [
            {"section": "80E", "name": "Education Loan Interest", "description": "If you have an education loan for children, interest is fully deductible. No upper limit.", "max_limit": 200000, "currently_claimed": 0, "potential_saving": 62400, "priority": "medium"},
        ],
        "action_plan": [
            {"action": "Old Regime saves ₹2,24,552 — confirm with CA", "saving_amount": 224552, "deadline": "April 1, 2026", "difficulty": "easy", "explanation": "Your high deductions (80C, NPS, home loan, health) make Old Regime significantly better. Ensure your employer's TDS is calculated on Old Regime."},
            {"action": "Education loan interest deduction under 80E", "saving_amount": 62400, "deadline": "March 31, 2026", "difficulty": "easy", "explanation": "If you or your children have any education loans, 100% of interest paid is deductible under 80E with no upper limit. Check with your CA."},
        ],
        "total_potential_savings": 62400,
        "summary": "Kavita, the Old Regime saves you ₹2,24,552 over New Regime — stick with it. You've claimed all major deductions correctly. Your TDS of ₹12,00,000 is close to your liability of ₹11,04,281, so you'll get a small refund. Explore 80E if there are any education loans in the family.",
    },
}

DEMO_PORTFOLIO = {
    "sunita": {
        "portfolio": {
            "holdings": [
                {"name": "UTI Nifty 50 Index Fund — Direct", "folio": "1234/01", "units": 245.67, "nav": 152.34, "current_value": 374200, "invested_amount": 300000, "category": "index", "plan_type": "direct", "xirr": 15.2},
                {"name": "SBI Bluechip Fund — Regular", "folio": "1234/02", "units": 88.12, "nav": 82.45, "current_value": 72650, "invested_amount": 60000, "category": "large_cap", "plan_type": "regular", "xirr": 12.1},
                {"name": "SBI Liquid Fund", "folio": "1234/03", "units": 412.3, "nav": 3662.4, "current_value": 150000, "invested_amount": 140000, "category": "liquid", "plan_type": "regular", "xirr": 6.8},
            ],
            "total_current_value": 596850, "total_invested": 500000, "absolute_return_pct": 19.4,
        },
        "portfolio_xirr": 13.1, "nifty50_return": 12.5, "alpha": 0.6,
        "overlap_matrix": {
            "UTI Nifty 50 Index Fund — Direct": {"UTI Nifty 50 Index Fund — Direct": 100.0, "SBI Bluechip Fund — Regular": 70.0, "SBI Liquid Fund": 0.0},
            "SBI Bluechip Fund — Regular": {"UTI Nifty 50 Index Fund — Direct": 70.0, "SBI Bluechip Fund — Regular": 100.0, "SBI Liquid Fund": 0.0},
            "SBI Liquid Fund": {"UTI Nifty 50 Index Fund — Direct": 0.0, "SBI Bluechip Fund — Regular": 0.0, "SBI Liquid Fund": 100.0},
        },
        "overlap_alerts": [{"fund_a": "UTI Nifty 50 Index Fund — Direct", "fund_b": "SBI Bluechip Fund — Regular", "overlap_pct": 70.0, "severity": "high", "message": "UTI Nifty 50 Index and SBI Bluechip share 70% of top holdings — consider consolidating into just the index fund."}],
        "expense_drag": {"total_portfolio_value": 596850, "total_annual_drag": 4920, "total_ten_year_drag": 49200, "regular_plan_funds": 2, "details": [{"fund": "SBI Bluechip Fund — Regular", "current_value": 72650, "current_er": 1.5, "direct_er": 0.8, "annual_saving": 509, "ten_year_saving": 5090}, {"fund": "SBI Liquid Fund", "current_value": 150000, "current_er": 0.25, "direct_er": 0.1, "annual_saving": 225, "ten_year_saving": 2250}], "tip": "Switching to direct plans saves ₹4,920/year — ₹49,200 over 10 years."},
        "rebalancing_plan": [{"category": "debt", "current_pct": 25.1, "target_pct": 30.0, "action": "buy", "amount": 29370, "message": "Add ₹29,370 in debt funds (currently 25%, target 30%)."}],
        "summary": "Your portfolio has returned ~13.1% CAGR, outperforming NIFTY 50 by 0.6%. UTI Nifty 50 and SBI Bluechip have 70% overlap — you're paying double fees for the same stocks. Switch 2 funds to direct plans to save ₹4,920/year.",
    },
    "arjun": {
        "portfolio": {
            "holdings": [
                {"name": "Parag Parikh Flexi Cap Fund — Direct", "folio": "9876/01", "units": 892.4, "nav": 78.92, "current_value": 704500, "invested_amount": 500000, "category": "flexi_cap", "plan_type": "direct", "xirr": 18.4},
                {"name": "Axis Bluechip Fund — Direct", "folio": "9876/02", "units": 1245.6, "nav": 52.34, "current_value": 652000, "invested_amount": 500000, "category": "large_cap", "plan_type": "direct", "xirr": 9.2},
                {"name": "Mirae Asset Emerging Bluechip — Regular", "folio": "9876/03", "units": 432.1, "nav": 122.4, "current_value": 528890, "invested_amount": 350000, "category": "mid_cap", "plan_type": "regular", "xirr": 16.7},
                {"name": "UTI Nifty Next 50 Index — Direct", "folio": "9876/04", "units": 1876.3, "nav": 42.18, "current_value": 791300, "invested_amount": 600000, "category": "index", "plan_type": "direct", "xirr": 9.8},
                {"name": "ICICI Pru Short Term Debt — Regular", "folio": "9876/05", "units": 8234.5, "nav": 30.22, "current_value": 248800, "invested_amount": 220000, "category": "debt", "plan_type": "regular", "xirr": 7.1},
                {"name": "Sovereign Gold Bond 2024", "folio": "N/A", "units": 50, "nav": 7200, "current_value": 360000, "invested_amount": 300000, "category": "gold", "plan_type": "direct", "xirr": 12.3},
            ],
            "total_current_value": 3285490, "total_invested": 2470000, "absolute_return_pct": 33.0,
        },
        "portfolio_xirr": 14.2, "nifty50_return": 12.5, "alpha": 1.7,
        "overlap_matrix": {
            "Parag Parikh Flexi Cap Fund — Direct": {"Parag Parikh Flexi Cap Fund — Direct": 100.0, "Axis Bluechip Fund — Direct": 30.0, "Mirae Asset Emerging Bluechip — Regular": 20.0, "UTI Nifty Next 50 Index — Direct": 10.0, "ICICI Pru Short Term Debt — Regular": 0.0, "Sovereign Gold Bond 2024": 0.0},
            "Axis Bluechip Fund — Direct": {"Parag Parikh Flexi Cap Fund — Direct": 30.0, "Axis Bluechip Fund — Direct": 100.0, "Mirae Asset Emerging Bluechip — Regular": 40.0, "UTI Nifty Next 50 Index — Direct": 20.0, "ICICI Pru Short Term Debt — Regular": 0.0, "Sovereign Gold Bond 2024": 0.0},
            "Mirae Asset Emerging Bluechip — Regular": {"Parag Parikh Flexi Cap Fund — Direct": 20.0, "Axis Bluechip Fund — Direct": 40.0, "Mirae Asset Emerging Bluechip — Regular": 100.0, "UTI Nifty Next 50 Index — Direct": 30.0, "ICICI Pru Short Term Debt — Regular": 0.0, "Sovereign Gold Bond 2024": 0.0},
            "UTI Nifty Next 50 Index — Direct": {"Parag Parikh Flexi Cap Fund — Direct": 10.0, "Axis Bluechip Fund — Direct": 20.0, "Mirae Asset Emerging Bluechip — Regular": 30.0, "UTI Nifty Next 50 Index — Direct": 100.0, "ICICI Pru Short Term Debt — Regular": 0.0, "Sovereign Gold Bond 2024": 0.0},
            "ICICI Pru Short Term Debt — Regular": {"Parag Parikh Flexi Cap Fund — Direct": 0.0, "Axis Bluechip Fund — Direct": 0.0, "Mirae Asset Emerging Bluechip — Regular": 0.0, "UTI Nifty Next 50 Index — Direct": 0.0, "ICICI Pru Short Term Debt — Regular": 100.0, "Sovereign Gold Bond 2024": 0.0},
            "Sovereign Gold Bond 2024": {"Parag Parikh Flexi Cap Fund — Direct": 0.0, "Axis Bluechip Fund — Direct": 0.0, "Mirae Asset Emerging Bluechip — Regular": 0.0, "UTI Nifty Next 50 Index — Direct": 0.0, "ICICI Pru Short Term Debt — Regular": 0.0, "Sovereign Gold Bond 2024": 100.0},
        },
        "overlap_alerts": [],
        "expense_drag": {"total_portfolio_value": 3285490, "total_annual_drag": 8720, "total_ten_year_drag": 87200, "regular_plan_funds": 2, "details": [{"fund": "Mirae Asset Emerging Bluechip — Regular", "current_value": 528890, "current_er": 1.8, "direct_er": 0.9, "annual_saving": 4760, "ten_year_saving": 47600}, {"fund": "ICICI Pru Short Term Debt — Regular", "current_value": 248800, "current_er": 0.8, "direct_er": 0.3, "annual_saving": 1244, "ten_year_saving": 12440}], "tip": "Switching to direct plans saves ₹8,720/year — ₹87,200 over 10 years."},
        "rebalancing_plan": [],
        "summary": "Arjun, your ₹32.85L portfolio has returned 14.2% CAGR — outperforming NIFTY 50 by 1.7%. Good diversification across equity, debt, and gold. Switch 2 remaining regular plan funds to direct and save ₹8,720/year in fees.",
    },
}

DEMO_HEALTH = {
    "sunita": {
        "overall_score": 48, "grade": "C",
        "dimensions": [
            {"name": "Emergency Fund", "score": 33, "details": {"months_covered": 2.0, "target_months": 6, "gap_amount": 240000}, "improvement_tip": "Build ₹2,40,000 more in liquid funds to reach 6-month cover."},
            {"name": "Insurance Coverage", "score": 25, "details": {"life_cover": 0, "target_life_cover": 8000000, "health_cover": 0, "target_health_cover": 300000, "life_gap": 8000000, "health_gap": 300000}, "improvement_tip": "Increase term life cover by ₹80,00,000 (target: 10x income). No health cover detected."},
            {"name": "Investment Diversification", "score": 62, "details": {"asset_classes": {"index": 62.7, "large_cap": 12.2, "liquid": 25.1}, "largest_allocation": 62.7, "num_asset_classes": 3}, "improvement_tip": "Add debt/gold to your portfolio for better diversification."},
            {"name": "Debt Health", "score": 100, "details": {"dti_ratio": 0.0, "monthly_emi": 0, "status": "Good"}, "improvement_tip": "Your debt load is manageable!"},
            {"name": "Tax Efficiency", "score": 40, "details": {"missed_count": 3, "annual_loss": 8500, "loss_pct_of_income": 1.1}, "improvement_tip": "Claim 3 missed deductions to save ₹8,500/year."},
            {"name": "Retirement Readiness", "score": 22, "details": {"projected_corpus": 2840000, "required_corpus": 14000000, "coverage_pct": 20.3, "years_to_retire": 26}, "improvement_tip": "Increase SIP by ₹12,000/month to stay on track for retirement."},
        ],
        "improvement_actions": [
            {"dimension": "Insurance Coverage", "current_score": 25, "tip": "Buy a ₹1 crore term plan (costs ~₹8,000/year at age 34). Add a ₹5L health insurance plan.", "score_impact": 20},
            {"dimension": "Retirement Readiness", "current_score": 22, "tip": "Start a ₹5,000/month SIP today. Even small amounts compound significantly over 26 years.", "score_impact": 15},
            {"dimension": "Emergency Fund", "current_score": 33, "tip": "Park ₹2,40,000 in a liquid mutual fund. Target: 6× monthly expenses = ₹3,60,000.", "score_impact": 15},
        ],
        "projected_score_after_actions": 63,
    },
    "arjun": {
        "overall_score": 71, "grade": "B",
        "dimensions": [
            {"name": "Emergency Fund", "score": 80, "details": {"months_covered": 4.8, "target_months": 6, "gap_amount": 72000}, "improvement_tip": "Build ₹72,000 more to reach a full 6-month emergency fund."},
            {"name": "Insurance Coverage", "score": 65, "details": {"life_cover": 15000000, "target_life_cover": 24000000, "health_cover": 1000000, "target_health_cover": 600000, "life_gap": 9000000, "health_gap": 0}, "improvement_tip": "Increase term life cover by ₹90L (target: 10× income at ₹24L)."},
            {"name": "Investment Diversification", "score": 85, "details": {"asset_classes": {"flexi_cap": 21.4, "large_cap": 19.8, "mid_cap": 16.1, "index": 24.1, "debt": 7.6, "gold": 11.0}, "largest_allocation": 24.1, "num_asset_classes": 6}, "improvement_tip": "Great spread across asset classes!"},
            {"name": "Debt Health", "score": 88, "details": {"dti_ratio": 18.5, "monthly_emi": 37000, "status": "Good"}, "improvement_tip": "Your debt load is manageable!"},
            {"name": "Tax Efficiency", "score": 58, "details": {"missed_count": 3, "annual_loss": 55486, "loss_pct_of_income": 2.3}, "improvement_tip": "Claim 3 missed deductions to save ₹55,486/year."},
            {"name": "Retirement Readiness", "score": 68, "details": {"projected_corpus": 52000000, "required_corpus": 63000000, "coverage_pct": 82.5, "years_to_retire": 31}, "improvement_tip": "Increase SIP by ₹8,000/month to close the retirement gap."},
        ],
        "improvement_actions": [
            {"dimension": "Tax Efficiency", "current_score": 58, "tip": "Max out 80C with ELSS + open NPS for 80CCD(1B) → save ₹55,486 in taxes this year.", "score_impact": 20},
            {"dimension": "Insurance Coverage", "current_score": 65, "tip": "Top up term life to ₹2.4 crore total cover. Costs ~₹5,000/year more.", "score_impact": 12},
            {"dimension": "Retirement Readiness", "current_score": 68, "tip": "Add ₹8,000/month to SIP. At 29, every ₹1,000 today = ₹18,000 at 60.", "score_impact": 10},
        ],
        "projected_score_after_actions": 85,
    },
}

DEMO_FIRE = {
    "sunita": {
        "fire_age": 55, "years_to_fire": 21, "target_corpus": 17500000, "projected_corpus": 8200000,
        "shortfall": 9300000, "monthly_sip_current": 5000, "monthly_sip_required": 22800,
        "blended_return_pct": 10.6, "asset_allocation": {"equity": 56, "debt": 34, "gold": 10},
        "savings_rate_pct": 42.5, "adj_annual_expenses": 840000, "on_track": False,
        "milestones": [{"year": 2026 + i, "projected_corpus": int(596850 * (1.108 ** i) + 5000 * 12 * i * (1.108 ** (i/2))), "target_line": int(17500000 * i / 21)} for i in range(22)],
    },
    "arjun": {
        "fire_age": 42, "years_to_fire": 13, "target_corpus": 52500000, "projected_corpus": 64800000,
        "shortfall": 0, "monthly_sip_current": 80000, "monthly_sip_required": 0,
        "blended_return_pct": 12.4, "asset_allocation": {"equity": 61, "debt": 29, "gold": 10},
        "savings_rate_pct": 60.0, "adj_annual_expenses": 2520000, "on_track": True,
        "milestones": [{"year": 2026 + i, "projected_corpus": int(3285490 * (1.124 ** i) + 80000 * 12 * i * (1.124 ** (i/2))), "target_line": int(52500000 * i / 13)} for i in range(14)],
    },
}


# ───────────────────────────────────────────────────────────────────────────────
# ROUTES
# ───────────────────────────────────────────────────────────────────────────────

Persona = Literal["sunita", "arjun", "kavita"]


@router.get("/demo/tax/{persona}")
async def demo_tax(persona: Persona):
    """Return a pre-built tax analysis result for a demo persona."""
    if persona not in DEMO_TAX:
        raise HTTPException(status_code=404, detail=f"Demo persona '{persona}' not found.")
    return DEMO_TAX[persona]


@router.get("/demo/portfolio/{persona}")
async def demo_portfolio(persona: str):
    """Return a pre-built portfolio X-Ray for a demo persona."""
    if persona not in DEMO_PORTFOLIO:
        raise HTTPException(status_code=404, detail=f"Demo persona '{persona}' not found.")
    return DEMO_PORTFOLIO[persona]


@router.get("/demo/health/{persona}")
async def demo_health(persona: str):
    """Return a pre-built health score for a demo persona."""
    if persona not in DEMO_HEALTH:
        raise HTTPException(status_code=404, detail=f"Demo persona '{persona}' not found.")
    return DEMO_HEALTH[persona]


@router.get("/demo/fire/{persona}")
async def demo_fire(persona: str):
    """Return a pre-built FIRE plan for a demo persona."""
    if persona not in DEMO_FIRE:
        raise HTTPException(status_code=404, detail=f"Demo persona '{persona}' not found.")
    return DEMO_FIRE[persona]


@router.get("/demo/personas")
async def list_personas():
    """List available demo personas."""
    return {
        "personas": [
            {"id": "sunita", "name": "Sunita Verma", "role": "Teacher", "city": "Delhi", "income": "₹8L/year", "emoji": "👩‍🏫"},
            {"id": "arjun", "name": "Arjun Mehta", "role": "Software Engineer", "city": "Bengaluru", "income": "₹24L/year", "emoji": "👨‍💻"},
            {"id": "kavita", "name": "Kavita Shah", "role": "Business Owner", "city": "Mumbai", "income": "₹50L/year", "emoji": "👩‍💼"},
        ]
    }
