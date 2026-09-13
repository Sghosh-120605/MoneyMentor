"""
Form 16 PDF Parser — pdfplumber first, GPT-4o fallback.
Extracts salary components and deductions from real Form 16 documents.
"""

import io
import re
import json
import base64
from typing import Dict, Optional
from openai import OpenAI
import pdfplumber

from config.settings import settings
from core.schemas import TaxProfile, SalaryComponents, DeductionsClaimed


# ===================================================================
# MAIN ENTRY POINT
# ===================================================================


def parse_form16(pdf_bytes: bytes) -> TaxProfile:
    """
    Parse Form 16 PDF. Strategy:
    1. Extract text with pdfplumber
    2. Try regex-based extraction
    3. If insufficient → send text to GPT-4o for structured extraction
    4. If no text at all → GPT-4o vision on page images
    """
    full_text = _extract_text(pdf_bytes)

    if not full_text or len(full_text.strip()) < 50:
        return _parse_with_vision(pdf_bytes)

    extracted = _extract_with_regex(full_text)

    if extracted.get("gross_salary", 0) > 0 and extracted.get("tds_deducted", 0) >= 0:
        return _build_profile(extracted)

    return _parse_with_gpt_text(full_text)


# ===================================================================
# STEP 1: TEXT EXTRACTION
# ===================================================================


def _extract_text(pdf_bytes: bytes) -> str:
    full_text = ""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    full_text += text + "\n"
                tables = page.extract_tables()
                for table in tables:
                    for row in table:
                        if row:
                            cleaned = [str(c).strip() for c in row if c]
                            full_text += " | ".join(cleaned) + "\n"
    except Exception as e:
        raise ValueError(f"Failed to read PDF: {e}")
    return full_text


# ===================================================================
# STEP 2: REGEX EXTRACTION
# ===================================================================


def _find_amount(text: str, patterns: list) -> float:
    for pattern in patterns:
        matches = re.findall(pattern, text, re.IGNORECASE | re.MULTILINE)
        for match in matches:
            try:
                raw = match if isinstance(match, str) else (match[-1] if isinstance(match, tuple) else str(match))
                cleaned = raw.replace(",", "").replace(" ", "").strip()
                val = float(cleaned)
                if val > 0:
                    return val
            except (ValueError, IndexError):
                continue
    return 0.0


