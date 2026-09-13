"""
CAMS/KFintech Statement Parser.
4-layer pipeline: pdfplumber text → regex extraction → GPT-4o text → GPT-4o vision fallback.
"""

import io
import json
import re
import base64
from typing import List, Optional
import pdfplumber
from openai import OpenAI

from config.settings import settings
from core.portfolio_schemas import MutualFundHolding, PortfolioData


# ===================================================================
# FUND CATEGORY GUESSER
# ===================================================================

CATEGORY_KEYWORDS = {
    "index": ["nifty", "sensex", "index", "bse", "nse"],
    "large_cap": ["large cap", "largecap", "bluechip", "top 100", "top50"],
    "mid_cap": ["mid cap", "midcap"],
    "small_cap": ["small cap", "smallcap"],
    "flexi_cap": ["flexi", "multi cap", "multicap", "diversified"],
    "elss": ["elss", "tax saver", "tax saving"],
    "debt": ["debt", "bond", "gilt", "liquid", "overnight", "money market", "income"],
    "liquid": ["liquid", "overnight", "money market"],
    "hybrid": ["hybrid", "balanced", "equity savings", "aggressive hybrid"],
    "gold": ["gold", "precious metal"],
}

PLAN_KEYWORDS = {
    "direct": ["direct", "-dir-", "dir plan"],
    "regular": ["regular", "-reg-", "reg plan"],
}


def _guess_category(name: str) -> str:
    name_lower = name.lower()
    for cat, keywords in CATEGORY_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return cat
    return "equity"


def _guess_plan(name: str) -> str:
    name_lower = name.lower()
    for plan, keywords in PLAN_KEYWORDS.items():
        if any(kw in name_lower for kw in keywords):
            return plan
    return "regular"


# ===================================================================
# LAYER 1: PDF TEXT EXTRACTION
# ===================================================================


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    """Extract all text from PDF using pdfplumber."""
    try:
        with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
            return "\n".join(
                page.extract_text() or "" for page in pdf.pages[:10]
            )
    except Exception:
        return ""


# ===================================================================
# LAYER 2: REGEX PARSING (for standard CAMS format)
# ===================================================================


def _parse_cams_regex(text: str) -> List[MutualFundHolding]:
    """
    Parse CAMS consolidated account statement using regex.
    CAMS format has fund names, folio numbers, and balance rows.
    """
    holdings = []

    # Match fund blocks: Fund name followed by Folio and value
    # Pattern: lines with scheme name, followed by units/nav/value lines
    fund_pattern = re.compile(
        r"([A-Z][^\n]{10,80}(?:Fund|Scheme|Plan|ELSS|ETF)[^\n]*)\n"
        r".*?Folio No[.:]?\s*([0-9A-Z/\-]+)"
        r".*?(?:Units|Balance)\s*[:\-]?\s*([\d,]+\.?\d*)"
        r".*?NAV\s*[:\-]?\s*(?:₹\s*)?([\d,]+\.?\d*)"
        r".*?(?:Current Value|Market Value)\s*[:\-]?\s*(?:₹\s*)?([\d,]+\.?\d*)",
        re.DOTALL | re.IGNORECASE,
    )

    for m in fund_pattern.finditer(text):
        try:
            name = m.group(1).strip()
            folio = m.group(2).strip()
            units = float(m.group(3).replace(",", ""))
            nav = float(m.group(4).replace(",", ""))
            current_value = float(m.group(5).replace(",", ""))

            holdings.append(MutualFundHolding(
                name=name,
                folio=folio,
                units=units,
                nav=nav,
                current_value=current_value,
                category=_guess_category(name),
                plan_type=_guess_plan(name),
            ))
        except (ValueError, IndexError):
            continue

    # Simpler fallback: look for value patterns near fund names
    if not holdings:
        holdings = _parse_cams_simple(text)

    return holdings


def _parse_cams_simple(text: str) -> List[MutualFundHolding]:
    """Simpler line-by-line CAMS parser for non-standard formats."""
    holdings = []
    lines = text.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()
        # Look for lines that look like fund names
        if (
            len(line) > 20
            and any(kw in line.lower() for kw in ["fund", "scheme", "elss", "nifty", "etf"])
            and not line.startswith("Total")
        ):
            name = line
            # Look for value in next few lines
            for j in range(i + 1, min(i + 10, len(lines))):
                val_match = re.search(r"₹?\s*([\d,]{5,}\.?\d*)", lines[j])
                if val_match:
                    try:
                        val = float(val_match.group(1).replace(",", ""))
                        if val > 100:  # Must be at least ₹100
                            holdings.append(MutualFundHolding(
                                name=name,
                                current_value=val,
                                category=_guess_category(name),
                                plan_type=_guess_plan(name),
                            ))
                            break
                    except ValueError:
                        pass
        i += 1

    return holdings


