"""
Generate realistic mock PDFs for testing MoneyMentor AI uploads.
Uses reportlab (pip install reportlab).

Creates:
  d:/ET/mock_data/form16_arjun.pdf   - Form 16 for Arjun Mehta  (Software Eng, Rs.24L)
  d:/ET/mock_data/form16_sunita.pdf  - Form 16 for Sunita Verma (Teacher, Rs.8L)
  d:/ET/mock_data/cams_arjun.pdf    - CAMS statement for Arjun  (5 mutual funds)
  d:/ET/mock_data/cams_sunita.pdf   - CAMS statement for Sunita (3 mutual funds)

Run: python generate_mock_data.py
"""

import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors

OUT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "mock_data")
os.makedirs(OUT_DIR, exist_ok=True)

W, H = A4


# ── Helpers ────────────────────────────────────────────────────────────────────

class PDFWriter:
    def __init__(self, filename):
        self.c = canvas.Canvas(filename, pagesize=A4)
        self.y = H - 20 * mm
        self.filename = filename

    def new_page(self):
        self.c.showPage()
        self.y = H - 20 * mm

    def check_space(self, needed=15):
        if self.y < needed * mm:
            self.new_page()

    def title(self, text, size=15):
        self.check_space(20)
        self.c.setFont("Helvetica-Bold", size)
        self.c.setFillColor(colors.HexColor("#141450"))
        self.c.drawCentredString(W / 2, self.y, text)
        self.y -= (size + 6) * 0.352 * mm * 2.5
        self.c.setFillColor(colors.black)

    def subtitle(self, text, size=9):
        self.check_space(10)
        self.c.setFont("Helvetica-Oblique", size)
        self.c.setFillColor(colors.HexColor("#555555"))
        self.c.drawCentredString(W / 2, self.y, text)
        self.y -= 7 * mm
        self.c.setFillColor(colors.black)

    def h2(self, text):
        self.check_space(15)
        self.y -= 2 * mm
        self.c.setFont("Helvetica-Bold", 11)
        self.c.setFillColor(colors.HexColor("#1e1e78"))
        self.c.drawString(15 * mm, self.y, text)
        self.y -= 7 * mm
        self.c.setFillColor(colors.black)

    def kv(self, label, value, bold_val=False, indent=0):
        self.check_space(8)
        self.c.setFont("Helvetica", 10)
        self.c.setFillColor(colors.HexColor("#333333"))
        self.c.drawString((15 + indent) * mm, self.y, label + ":")
        if bold_val:
            self.c.setFont("Helvetica-Bold", 10)
            self.c.setFillColor(colors.HexColor("#111111"))
        else:
            self.c.setFont("Helvetica", 10)
        self.c.drawString(105 * mm, self.y, str(value))
        self.y -= 6 * mm
        self.c.setFillColor(colors.black)

    def divider(self):
        self.check_space(8)
        self.c.setStrokeColor(colors.HexColor("#c8c8dc"))
        self.c.setLineWidth(0.4)
        self.c.line(15 * mm, self.y, 195 * mm, self.y)
        self.y -= 5 * mm

    def note(self, text, size=8):
        self.check_space(8)
        self.c.setFont("Helvetica-Oblique", size)
        self.c.setFillColor(colors.HexColor("#888888"))
        self.c.drawCentredString(W / 2, self.y, text)
        self.y -= 6 * mm
        self.c.setFillColor(colors.black)

    def small(self, text, size=9, indent=0):
        self.check_space(8)
        self.c.setFont("Helvetica", size)
        self.c.setFillColor(colors.HexColor("#444444"))
        self.c.drawString((15 + indent) * mm, self.y, text)
        self.y -= 5.5 * mm
        self.c.setFillColor(colors.black)

    def row4(self, col1, col2, col3, col4, bold=False):
        """Print a 4-column transaction row."""
        self.check_space(7)
        font = "Helvetica-Bold" if bold else "Helvetica"
        self.c.setFont(font, 8)
        self.c.setFillColor(colors.HexColor("#333333"))
        self.c.drawString(20 * mm, self.y, col1)
        self.c.drawString(60 * mm, self.y, col2)
        self.c.drawString(110 * mm, self.y, col3)
        self.c.drawString(155 * mm, self.y, col4)
        self.y -= 5 * mm

    def save(self):
        self.c.save()
        print(f"  [OK] {self.filename}")


# ── Form 16 ────────────────────────────────────────────────────────────────────

