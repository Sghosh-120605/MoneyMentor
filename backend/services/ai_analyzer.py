"""
AI Action Plan Generator — Uses GPT to convert tax analysis into actionable advice.
"""

import json
from typing import List
from openai import OpenAI

from config.settings import settings
from core.schemas import TaxProfile, TaxComparison, MissedDeduction, ActionItem


def generate_action_plan(
    profile: TaxProfile,
    comparison: TaxComparison,
    missed: List[MissedDeduction],
) -> List[ActionItem]:
    """Generate AI-powered actionable tax-saving plan."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    context = {
        "gross_salary": profile.salary.gross_salary,
        "recommended_regime": comparison.recommended_regime,
        "regime_savings": comparison.savings_amount,
        "old_tax": comparison.old_regime_tax,
        "new_tax": comparison.new_regime_tax,
        "tds_paid": profile.tds_deducted,
        "missed_deductions": [
            {"section": m.section, "name": m.name, "gap": m.max_limit - m.currently_claimed, "saving": m.potential_saving}
            for m in missed
        ],
        "age": profile.age,
        "has_health_insurance": profile.has_health_insurance,
        "has_nps": profile.has_nps,
        "has_home_loan": profile.has_home_loan,
    }

    prompt = f"""You are India's top tax advisor. Based on this taxpayer's data, generate 3-5 specific, actionable tax-saving steps.

TAXPAYER DATA:
{json.dumps(context, indent=2)}

RULES:
- Each action must have an exact ₹ saving amount (use the data provided)
- Rank by impact (highest saving first)
- Use simple, direct language a non-expert can understand
- Include specific deadlines (e.g., "before March 31, 2026")
- Difficulty: "easy" (just paperwork), "medium" (requires investment), "hard" (lifestyle change)
- Do NOT recommend anything already being done
- If regime switch saves money, include that as action #1

Return ONLY a JSON array:
[
  {{
    "action": "Short action description",
    "saving_amount": 15600,
    "deadline": "March 31, 2026",
    "difficulty": "easy",
    "explanation": "2-3 sentence explanation of why and how"
  }}
]"""

    resp = client.chat.completions.create(
        model=settings.GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert Indian tax advisor. Return only valid JSON arrays."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
        response_format={"type": "json_object"},
    )

    raw = json.loads(resp.choices[0].message.content)
    items = raw if isinstance(raw, list) else raw.get("actions", raw.get("action_plan", []))

    actions = []
    for item in items[:5]:
        actions.append(ActionItem(
            action=item.get("action", ""),
            saving_amount=float(item.get("saving_amount", 0)),
            deadline=item.get("deadline", "March 31, 2026"),
            difficulty=item.get("difficulty", "medium"),
            explanation=item.get("explanation", ""),
        ))

    return actions


def generate_summary(
    profile: TaxProfile,
    comparison: TaxComparison,
    missed: List[MissedDeduction],
    total_savings: float,
) -> str:
    """Generate a plain-English summary of the tax analysis."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""Write a 3-4 sentence summary for an Indian taxpayer:

- Gross salary: ₹{profile.salary.gross_salary:,.0f}
- Old regime tax: ₹{comparison.old_regime_tax:,.0f}
- New regime tax: ₹{comparison.new_regime_tax:,.0f}
- Recommended: {comparison.recommended_regime} regime (saves ₹{comparison.savings_amount:,.0f})
- TDS already paid: ₹{profile.tds_deducted:,.0f}
- Total potential additional savings: ₹{total_savings:,.0f}
- Number of missed deductions: {len(missed)}

Make it personal, encouraging, and action-oriented. Start with the most impactful finding. Use ₹ amounts. No jargon."""

    resp = client.chat.completions.create(
        model=settings.GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are a friendly Indian financial advisor writing for regular people."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.5,
        max_tokens=300,
    )
    return resp.choices[0].message.content.strip()

def determine_best_tool(answers: dict) -> dict:
    """Uses LLM to evaluate the onboarding answers and route to the best tool."""
    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    prompt = f"""You are the ET MoneyMentor Onboarding AI.
The user has answered 3 questions about their financial state:
1. Primary Goal: {answers.get('q1', 'N/A')}
2. Current Situation: {answers.get('q2', 'N/A')}
3. Immediate Need: {answers.get('q3', 'N/A')}

You have 9 tools available:
1. Tax Wizard (path: '/tax') - Saving tax, finding deductions.
2. Portfolio X-Ray (path: '/portfolio') - Mutual funds/stocks optimization, XIRR.
3. Couple's Planner (path: '/couples') - Married couples combining finances.
4. Money Health (path: '/health') - General checkup for confused users.
5. F.I.R.E Planner (path: '/fire') - Early retirement.
6. Afford Advisor (path: '/afford') - Buying a house, car, or big asset.
7. AI Budget Planner (path: '/budget') - Day-to-day budgeting and tracking.
8. Proactive Alerts (path: '/alerts') - Tracking news impact.

Pick the ONE best tool for this user based on their answers.

CRITICAL INSTRUCTION for 'reasoning': 
Your 'reasoning' MUST explicitly answer "WHY is this recommended?" 
Write 1-2 powerful, conversational sentences combining their exact answers with what the tool will do for them.
Example: "You mentioned you want to afford a big purchase while feeling like your money is a mess. The Afford Advisor will look at your cashflow and tell you exactly if you can buy it today, or how many months you need to wait."

Return ONLY valid JSON resembling:
{{
  "recommended_path": "/tax",
  "tool_name": "Tax Wizard",
  "reasoning": "Because you want to maximize your take-home salary and find missed deductions, the Tax Wizard will instantly scan your Form 16 and find your missing money."
}}
"""

    try:
        resp = client.chat.completions.create(
            model=settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a financial routing agent. Always return valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        import json
        import re
        
        content = resp.choices[0].message.content.strip()
        
        # Strip markdown json block if present
        if content.startswith("```"):
            content = re.sub(r"^```(json)?", "", content)
            content = re.sub(r"```$", "", content).strip()
            
        data = json.loads(content)
        
        # Ensure exact keys to prevent Pydantic ValidationError
        return {
            "recommended_path": data.get("recommended_path", data.get("path", "/health")),
            "tool_name": data.get("tool_name", data.get("toolName", data.get("name", "Money Health Score"))),
            "reasoning": data.get("reasoning", "Let's start your journey with a quick financial health checkup!")
        }
    except Exception as e:
        return {
            "recommended_path": "/health",
            "tool_name": "Money Health Score",
            "reasoning": "Let's start your journey with a quick overall financial health checkup!"
        }