# ===================================================================
# LAYER 3: GPT-4o TEXT PARSING
# ===================================================================


def _parse_with_gpt_text(text: str) -> List[MutualFundHolding]:
    """Use GPT to extract mutual fund holdings from raw text."""
    if not settings.OPENAI_API_KEY:
        return []

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    excerpt = text[:6000]  # Limit tokens

    prompt = f"""Extract all mutual fund holdings from this CAMS/KFintech statement text.

TEXT:
{excerpt}

Return a JSON array of holdings. Each object must have:
- name: fund scheme name (string)
- folio: folio number (string, empty if not found)
- units: number of units (float, 0 if not found)
- nav: current NAV in ₹ (float, 0 if not found)
- current_value: current market value in ₹ (float, required)
- invested_amount: amount invested in ₹ (float, 0 if not found)
- plan_type: "direct" or "regular" (infer from name)
- category: one of large_cap/mid_cap/small_cap/flexi_cap/elss/debt/liquid/index/gold/hybrid

Only include holdings with a positive current_value. Return ONLY the JSON array."""

    try:
        resp = client.chat.completions.create(
            model=settings.GPT_MODEL,
            messages=[
                {"role": "system", "content": "You are a financial data extractor. Return only valid JSON."},
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )
        raw = json.loads(resp.choices[0].message.content)
        items = raw if isinstance(raw, list) else raw.get("holdings", raw.get("funds", []))
        return [MutualFundHolding(**item) for item in items if item.get("current_value", 0) > 0]
    except Exception:
        return []


# ===================================================================
# LAYER 4: GPT-4o VISION FALLBACK
# ===================================================================


def _parse_with_gpt_vision(pdf_bytes: bytes) -> List[MutualFundHolding]:
    """Use GPT-4o vision to parse PDF pages as images."""
    if not settings.OPENAI_API_KEY:
        return []

    try:
        from PIL import Image
        import io as _io
    except ImportError:
        return []

    client = OpenAI(api_key=settings.OPENAI_API_KEY)

    # Convert first 3 pages to images
    try:
        with pdfplumber.open(_io.BytesIO(pdf_bytes)) as pdf:
            pages = pdf.pages[:3]
            images_b64 = []
            for page in pages:
                img = page.to_image(resolution=150)
                buf = _io.BytesIO()
                img.save(buf, format="PNG")
                images_b64.append(base64.b64encode(buf.getvalue()).decode())
    except Exception:
        return []

    if not images_b64:
        return []

    content = [
        {
            "type": "text",
            "text": "Extract all mutual fund holdings from this CAMS statement image. Return a JSON object with a 'holdings' array containing objects with: name, folio, units, nav, current_value, invested_amount, plan_type (direct/regular), category.",
        }
    ] + [
        {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{b64}"}}
        for b64 in images_b64
    ]

    try:
        resp = client.chat.completions.create(
            model=settings.GPT_VISION_MODEL,
            messages=[{"role": "user", "content": content}],
            temperature=0,
            response_format={"type": "json_object"},
            max_tokens=2000,
        )
        raw = json.loads(resp.choices[0].message.content)
        items = raw.get("holdings", raw.get("funds", []))
        return [MutualFundHolding(**item) for item in items if item.get("current_value", 0) > 0]
    except Exception:
        return []


# ===================================================================
# MAIN PARSER
# ===================================================================


def parse_cams_statement(pdf_bytes: bytes) -> PortfolioData:
    """
    Parse a CAMS/KFintech consolidated account statement.
    Tries 4 layers in order until holdings are found.
    """
    # Layer 1: Extract text
    text = _extract_pdf_text(pdf_bytes)

    # Layer 2: Regex parsing
    holdings = _parse_cams_regex(text) if text else []

    # Layer 3: GPT text if regex fails
    if not holdings and text:
        holdings = _parse_with_gpt_text(text)

    # Layer 4: Vision fallback
    if not holdings:
        holdings = _parse_with_gpt_vision(pdf_bytes)

    if not holdings:
        raise ValueError(
            "Could not extract mutual fund holdings from the statement. "
            "Please ensure this is a CAMS or KFintech consolidated account statement."
        )

    # Compute totals
    total_current = sum(h.current_value for h in holdings)
    total_invested = sum(h.invested_amount for h in holdings)
    abs_return = (
        round((total_current - total_invested) / total_invested * 100, 2)
        if total_invested > 0 else None
    )

    return PortfolioData(
        holdings=holdings,
        total_current_value=round(total_current),
        total_invested=round(total_invested),
        absolute_return_pct=abs_return,
    )