def _extract_with_regex(text: str) -> Dict:
    data: Dict[str, float] = {}

    data["gross_salary"] = _find_amount(text, [
        r"[Gg]ross\s+[Ss]alary.*?(\d[\d,]*\.?\d*)",
        r"[Gg]ross\s+[Tt]otal\s+[Ss]alary.*?(\d[\d,]*\.?\d*)",
        r"1\s*[\.\)]\s*[Gg]ross\s+[Ss]alary.*?(\d[\d,]*\.?\d*)",
        r"[Gg]ross\s+[Aa]mount.*?(\d[\d,]*\.?\d*)",
    ])

    data["basic_salary"] = _find_amount(text, [
        r"[Bb]asic\s+[Ss]alary.*?(\d[\d,]*\.?\d*)",
        r"[Bb]asic\s+[Pp]ay.*?(\d[\d,]*\.?\d*)",
    ])

    data["hra_received"] = _find_amount(text, [
        r"[Hh]ouse\s+[Rr]ent\s+[Aa]llow.*?(\d[\d,]*\.?\d*)",
        r"HRA.*?(\d[\d,]*\.?\d*)",
    ])

    data["standard_deduction"] = _find_amount(text, [
        r"[Ss]tandard\s+[Dd]eduction.*?(\d[\d,]*\.?\d*)",
        r"16\s*\(?ia\)?.*?(\d[\d,]*\.?\d*)",
    ])

    data["professional_tax"] = _find_amount(text, [
        r"[Pp]rofessional\s+[Tt]ax.*?(\d[\d,]*\.?\d*)",
        r"[Tt]ax\s+on\s+[Ee]mployment.*?(\d[\d,]*\.?\d*)",
        r"16\s*\(?ii\)?.*?(\d[\d,]*\.?\d*)",
    ])

    data["section_80c"] = _find_amount(text, [
        r"80\s*C\b[^CD].*?(\d[\d,]*\.?\d*)",
        r"VI[\-\s]*A.*?80C.*?(\d[\d,]*\.?\d*)",
    ])

    data["section_80ccd_1b"] = _find_amount(text, [
        r"80\s*CCD\s*\(?\s*1\s*B\s*\)?.*?(\d[\d,]*\.?\d*)",
    ])

    data["section_80d"] = _find_amount(text, [
        r"80\s*D\b.*?(\d[\d,]*\.?\d*)",
    ])

    data["tds_deducted"] = _find_amount(text, [
        r"[Tt]otal\s+[Tt]ax\s+[Dd]eposited.*?(\d[\d,]*\.?\d*)",
        r"[Tt]ax\s+[Dd]educt.*?[Ss]ource.*?(\d[\d,]*\.?\d*)",
        r"TDS.*?(\d[\d,]*\.?\d*)",
    ])

    data["epf_employee"] = _find_amount(text, [
        r"[Pp]rovident\s+[Ff]und.*?(\d[\d,]*\.?\d*)",
        r"EPF.*?(\d[\d,]*\.?\d*)",
        r"PF\s+[Cc]ontribution.*?(\d[\d,]*\.?\d*)",
    ])

    # ── Other income & house property (can be negative) ──
    data["income_other_sources"] = _find_amount(text, [
        r"[Ii]ncome\s+[Ff]rom\s+[Oo]ther\s+[Ss]ources.*?(\d[\d,]*\.?\d*)",
        r"[Oo]ther\s+[Ss]ources?.*?(\d[\d,]*\.?\d*)",
    ])

    data["house_property_income"] = _find_amount(text, [
        r"[Ii]ncome\s+[Ff]rom\s+[Hh]ouse\s+[Pp]roperty.*?\(?-?\)?(\d[\d,]*\.?\d*)",
        r"[Hh]ouse\s+[Pp]roperty.*?\(?-?\)?(\d[\d,]*\.?\d*)",
    ])

    # Check if house property is negative (loss)
    hp_loss_match = re.search(
        r"[Hh]ouse\s+[Pp]roperty.*?\([-]?(\d[\d,]*\.?\d*)\)",
        text, re.IGNORECASE
    )
    if hp_loss_match:
        data["house_property_loss"] = float(hp_loss_match.group(1).replace(",", ""))
    elif re.search(r"[Hh]ouse\s+[Pp]roperty.*?-\s*(\d[\d,]*\.?\d*)", text, re.IGNORECASE):
        m = re.search(r"[Hh]ouse\s+[Pp]roperty.*?-\s*(\d[\d,]*\.?\d*)", text, re.IGNORECASE)
        data["house_property_loss"] = float(m.group(1).replace(",", ""))
    else:
        data["house_property_loss"] = 0.0

    # Gross total income (Item 8 in Form 16) — ground truth
    data["gross_total_income"] = _find_amount(text, [
        r"[Gg]ross\s+[Tt]otal\s+[Ii]ncome.*?(\d[\d,]*\.?\d*)",
        r"[Gg]ross\s+[Tt]otal.*?\(6\+7\).*?(\d[\d,]*\.?\d*)",
    ])

    return data


# ===================================================================
# STEP 3: GPT TEXT-BASED EXTRACTION
# ===================================================================


_GPT_EXTRACTION_PROMPT = """You are an expert Indian tax professional. Extract all financial data from this Form 16 document.

Return ONLY a valid JSON object with these keys (all annual amounts in INR, use 0 if not found):
{
    "gross_salary": 0,
    "basic_salary": 0,
    "hra_received": 0,
    "special_allowance": 0,
    "lta": 0,
    "professional_tax": 0,
    "epf_employee": 0,
    "income_other_sources": 0,
    "house_property_loss": 0,
    "gross_total_income": 0,
    "exempt_allowances": 0,
    "section_80c": 0,
    "section_80ccd_1b": 0,
    "section_80d": 0,
    "section_80e": 0,
    "section_80g": 0,
    "section_80tta": 0,
    "section_24b": 0,
    "hra_exemption": 0,
    "tds_deducted": 0,
    "employer_nps": 0
}

Rules:
- All values must be numbers (no strings, no currency symbols)
- Basic salary is typically 40-50% of gross if not stated
- "house_property_loss" = if Income from House Property is negative (shown as (-) amount), set this to the POSITIVE magnitude of that loss
- "income_other_sources" = Income from Other Sources (interest, dividends, etc.) — always positive
- "gross_total_income" = Gross Total Income (Item 8 in Form 16) — this is the ground truth
- "exempt_allowances" = total exempt allowances under Section 10 (HRA exemption, LTA, conveyance, etc.)
- Do NOT include any text outside the JSON

FORM 16 TEXT:
"""


def _parse_with_gpt_text(text: str) -> TaxProfile:
    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    resp = client.chat.completions.create(
        model=settings.GPT_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert Indian tax document parser. Return only valid JSON."},
            {"role": "user", "content": _GPT_EXTRACTION_PROMPT + text[:12000]},
        ],
        temperature=0.0,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    return _build_profile(data)


