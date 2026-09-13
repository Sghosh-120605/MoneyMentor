# MoneyMentor AI 💰
*Your Personal AI CFO — Built for the ET AI Hackathon 2026*

> **The Problem:** Over 95% of Indians overpay their taxes or mismanage their investments simply because personal finance is too complex, filled with jargon, and largely relies on expensive advisors.  
> **The Solution:** MoneyMentor AI. Think of it as a personalized, Chief Financial Officer (CFO) in your pocket—an AI trained strictly on Indian financial context (FY 2025-26) to manage everything from your Form 16 to your early retirement.

---

## Table of Contents
1. [The Vision](#the-vision)
2. [The 9-in-1 Financial Arsenal](#the-9-in-1-financial-arsenal)
3. [Under the Hood: Tech & Architecture](#under-the-hood-tech--architecture)
4. [Data Privacy Promise](#data-privacy-promise)
5. [Local Development Setup](#local-development-setup)
6. [Core API Endpoints](#core-api-endpoints)
7. [Acknowledgements](#acknowledgements)

---

## The Vision
We built MoneyMentor AI primarily because **personal finance should not be a black box**. Traditional advisory is expensive, and DIY calculations via spreadsheets lead to errors. By marrying a hard-coded mathematical Indian tax engine with the intuitive reasoning power of state-of-the-art AI, we’ve made world-class financial planning accessible to the average salaried individual. It's fast, hyper-personalized, and beautifully designed.

---

## The 9-in-1 Financial Arsenal
MoneyMentor AI acts as a super-app housing a suite of interconnected tools. To prevent feature-paralysis, an intelligent **AI Onboarding Flow** dynamically directs users to the most urgent tool based on their current financial priority.

1. **Tax Wizard (Flagship)** 🪄  
   Upload your Form 16 PDF and let our 4-layer parser (OCR + AI Vision) rip through it. The engine calculates your exact tax liability under the Old vs. New Regimes, flags missed deductions (80C, 80D, HRA), and generates a plain-English, actionable plan to save ₹10,000s next year.
2. **AI Budget Planner** 📊  
   Applies the 50/30/20 rule to your income and generates brutal, instant "quick wins" to cut the fluff and optimize your monthly expenses.
3. **Portfolio X-Ray** 🔍  
   Upload your CAMS / KFintech statements to uncover hidden overlap in your mutual funds, check your real XIRR, and eliminate funds with a high expense drag.
4. **F.I.R.E. Planner** 🔥  
   Want to retire at 45? This calculates exactly what corpus you need adjusted for inflation and reverse-engineers a monthly SIP roadmap to get you there.
5. **Couple's Planner** 👩‍❤️‍👨  
   A unique calculator optimizing which partner should claim specific deductions (home loans, children's tuition) to maximize the *combined* household tax savings.
6. **Afford Advisor** 🛍  
   Thinking about buying that new iPhone or taking a Europe trip? Tell the AI the cost. It will evaluate your cash flow and give you a cold verdict: *Buy, Wait, or Skip*.
7. **Money Health Score** 🩺  
   A rapid 2-minute diagnostic generating a financial fitness score based on your liquidity, savings rate, and debt-to-income ratio.
8. **Proactive Alerts** 🔔  
   Personalized pings on critical macroeconomic shifts (like RBI rate hikes affecting your specific home loan or new SEBI guidelines).
9. **Indian Market Intelligence** 📈  
   A live dashboard tracking critical equity indices (Nifty 50, Sensex) and commodity patterns at a glance.

---

## Under the Hood: Tech & Architecture

We refused to compromise on performance. The platform leverages modern architectures to keep analysis fast (sub-60 seconds for full AI reports) and interactions buttery smooth.

**Frontend:**
- **Framework:** Next.js 14 (React)
- **Styling:** Tailwind CSS (Premium Dark Mode with Glassmorphism)
- **Animations:** Framer Motion (for dynamic UI components)

**Backend:**
- **Framework:** Python FastAPI
- **The Core:** A custom deterministic Indian Tax Engine (FY 2025-26 rules mapping marginal relief, cess, surcharge, and Section 87A rebate).
- **AI Integration:** OpenAI GPT-4o & GPT-4o Vision for complex heuristics, advisory summarizations, and OCR fallbacks.
- **Parsing Toolkit:** `pdfplumber` paired with smart RegEx logic.

---

## Data Privacy Promise
Financial data is highly sensitive. MoneyMentor AI was built with a **Zero-Storage architecture**. 
Whenever you upload a Form 16 or CAMS statement:
- The file is converted entirely in-memory.
- Analyzed in real-time.
- And instantly purged. 
**Absolutely nothing is saved to a database or written to our servers.**

---

## Local Development Setup

Want to spin this up locally and contribute? Follow these comprehensive step-by-step instructions.

### Prerequisites
Before you start, ensure you have the following installed on your machine:
- **Node.js** (v18 or higher)
- **Python** (v3.9 or higher)
- **Git**

### 1. Clone the Repository
First, clone the project to your local machine:
```bash
git clone https://github.com/your-username/moneymentor-ai.git
cd moneymentor-ai
```

### 2. Backend Setup (FastAPI)
The backend handles the deterministic tax engine and AI integrations.

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv venv
   
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```
3. Install the required Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
4. Set up your environment variables:
   ```bash
   cp .env.example .env 
   ```
5. Open the newly created `.env` file and add your OpenAI API key:
   ```env
   OPENAI_API_KEY=sk-your-openai-key-here
   GPT_MODEL=gpt-4o-mini
   FRONTEND_URL=http://localhost:3000
   ```
6. Start the FastAPI development server:
   ```bash
   python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload
   ```
   *(The backend API and Swagger UI will be live at `http://localhost:8000/docs`)*

### 3. Frontend Setup (Next.js)
The frontend serves the premium glassmorphism UI.

1. Open a **new terminal tab/window** and navigate to the frontend directory:
   ```bash
   cd frontend
   ```
2. Install the Node dependencies:
   ```bash
   npm install
   ```
3. Boot up the Next.js development server:
   ```bash
   npm run dev
   ```
   *(The frontend application will be rolling at `http://localhost:3000`)*

---

## Core API Endpoints

The backend exposes a highly modular REST API. Here are the stars of the show:

| HTTP Method | Endpoint | Description |
| :--- | :--- | :--- |
| **POST** | `/api/upload-form16` | Secure, in-memory PDF parsing returning a structured JSON tax profile. |
| **POST** | `/api/analyze-tax` | Runs the full deterministic engine + GPT-4o advisory plan. |
| **POST** | `/api/quick-analyze` | Fast, math-only analysis (bypassing AI logic for speed). |
| **POST** | `/api/upload-cams` | Parses CAMS/KFintech statements for Portfolio X-Ray. |
| **POST** | `/api/health-score` | Computes the 6-dimensional Money Health metric. |
| **POST** | `/api/fire-plan` | Calculates SIP roadmaps for early retirement. |
| **GET** | `/api/health` | Standard server & API key validation health check. |

---

## Acknowledgements

Built from the ground up for the **ET AI Hackathon 2026** 🇮🇳. 
*Empowering India, one intelligent financial decision at a time.*
