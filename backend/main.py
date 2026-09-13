"""MoneyMentor AI — FastAPI Backend Entry Point."""

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from routes.tax_routes import router as tax_router
from routes.portfolio_routes import router as portfolio_router
from routes.health_routes import router as health_router
from routes.fire_routes import router as fire_router
from routes.alerts_routes import router as alerts_router
from routes.demo_routes import router as demo_router
from routes.couples_routes import router as couples_router
from routes.afford_routes import router as afford_router
from routes.budget_routes import router as budget_router
from routes.onboarding_routes import router as onboarding_router
from config.settings import settings

app = FastAPI(
    title="MoneyMentor AI",
    description="CFO for Every Indian — AI-powered tax analysis and financial planning",
    version="2.0.0",
)

# CORS — allow frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        settings.FRONTEND_URL,
        "http://localhost:3000",
        "http://localhost:3001",
    ],
    allow_origin_regex=r"https://.*\.vercel\.app",
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={"success": False, "error": "Internal server error", "detail": str(exc)},
    )


@app.get("/")
async def root():
    return {
        "name": "MoneyMentor AI",
        "version": "2.0.0",
        "status": "running",
        "endpoints": [
            "POST /api/upload-form16   — Parse Form 16 PDF",
            "POST /api/analyze-tax     — Full tax analysis + AI action plan",
            "POST /api/quick-analyze   — Math-only tax analysis",
            "POST /api/upload-cams     — Parse CAMS/KFintech statement",
            "POST /api/analyze-portfolio — Portfolio X-Ray (XIRR, overlap, expense drag)",
            "POST /api/health-score    — 6-dimension money health score",
            "POST /api/fire-plan       — FIRE retirement planner",
            "GET  /api/alerts          — Proactive policy/market alerts",
            "GET  /api/health          — Server health check",
        ],
    }


@app.get("/api/health")
async def health():
    return {"status": "healthy", "version": "2.0.0", "api_key_set": bool(settings.OPENAI_API_KEY)}


app.include_router(tax_router, prefix="/api")
app.include_router(portfolio_router, prefix="/api")
app.include_router(health_router, prefix="/api")
app.include_router(fire_router, prefix="/api")
app.include_router(alerts_router, prefix="/api")
app.include_router(demo_router, prefix="/api")
app.include_router(couples_router, prefix="/api")
app.include_router(afford_router, prefix="/api")
app.include_router(budget_router, prefix="/api")
app.include_router(onboarding_router, prefix="/api")