def make_form16(filename, d):
    p = PDFWriter(filename)

    p.title("FORM 16 - Certificate of TDS on Salary")
    p.title("FY 2025-26  |  Assessment Year 2026-27", size=11)
    p.subtitle("[Under Section 203 of the Income Tax Act, 1961]")
    p.divider()

    p.h2("PART A - Employer & Employee Details")
    p.kv("Name of Employee", d["name"])
    p.kv("PAN of Employee", d["pan"])
    p.kv("Name of Employer", d["employer"])
    p.kv("TAN of Employer", d["tan"])
    p.kv("Period of Employment", "01-Apr-2025 to 31-Mar-2026")
    p.kv("Total TDS Deducted & Deposited", f"Rs. {d['tds']:,}", bold_val=True)
    p.divider()

    p.h2("PART B - Computation of Income & Tax")

    p.h2("1. Gross Salary")
    p.kv("(a) Salary as per Section 17(1)", f"Rs. {d['gross_salary']:,}", indent=3)
    p.kv("(b) Value of Perquisites u/s 17(2)", "Rs. 0", indent=3)
    p.kv("(c) Profits in lieu of salary 17(3)", "Rs. 0", indent=3)
    p.kv("   Total Gross Salary", f"Rs. {d['gross_salary']:,}", bold_val=True)
    p.divider()

    p.h2("2. Allowances Exempt u/s 10")
    p.kv("HRA Exemption u/s 10(13A)", f"Rs. {d['hra_exemption']:,}", indent=3)
    p.kv("LTA Exemption u/s 10(5)", f"Rs. {d['lta']:,}", indent=3)
    total_exempt = d['hra_exemption'] + d['lta']
    p.kv("   Total Exempt Allowances", f"Rs. {total_exempt:,}", bold_val=True)
    p.divider()

    p.h2("3. Deductions u/s 16")
    p.kv("Standard Deduction u/s 16(ia)", f"Rs. {d['std_deduction']:,}", indent=3)
    p.kv("Professional Tax u/s 16(iii)", f"Rs. {d['prof_tax']:,}", indent=3)
    p.divider()

    net_sal = d['gross_salary'] - total_exempt - d['std_deduction'] - d['prof_tax']
    p.kv("4. Income Chargeable under 'Salaries'", f"Rs. {net_sal:,}", bold_val=True)
    p.divider()

    p.h2("5. Deductions under Chapter VI-A")
    p.kv("Section 80C (EPF + ELSS + PPF)", f"Rs. {d['sec80c']:,}", indent=3)
    p.kv("Section 80CCD(1B) - NPS", f"Rs. {d['sec80ccd']:,}", indent=3)
    p.kv("Section 80D - Health Insurance", f"Rs. {d['sec80d']:,}", indent=3)
    p.kv("Section 24(b) - Home Loan Interest", f"Rs. {d['sec24b']:,}", indent=3)
    total_ded = d['sec80c'] + d['sec80ccd'] + d['sec80d'] + d['sec24b']
    p.kv("   Total Chapter VI-A Deductions", f"Rs. {total_ded:,}", bold_val=True)
    p.divider()

    taxable = max(0, net_sal - total_ded)
    p.kv("6. Total Taxable Income", f"Rs. {taxable:,}", bold_val=True)
    p.kv("7. Tax on Total Income", f"Rs. {d['tax_payable']:,}")
    p.kv("8. Education Cess @ 4%", f"Rs. {int(d['tax_payable'] * 0.04):,}")
    total_tax = int(d['tax_payable'] * 1.04)
    p.kv("9. Total Tax Payable (incl. cess)", f"Rs. {total_tax:,}", bold_val=True)
    p.kv("10. Total TDS Deducted", f"Rs. {d['tds']:,}", bold_val=True)
    refund = d['tds'] - total_tax
    if refund > 0:
        p.kv("11. Tax Refund Due", f"Rs. {refund:,}", bold_val=True)
    else:
        p.kv("11. Balance Tax Payable", f"Rs. {-refund:,}", bold_val=True)
    p.divider()

    p.y -= 4 * mm
    p.note(
        "Certified that a sum of Rs. " + f"{d['tds']:,}" +
        " has been deducted and deposited to the Central Government."
    )
    p.note("Generated for demonstration purposes - MoneyMentor AI Demo")

    p.save()


# ── CAMS ───────────────────────────────────────────────────────────────────────

