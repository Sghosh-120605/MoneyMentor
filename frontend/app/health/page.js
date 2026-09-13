"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { getHealthScore } from "../../lib/api";

export default function HealthPage() {
  const [form, setForm] = useState({
    annual_income: "", monthly_expenses: "", emergency_fund: "",
    life_cover: "", health_cover: "", dependants: 1,
    total_investments: "", equity_pct: 60, debt_pct: 30, gold_pct: 10,
    monthly_emi: "", avg_loan_rate: 0,
    missed_deductions_count: 0, tax_potential_savings: 0,
    current_corpus: "", monthly_sip: "", age: 30, retirement_age: 60,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const num = (v) => parseFloat(v) || 0;

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null);
    try {
      const payload = Object.fromEntries(Object.entries(form).map(([k, v]) => [k, num(v)]));
      setResult(await getHealthScore(payload));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const scoreColor = (s) => s >= 70 ? "text-emerald-400" : s >= 50 ? "text-amber-400" : "text-[#E4002B]";
  const scoreBg = (s) => s >= 70 ? "bg-emerald-500" : s >= 50 ? "bg-amber-500" : "bg-[#E4002B]";

  const Field = ({ label, field, placeholder = "0" }) => (
    <label className="flex items-center justify-between py-2 group" style={{ borderBottom: '1px solid var(--border)' }}>
      <span className="font-mono text-[10px] tracking-wider uppercase transition-colors" style={{ color: 'var(--text-muted)' }}>{label}</span>
      <input type="number" placeholder={placeholder} value={form[field] || ""} onChange={(e) => set(field, e.target.value)}
        className="input-terminal text-right w-28" />
    </label>
  );

  return (
    <div className="space-y-8">
      <div>
        <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Financial Fitness</span>
        <h1 className="text-massive text-4xl md:text-6xl">MONEY<br/>HEALTH</h1>
        <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>6-dimension financial fitness score · 2 min quiz</p>
      </div>

      {!result ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          {[
            { title: "Income & Expenses", fields: [["Annual Income", "annual_income", "1200000"], ["Monthly Expenses", "monthly_expenses", "50000"], ["Age", "age", "30"]] },
            { title: "Emergency Fund", fields: [["Emergency Savings", "emergency_fund", "300000"]] },
            { title: "Insurance", fields: [["Life Cover", "life_cover", "10000000"], ["Health Cover", "health_cover", "500000"], ["Dependants", "dependants", "1"]] },
            { title: "Investments", fields: [["Total Investments", "total_investments", "500000"], ["Equity %", "equity_pct", "60"], ["Debt %", "debt_pct", "30"], ["Retirement Corpus", "current_corpus", "0"], ["Monthly SIP", "monthly_sip", "10000"], ["Retirement Age", "retirement_age", "60"]] },
            { title: "Debt & Loans", fields: [["Monthly EMI", "monthly_emi", "0"], ["Avg Loan Rate %", "avg_loan_rate", "8.5"]] },
          ].map(({ title, fields }) => (
            <div key={title} className="p-6" style={{ border: '1px solid var(--border)' }}>
              <p className="font-mono text-[10px] tracking-wider uppercase mb-4" style={{ color: 'var(--text-muted)' }}>{title}</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8">
                {fields.map(([label, field, ph]) => <Field key={field} label={label} field={field} placeholder={ph} />)}
              </div>
            </div>
          ))}
          {error && <p className="font-mono text-[10px] text-[#E4002B]">⚠ {error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full text-center disabled:opacity-50">
            {loading ? "Computing..." : "Calculate Health Score →"}
          </button>
        </form>
      ) : (
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          <div className="p-10 text-center" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] tracking-wider mb-4" style={{ color: 'var(--text-faint)' }}>Your Money Health Score</p>
            <p className={`text-massive text-[120px] leading-none ${scoreColor(result.overall_score)}`}>{result.overall_score}</p>
            <p className="font-mono text-[10px] mt-2" style={{ color: 'var(--text-faint)' }}>/100 · Grade {result.grade}</p>
            {result.projected_score_after_actions && (
              <p className="text-editorial text-lg mt-4" style={{ color: 'var(--text-muted)' }}>
                After actions → <span className="text-emerald-400">{result.projected_score_after_actions}/100</span>
              </p>
            )}
          </div>

          <div className="p-6 space-y-4" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Dimension Breakdown</p>
            {result.dimensions?.map((d) => (
              <div key={d.name}>
                <div className="flex items-center justify-between mb-1">
                  <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{d.name}</span>
                  <span className={`text-sm font-bold font-mono ${scoreColor(d.score)}`}>{d.score}/100</span>
                </div>
                <div className="h-1 overflow-hidden" style={{ background: 'var(--border)' }}>
                  <motion.div initial={{ width: 0 }} animate={{ width: `${d.score}%` }} transition={{ duration: 0.8, delay: 0.2 }}
                    className={`h-full ${scoreBg(d.score)}`} />
                </div>
                <p className="text-[10px] mt-1" style={{ color: 'var(--text-faint)' }}>{d.improvement_tip}</p>
              </div>
            ))}
          </div>

          {result.improvement_actions?.length > 0 && (
            <div className="p-6 space-y-3" style={{ border: '1px solid var(--border)' }}>
              <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-2">Top Actions</p>
              {result.improvement_actions.map((a, i) => (
                <div key={i} className="p-4 hover:opacity-80 transition-all" style={{ border: '1px solid var(--border)' }}>
                  <div className="flex justify-between items-start">
                    <p className="text-sm font-medium">{a.dimension}</p>
                    <span className="font-mono text-[10px] text-[#E4002B]">+{a.score_impact} pts</span>
                  </div>
                  <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{a.tip}</p>
                </div>
              ))}
            </div>
          )}
          <button onClick={() => setResult(null)} className="btn-bracket text-[9px]">← Recalculate</button>
        </motion.div>
      )}
    </div>
  );
}
