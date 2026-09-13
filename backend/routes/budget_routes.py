"""
AI Budget Planner — "Fix My Budget in 60 Seconds"
User inputs income & expenses → GPT-4o generates an optimised budget with actionable advice.
"""

from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional, List
import json
from openai import OpenAI
from config.settings import settings

router = APIRouter()


class BudgetRequest(BaseModel):
    monthly_income: float = 0
    rent: float = 0
    groceries: float = 0
    utilities: float = 0          # electricity, water, internet, phone
    emis: float = 0               # existing loan EMIs
    insurance: float = 0          # health + life premiums per month
    sip_investments: float = 0    # SIPs and recurring investments
    transport: float = 0          # fuel, metro, uber
    dining_out: float = 0         # restaurants, zomato, swiggy
    shopping: float = 0           # clothes, gadgets, etc.
    subscriptions: float = 0      # netflix, spotify, gym, etc.
    education: float = 0          # courses, tuition, books
    medical: float = 0            # recurring medical expenses
    other_expenses: float = 0     # anything else
    dependants: int = 0
    age: int = 30
    financial_goal: str = ""      # e.g. "Buy a house in 3 years"


def _build_budget_math(req: BudgetRequest) -> dict:
    """Compute current budget breakdown without AI."""
    expenses = {
        "Rent": req.rent,
        "Groceries": req.groceries,
        "Utilities": req.utilities,
        "EMIs": req.emis,
        "Insurance": req.insurance,
        "Investments (SIP)": req.sip_investments,
        "Transport": req.transport,
        "Dining Out": req.dining_out,
        "Shopping": req.shopping,
        "Subscriptions": req.subscriptions,
        "Education": req.education,
        "Medical": req.medical,
        "Other": req.other_expenses,
    }

    # Filter zero entries
    expenses = {k: v for k, v in expenses.items() if v > 0}
    total_expenses = sum(expenses.values())
    surplus = req.monthly_income - total_expenses

    # Category buckets (50/30/20 framework)
    needs = req.rent + req.groceries + req.utilities + req.emis + req.insurance + req.transport + req.medical
    wants = req.dining_out + req.shopping + req.subscriptions + req.education + req.other_expenses
    savings = req.sip_investments

    needs_pct = round(needs / req.monthly_income * 100, 1) if req.monthly_income > 0 else 0
    wants_pct = round(wants / req.monthly_income * 100, 1) if req.monthly_income > 0 else 0
    savings_pct = round(savings / req.monthly_income * 100, 1) if req.monthly_income > 0 else 0
    unallocated_pct = round(surplus / req.monthly_income * 100, 1) if req.monthly_income > 0 else 0

    return {
        "expenses": expenses,
        "total_expenses": round(total_expenses),
        "monthly_surplus": round(surplus),
        "current_split": {
            "needs": round(needs),
            "needs_pct": needs_pct,
            "wants": round(wants),
            "wants_pct": wants_pct,
            "savings": round(savings),
            "savings_pct": savings_pct,
            "unallocated": round(surplus),
            "unallocated_pct": unallocated_pct,
        },
        "ideal_split": {
            "needs": round(req.monthly_income * 0.50),
            "needs_pct": 50,
            "wants": round(req.monthly_income * 0.30),
            "wants_pct": 30,
            "savings": round(req.monthly_income * 0.20),
            "savings_pct": 20,
        },
    }


def _generate_ai_plan(req: BudgetRequest, math: dict) -> dict:
    """Use GPT-4o to generate personalised budget advice."""
    if not settings.OPENAI_API_KEY:
        return {
            "optimised_budget": {},
            "quick_wins": [
                {"action": "Set up auto-SIP", "monthly_saving": round(req.monthly_income * 0.05), "difficulty": "easy"},
                {"action": "Cut dining out by 30%", "monthly_saving": round(req.dining_out * 0.3), "difficulty": "easy"},
                {"action": "Review subscriptions", "monthly_saving": round(req.subscriptions * 0.5), "difficulty": "easy"},
            ],
            "summary": f"You're spending {math['current_split']['needs_pct']}% on needs, {math['current_split']['wants_pct']}% on wants, and saving {math['current_split']['savings_pct']}%. Target the 50/30/20 split for financial health.",
            "health_grade": "B",
        }

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    context = {
        "monthly_income": req.monthly_income,
        "age": req.age,
        "dependants": req.dependants,
        "financial_goal": req.financial_goal or "Build emergency fund and start investing",
        "current_expenses": math["expenses"],
        "total_expenses": math["total_expenses"],
        "monthly_surplus": math["monthly_surplus"],
        "current_split": math["current_split"],
        "ideal_50_30_20": math["ideal_split"],
    }

    prompt = f"""You are India's top personal finance coach. A user has shared their monthly budget. Create an optimised budget plan.

USER DATA:
{json.dumps(context, indent=2)}

INSTRUCTIONS:
1. Analyse their current spending pattern
2. Create an optimised monthly budget using the 50/30/20 rule (adjusted for Indian context)
3. Identify 3-5 "quick wins" — specific, actionable cuts/changes with exact ₹ savings
4. Give a budget health grade (A/B/C/D/F)
5. Write a 2-3 sentence personalised summary

IMPORTANT RULES:
- Use Indian context (₹ amounts, Indian expense patterns)
- Be specific with numbers — "Cut Swiggy orders from 15/month to 8" not "reduce dining"
- Don't suggest unrealistic cuts (don't tell someone paying ₹25K rent to move)
- If savings are <20%, prioritise increasing that
- If EMI is >35% of income, flag it as dangerous

Return ONLY a JSON object:
{{
  "optimised_budget": {{
    "Rent": 25000,
    "Groceries": 8000,
    ...
  }},
  "quick_wins": [
    {{
      "action": "Specific action description",
      "monthly_saving": 3000,
      "difficulty": "easy|medium|hard",
      "category": "which expense category"
    }}
  ],
  "summary": "2-3 sentence personalised advice",
  "health_grade": "B",
  "target_savings_rate": 25,
  "monthly_savings_possible": 15000
}}"""

    try:
        resp = client.chat.completions.create(
            model=settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a personal finance expert for Indian salaried professionals. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        return json.loads(resp.choices[0].message.content)
    except Exception as e:
        return {
            "optimised_budget": {},
            "quick_wins": [],
            "summary": f"Could not generate AI plan: {str(e)}",
            "health_grade": "?",
        }


@router.post("/budget-plan")
async def budget_plan(req: BudgetRequest):
    if req.monthly_income <= 0:
        return {"error": "Monthly income must be greater than 0"}

    math = _build_budget_math(req)
    ai_plan = _generate_ai_plan(req, math)

    return {
        "income": round(req.monthly_income),
        "current": math,
        "ai_plan": ai_plan,
    }