def make_cams(filename, d):
    p = PDFWriter(filename)

    p.title("CONSOLIDATED ACCOUNT STATEMENT (CAS)")
    p.title("CAMS / KFintech  |  Period: 01-Apr-2025 to 31-Mar-2026", size=10)
    p.divider()

    p.kv("Investor Name", d["name"])
    p.kv("PAN", d["pan"])
    p.kv("Email", d["email"])
    p.kv("Mobile", d["mobile"])
    p.divider()

    total_current = 0
    total_invested = 0

    for fund in d["funds"]:
        p.check_space(60)
        p.h2(fund["name"])
        p.kv("Folio No.", fund["folio"], indent=2)
        p.kv("AMC", fund["amc"], indent=2)
        p.kv("Plan", fund["plan"], indent=2)
        p.kv("Category", fund["category"], indent=2)
        p.kv("Units as on 31-Mar-2026", f"{fund['units']:.3f}", indent=2)
        p.kv("NAV as on 31-Mar-2026", f"Rs. {fund['nav']:.4f}", indent=2)
        p.kv("Current Market Value", f"Rs. {fund['current_value']:,.2f}", bold_val=True, indent=2)
        p.kv("Cost / Invested Amount", f"Rs. {fund['invested']:,.2f}", indent=2)
        gain = fund['current_value'] - fund['invested']
        gain_pct = (gain / fund['invested'] * 100) if fund['invested'] > 0 else 0
        p.kv("Unrealised Gain / Loss", f"Rs. {gain:,.2f}  ({gain_pct:.1f}%)", bold_val=True, indent=2)

        p.y -= 2 * mm
        p.small("Transaction History:", indent=2)
        p.row4("Date", "Transaction Type", "Units", "Amount (Rs.)", bold=True)
        for txn in fund.get("txns", []):
            p.row4(
                txn["date"],
                txn["type"],
                f"{txn['units']:.3f}",
                f"{txn['amount']:,.0f}",
            )

        total_current += fund["current_value"]
        total_invested += fund["invested"]
        p.divider()

    p.check_space(30)
    p.h2("PORTFOLIO SUMMARY")
    p.kv("Total Current Market Value", f"Rs. {total_current:,.2f}", bold_val=True)
    p.kv("Total Cost / Invested Amount", f"Rs. {total_invested:,.2f}", bold_val=True)
    gain = total_current - total_invested
    gain_pct = (gain / total_invested * 100) if total_invested > 0 else 0
    p.kv("Total Unrealised Gain / Loss", f"Rs. {gain:,.2f}  ({gain_pct:.1f}%)", bold_val=True)
    p.divider()
    p.note("This statement is generated for demonstration purposes - MoneyMentor AI Demo")

    p.save()


# ── Data ───────────────────────────────────────────────────────────────────────

FORM16_ARJUN = {
    "name": "Arjun Mehta", "pan": "ABCPM3421K",
    "employer": "TechCorp India Pvt Ltd", "tan": "BLRT12345A",
    "gross_salary": 2400000, "hra_exemption": 230400, "lta": 48000,
    "std_deduction": 50000, "prof_tax": 2400,
    "sec80c": 34800, "sec80ccd": 0, "sec80d": 18000, "sec24b": 0,
    "tax_payable": 280380, "tds": 320000,
}

FORM16_SUNITA = {
    "name": "Sunita Verma", "pan": "ABCPV7812Q",
    "employer": "Kendriya Vidyalaya Sangathan", "tan": "DLRT98765B",
    "gross_salary": 800000, "hra_exemption": 64000, "lta": 16000,
    "std_deduction": 50000, "prof_tax": 2400,
    "sec80c": 11600, "sec80ccd": 0, "sec80d": 0, "sec24b": 0,
    "tax_payable": 10620, "tds": 28000,
}