# ===================================================================
# STEP 4: VISION FALLBACK
# ===================================================================


def _parse_with_vision(pdf_bytes: bytes) -> TaxProfile:
    images_b64 = []
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            for page in pdf.pages[:4]:
                img = page.to_image(resolution=200)
                buf = io.BytesIO()
                img.save(buf, format="PNG")
                images_b64.append(base64.b64encode(buf.getvalue()).decode())
    except Exception:
        text = _extract_text(pdf_bytes)
        if text:
            return _parse_with_gpt_text(text)
        raise ValueError("Cannot parse this PDF — neither text nor image extraction succeeded.")

    if not images_b64:
        raise ValueError("PDF has no readable pages.")

    client = OpenAI(api_key=settings.OPENAI_API_KEY)
    content = [
        {"type": "text", "text": _GPT_EXTRACTION_PROMPT.replace("FORM 16 TEXT:", "Analyze these Form 16 page images:")},
    ] + [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        for b64 in images_b64
    ]

    resp = client.chat.completions.create(
        model=settings.GPT_VISION_MODEL,
        messages=[
            {"role": "system", "content": "You are an expert Indian tax document parser. Return only valid JSON."},
            {"role": "user", "content": content},
        ],
        temperature=0.0,
        max_tokens=2000,
        response_format={"type": "json_object"},
    )
    data = json.loads(resp.choices[0].message.content)
    return _build_profile(data)


# ===================================================================
# PROFILE BUILDER
# ===================================================================


def _build_profile(data: Dict) -> TaxProfile:
    gross = float(data.get("gross_salary", 0))
    basic = float(data.get("basic_salary", 0))
    if basic == 0 and gross > 0:
        basic = round(gross * 0.40)

    # ── Compute net other_income correctly ──
    # other_income = (income from other sources) - (house property loss)
    # House property can be negative (loss from home loan interest)
    income_other_sources = float(data.get("income_other_sources", 0))
    raw_other = float(data.get("other_income", 0))
    house_property_loss = float(data.get("house_property_loss", 0))
    hp_income = float(data.get("house_property_income", 0))
    gross_total_income = float(data.get("gross_total_income", 0))

    # If parser found income_other_sources and house_property_loss separately,
    # compute net. Otherwise fall back to raw other_income.
    if income_other_sources > 0 or house_property_loss > 0:
        # Net other income = other sources - house property loss
        net_other_income = income_other_sources - house_property_loss
    elif raw_other != 0:
        net_other_income = raw_other
    else:
        net_other_income = 0

    # Sanity check: if we have gross_total_income from Form 16,
    # use it to validate / correct our computation
    prof_tax = float(data.get("professional_tax", 0))
    std_ded = float(data.get("standard_deduction", 0)) or 50000
    hra_exempt = float(data.get("hra_exemption", 0))
    allowances = float(data.get("exempt_allowances", 0))

    if gross_total_income > 0 and gross > 0:
        # Back-compute what other_income should be:
        # GTI = (gross - allowances - hra - std_ded - prof_tax) + other_income
        implied_salary = gross - allowances - hra_exempt - std_ded - prof_tax
        implied_other = gross_total_income - max(0, implied_salary)
        # If our computed other_income is way off, trust the Form 16 GTI
        if abs(implied_other - net_other_income) > 10000:
            net_other_income = implied_other

    salary = SalaryComponents(
        gross_salary=gross,
        basic_salary=basic,
        hra_received=float(data.get("hra_received", 0)),
        special_allowance=float(data.get("special_allowance", 0)),
        lta=float(data.get("lta", 0)),
        professional_tax=prof_tax,
        epf_employee=float(data.get("epf_employee", 0)),
        other_income=net_other_income,
    )

    deductions = DeductionsClaimed(
        section_80c=float(data.get("section_80c", 0)),
        section_80ccd_1b=float(data.get("section_80ccd_1b", 0)),
        section_80d=float(data.get("section_80d", 0)),
        section_80e=float(data.get("section_80e", 0)),
        section_80g=float(data.get("section_80g", 0)),
        section_80tta=float(data.get("section_80tta", 0)),
        section_24b=float(data.get("section_24b", 0)),
        hra_exemption=hra_exempt,
    )

    return TaxProfile(
        salary=salary,
        deductions=deductions,
        tds_deducted=float(data.get("tds_deducted", 0)),
        employer_nps=float(data.get("employer_nps", 0)),
        has_health_insurance=float(data.get("section_80d", 0)) > 0,
        has_nps=float(data.get("section_80ccd_1b", 0)) > 0,
    )
