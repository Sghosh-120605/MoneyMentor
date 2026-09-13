/**
 * Extended API client — all endpoints for MoneyMentor AI v2.
 */

const API_BASE = process.env.NEXT_PUBLIC_API_URL !== undefined 
    ? process.env.NEXT_PUBLIC_API_URL 
    : (typeof window !== 'undefined' ? "" : "http://localhost:8000");

// ── Helpers ──────────────────────────────────────────────────────────

async function _post(path, body) {
  const res = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `${path} failed (${res.status})`);
  }
  return res.json();
}

async function _get(path, params = {}) {
  const qs = new URLSearchParams(
    Object.fromEntries(Object.entries(params).filter(([, v]) => v !== undefined && v !== null))
  ).toString();
  const url = `${API_BASE}${path}${qs ? `?${qs}` : ""}`;
  const res = await fetch(url);
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Request failed" }));
    throw new Error(err.detail || `${path} failed (${res.status})`);
  }
  return res.json();
}

// ── Tax ──────────────────────────────────────────────────────────────

export async function uploadForm16(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload-form16`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

export async function analyzeTax(taxProfile, options = {}) {
  return _post("/api/analyze-tax", {
    tax_profile: taxProfile,
    rent_paid: options.rent_paid || 0,
    is_metro: options.is_metro !== undefined ? options.is_metro : true,
    age: options.age || 30,
    has_health_insurance: options.has_health_insurance || false,
    has_nps: options.has_nps || false,
    has_home_loan: options.has_home_loan || false,
  });
}

export async function quickAnalyze(profile) {
  return _post("/api/quick-analyze", profile);
}

// ── Portfolio ─────────────────────────────────────────────────────────

export async function uploadCams(file) {
  const formData = new FormData();
  formData.append("file", file);
  const res = await fetch(`${API_BASE}/api/upload-cams`, { method: "POST", body: formData });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: "Upload failed" }));
    throw new Error(err.detail || `Upload failed (${res.status})`);
  }
  return res.json();
}

export async function analyzePortfolio(portfolio) {
  return _post("/api/analyze-portfolio", portfolio);
}

// ── Health Score ──────────────────────────────────────────────────────

export async function getHealthScore(data) {
  return _post("/api/health-score", data);
}

// ── FIRE Planner ──────────────────────────────────────────────────────

export async function getFirePlan(data) {
  return _post("/api/fire-plan", data);
}

// ── Alerts ────────────────────────────────────────────────────────────

export async function getAlerts(params = {}) {
  return _get("/api/alerts", params);
}

// ── Health ────────────────────────────────────────────────────────────

export async function checkHealth() {
  return _get("/api/health");
}

// ── Affordability ────────────────────────────────────────────────────

export async function checkAffordability(data) {
  return _post("/api/affordability-check", data);
}

// ── Budget ────────────────────────────────────────────────────────

export async function getBudgetPlan(data) {
  return _post("/api/budget-plan", data);
}