CAMS_ARJUN = {
    "name": "Arjun Mehta", "pan": "ABCPM3421K",
    "email": "arjun.mehta@techcorp.in", "mobile": "9876543210",
    "funds": [
        {
            "name": "Parag Parikh Flexi Cap Fund - Direct Plan - Growth",
            "folio": "9876543/01", "amc": "PPFAS Mutual Fund",
            "plan": "Direct", "category": "Flexi Cap",
            "units": 892.401, "nav": 78.9200,
            "current_value": 704499.60, "invested": 500000.00,
            "txns": [
                {"date": "05-Apr-2025", "type": "Purchase (SIP)", "units": 12.456, "amount": 10000},
                {"date": "05-May-2025", "type": "Purchase (SIP)", "units": 11.982, "amount": 10000},
                {"date": "05-Jun-2025", "type": "Purchase (SIP)", "units": 12.134, "amount": 10000},
            ],
        },
        {
            "name": "Axis Bluechip Fund - Direct Plan - Growth",
            "folio": "9876543/02", "amc": "Axis Mutual Fund",
            "plan": "Direct", "category": "Large Cap",
            "units": 1245.600, "nav": 52.3400,
            "current_value": 652015.40, "invested": 500000.00,
            "txns": [
                {"date": "10-Apr-2025", "type": "Purchase (SIP)", "units": 18.901, "amount": 10000},
                {"date": "10-May-2025", "type": "Purchase (SIP)", "units": 19.234, "amount": 10000},
            ],
        },
        {
            "name": "Mirae Asset Emerging Bluechip - Regular Plan - Growth",
            "folio": "9876543/03", "amc": "Mirae Asset Mutual Fund",
            "plan": "Regular", "category": "Mid Cap",
            "units": 432.100, "nav": 122.4000,
            "current_value": 528890.40, "invested": 350000.00,
            "txns": [
                {"date": "15-Mar-2026", "type": "Purchase (Lump Sum)", "units": 82.000, "amount": 100000},
            ],
        },
        {
            "name": "UTI Nifty Next 50 Index Fund - Direct Plan - Growth",
            "folio": "9876543/04", "amc": "UTI Mutual Fund",
            "plan": "Direct", "category": "Index Fund",
            "units": 1876.300, "nav": 42.1800,
            "current_value": 791305.40, "invested": 600000.00,
            "txns": [
                {"date": "01-Apr-2025", "type": "Purchase (SIP)", "units": 23.456, "amount": 10000},
                {"date": "01-May-2025", "type": "Purchase (SIP)", "units": 22.891, "amount": 10000},
            ],
        },
        {
            "name": "ICICI Pru Short Term Debt Fund - Regular Plan - Growth",
            "folio": "9876543/05", "amc": "ICICI Prudential Mutual Fund",
            "plan": "Regular", "category": "Short Duration Debt",
            "units": 8234.500, "nav": 30.2200,
            "current_value": 248746.90, "invested": 220000.00,
            "txns": [
                {"date": "20-Sep-2025", "type": "Purchase (Lump Sum)", "units": 3200.000, "amount": 96000},
            ],
        },
    ],
}

CAMS_SUNITA = {
    "name": "Sunita Verma", "pan": "ABCPV7812Q",
    "email": "sunita.verma@kvs.gov.in", "mobile": "9812345678",
    "funds": [
        {
            "name": "UTI Nifty 50 Index Fund - Direct Plan - Growth",
            "folio": "1234567/01", "amc": "UTI Mutual Fund",
            "plan": "Direct", "category": "Index Fund",
            "units": 245.670, "nav": 152.3400,
            "current_value": 374198.78, "invested": 300000.00,
            "txns": [
                {"date": "05-Apr-2025", "type": "Purchase (SIP)", "units": 6.547, "amount": 1000},
                {"date": "05-May-2025", "type": "Purchase (SIP)", "units": 6.423, "amount": 1000},
                {"date": "05-Jun-2025", "type": "Purchase (SIP)", "units": 6.612, "amount": 1000},
            ],
        },
        {
            "name": "SBI Bluechip Fund - Regular Plan - Growth",
            "folio": "1234567/02", "amc": "SBI Funds Management",
            "plan": "Regular", "category": "Large Cap",
            "units": 88.120, "nav": 82.4500,
            "current_value": 72645.10, "invested": 60000.00,
            "txns": [
                {"date": "01-Apr-2025", "type": "Purchase (SIP)", "units": 11.234, "amount": 1000},
                {"date": "01-May-2025", "type": "Purchase (SIP)", "units": 11.098, "amount": 1000},
            ],
        },
        {
            "name": "SBI Liquid Fund - Regular Plan - Growth",
            "folio": "1234567/03", "amc": "SBI Funds Management",
            "plan": "Regular", "category": "Liquid",
            "units": 40.983, "nav": 3662.4000,
            "current_value": 150142.15, "invested": 140000.00,
            "txns": [
                {"date": "15-Mar-2026", "type": "Purchase (Lump Sum)", "units": 5.456, "amount": 20000},
            ],
        },
    ],
}


# ── Main ───────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    print(f"\nGenerating mock PDFs in: {OUT_DIR}\n")
    make_form16(os.path.join(OUT_DIR, "form16_arjun.pdf"), FORM16_ARJUN)
    make_form16(os.path.join(OUT_DIR, "form16_sunita.pdf"), FORM16_SUNITA)
    make_cams(os.path.join(OUT_DIR, "cams_arjun.pdf"), CAMS_ARJUN)
    make_cams(os.path.join(OUT_DIR, "cams_sunita.pdf"), CAMS_SUNITA)
    print("\n4 mock files ready in d:/ET/mock_data/")
    print("   form16_arjun.pdf  - Software Engineer, Rs.24L salary")
    print("   form16_sunita.pdf - Teacher, Rs.8L salary")
    print("   cams_arjun.pdf    - 5 mutual funds, Rs.32L portfolio")
    print("   cams_sunita.pdf   - 3 mutual funds, Rs.6L portfolio")
