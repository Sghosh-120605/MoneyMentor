"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { checkAffordability } from "../../lib/api";

const fmt = (n) => "₹" + Math.round(n || 0).toLocaleString("en-IN");
const PRESETS = [
  { name: "Car", cost: 1200000, tenure: 5, rate: 8.5, down: 20 },
  { name: "Bike", cost: 250000, tenure: 3, rate: 9.5, down: 20 },
  { name: "iPhone", cost: 150000, tenure: 1, rate: 16, down: 0 },
  { name: "Laptop", cost: 120000, tenure: 1, rate: 16, down: 0 },
  { name: "Home", cost: 6000000, tenure: 20, rate: 8.0, down: 20 },
  { name: "Vacation", cost: 200000, tenure: 1, rate: 14, down: 0 },
];

export default function AffordPage() {
  const [form, setForm] = useState({
    item_name: "Car", item_cost: "", down_payment_pct: 20,
    loan_tenure_years: 5, loan_interest_rate: 8.5,
    monthly_income: "", monthly_expenses: "", existing_emis: "",
    total_savings: "", monthly_sip: "", age: 30, retirement_age: 60,
    emergency_fund_target_months: 6,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const loadPreset = (p) => {
    set("item_name", p.name);
    set("item_cost", p.cost);
    set("loan_tenure_years", p.tenure);
    set("loan_interest_rate", p.rate);
    set("down_payment_pct", p.down);
  };

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null);
    try {
      const payload = {};
      Object.entries(form).forEach(([k, v]) => {
        payload[k] = typeof v === "string" ? (parseFloat(v) || 0) : v;
      });
      payload.item_name = form.item_name;
      setResult(await checkAffordability(payload));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = () => {
    setForm({
      item_name: "Car", item_cost: 1200000, down_payment_pct: 20,
      loan_tenure_years: 5, loan_interest_rate: 8.5,
      monthly_income: 100000, monthly_expenses: 45000, existing_emis: 8000,
      total_savings: 500000, monthly_sip: 15000, age: 28, retirement_age: 55,
      emergency_fund_target_months: 6,
    });
    setResult(null);
  };

  const verdictColor = (c) => c === "green" ? "text-emerald-400" : c === "amber" ? "text-amber-400" : "text-[#E4002B]";
  const verdictBorder = (c) => c === "green" ? "border-emerald-500/30" : c === "amber" ? "border-amber-500/30" : "border-[#E4002B]/30";

  const Field = ({ label, field, placeholder = "0", suffix = "" }) => (
    <label className="flex items-center justify-between py-2 group" style={{ borderBottom: '1px solid var(--border)' }}>
      <span className="font-mono text-[10px] tracking-wider uppercase transition-colors" style={{ color: 'var(--text-muted)' }}>{label}</span>
      <div className="flex items-center gap-1">
        <input type="number" placeholder={placeholder} value={form[field] || ""} onChange={(e) => set(field, e.target.value)}
          className="input-terminal text-right w-28" />
        {suffix && <span className="font-mono text-[8px]" style={{ color: 'var(--text-faint)' }}>{suffix}</span>}
      </div>
    </label>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Affordability Advisor</span>
          <h1 className="text-massive text-4xl md:text-6xl">SHOULD I<br/>BUY THIS?</h1>
          <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>
            Find out if you can afford a big purchase — or how long to wait
          </p>
        </div>
        <button onClick={loadDemo} className="btn-bracket text-[9px]">Load Demo</button>
      </div>

      {!result ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          {/* Quick presets */}
          <div>
            <p className="font-mono text-[10px] tracking-wider uppercase mb-3" style={{ color: 'var(--text-muted)' }}>Quick Select</p>
            <div className="flex flex-wrap gap-2">
              {PRESETS.map((p) => (
                <button key={p.name} type="button" onClick={() => loadPreset(p)}
                  className="px-4 py-2 font-mono text-[10px] uppercase border transition-all"
                  style={{
                    borderColor: form.item_name === p.name ? '#E4002B' : 'var(--border)',
                    color: form.item_name === p.name ? '#E4002B' : 'var(--text-muted)',
                    background: form.item_name === p.name ? 'rgba(228,0,43,0.05)' : 'transparent',
                  }}>
                  {p.name}
                </button>
              ))}
            </div>
          </div>

          {/* Purchase details */}
          <div className="p-6" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-4">What You Want to Buy</p>
            <div className="space-y-1">
              <label className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                <span className="font-mono text-[10px] tracking-wider uppercase" style={{ color: 'var(--text-muted)' }}>Item Name</span>
                <input type="text" value={form.item_name} onChange={(e) => set("item_name", e.target.value)}
                  className="bg-transparent text-right text-sm outline-none border-b border-transparent focus:border-[#E4002B]" style={{ color: 'var(--text-primary)' }} placeholder="Car" />
              </label>
              <Field label="Total Price" field="item_cost" placeholder="1200000" suffix="₹" />
              <Field label="Down Payment" field="down_payment_pct" placeholder="20" suffix="%" />
              <Field label="Loan Tenure" field="loan_tenure_years" placeholder="5" suffix="yrs" />
              <Field label="Interest Rate" field="loan_interest_rate" placeholder="8.5" suffix="%" />
            </div>
          </div>

          {/* Financial profile */}
          <div className="p-6" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] tracking-wider uppercase mb-4" style={{ color: 'var(--text-muted)' }}>Your Financial Profile</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
              <Field label="Monthly Income" field="monthly_income" placeholder="100000" suffix="₹" />
              <Field label="Monthly Expenses" field="monthly_expenses" placeholder="45000" suffix="₹" />
              <Field label="Existing EMIs" field="existing_emis" placeholder="0" suffix="₹/mo" />
              <Field label="Total Savings" field="total_savings" placeholder="500000" suffix="₹" />
              <Field label="Monthly SIP" field="monthly_sip" placeholder="15000" suffix="₹/mo" />
              <Field label="Age" field="age" placeholder="30" />
            </div>
          </div>

          {error && <p className="font-mono text-[10px] text-[#E4002B]">⚠ {error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full text-center disabled:opacity-50">
            {loading ? "Analysing..." : `Can I Afford This ${form.item_name}? →`}
          </button>
        </form>
      ) : (
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          {/* Verdict */}
          <div className={`p-8 border-2 ${verdictBorder(result.verdict_color)} relative`}>
            <div className="absolute -top-px left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-current to-transparent opacity-30" />
            <div className="flex items-start justify-between">
              <div>
                <p className="font-mono text-[9px] tracking-wider mb-3" style={{ color: 'var(--text-faint)' }}>Verdict for "{result.item.name}"</p>
                <p className={`text-massive text-4xl md:text-5xl ${verdictColor(result.verdict_color)}`}>{result.verdict}</p>
                <p className="text-sm mt-3 max-w-lg leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{result.verdict_detail}</p>
              </div>
              <div className="text-right shrink-0 ml-8">
                <p className="text-massive text-3xl">{fmt(result.item.cost)}</p>
                <p className="font-mono text-[9px] mt-1" style={{ color: 'var(--text-faint)' }}>{result.item.name} price</p>
              </div>
            </div>
          </div>

          {/* Purchase breakdown */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {[
              ["Monthly EMI", fmt(result.item.monthly_emi), ""],
              ["Down Payment", fmt(result.item.down_payment), ""],
              ["Total Interest", fmt(result.item.total_interest), "text-amber-400"],
              ["Total Cost", fmt(result.item.total_cost), "text-[#E4002B]"],
            ].map(([label, value, color], i) => (
              <div key={i} className="p-5" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                <p className="font-mono text-[9px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-faint)' }}>{label}</p>
                <p className={`text-massive text-xl ${color}`} style={!color ? { color: 'var(--text-primary)' } : {}}>{value}</p>
              </div>
            ))}
          </div>

          {/* Impact gauges */}
          <div className="p-6 space-y-5" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] text-[#E4002B] tracking-wider">Financial Impact Analysis</p>

            {/* DTI Gauge */}
            <div>
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Debt-to-Income Ratio</span>
                <div className="font-mono text-[12px]">
                  <span style={{ color: 'var(--text-faint)' }}>{result.impact.current_dti}%</span>
                  <span className="mx-2" style={{ color: 'var(--text-faint)' }}>→</span>
                  <span className={result.impact.dti_healthy ? "text-emerald-400" : "text-[#E4002B]"}>{result.impact.new_dti}%</span>
                </div>
              </div>
              <div className="h-2 overflow-hidden relative" style={{ background: 'var(--border)' }}>
                <div className="absolute h-full transition-all" style={{
                  width: `${Math.min(100, result.impact.new_dti * 2)}%`,
                  background: result.impact.new_dti <= 35 ? '#34d399' : result.impact.new_dti <= 50 ? '#fbbf24' : '#E4002B',
                }} />
                <div className="absolute h-full w-px bg-white/30" style={{ left: '70%' }} title="35% healthy limit" />
              </div>
              <p className="font-mono text-[8px] mt-1" style={{ color: 'var(--text-faint)' }}>
                Healthy: &lt;35% | Caution: 35-50% | Danger: &gt;50%
              </p>
            </div>

            {/* Surplus */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Monthly Surplus</span>
                <div className="font-mono text-[12px]">
                  <span style={{ color: 'var(--text-faint)' }}>{fmt(result.impact.current_surplus)}</span>
                  <span className="mx-2" style={{ color: 'var(--text-faint)' }}>→</span>
                  <span className={result.impact.new_surplus >= 0 ? "text-emerald-400" : "text-[#E4002B]"}>{fmt(result.impact.new_surplus)}</span>
                </div>
              </div>
            </div>

            {/* Savings Rate */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Savings Rate</span>
                <div className="font-mono text-[12px]">
                  <span style={{ color: 'var(--text-faint)' }}>{result.impact.current_savings_rate}%</span>
                  <span className="mx-2" style={{ color: 'var(--text-faint)' }}>→</span>
                  <span className={result.impact.new_savings_rate >= 20 ? "text-emerald-400" : result.impact.new_savings_rate >= 10 ? "text-amber-400" : "text-[#E4002B]"}>
                    {result.impact.new_savings_rate}%
                  </span>
                </div>
              </div>
            </div>

            {/* Emergency Fund */}
            <div>
              <div className="flex items-center justify-between mb-1">
                <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>Emergency Fund After Purchase</span>
                <span className={`font-mono text-[12px] ${result.impact.emergency_fund_ok ? "text-emerald-400" : "text-[#E4002B]"}`}>
                  {result.impact.emergency_fund_months_after} months
                </span>
              </div>
              <p className="font-mono text-[8px]" style={{ color: 'var(--text-faint)' }}>
                {result.impact.emergency_fund_ok ? "✓ Adequate coverage" : "✗ Below 6-month target — risky"}
              </p>
            </div>

            {/* SIP Impact */}
            {result.impact.sip_cut_needed > 0 && (
              <div className="p-3" style={{ border: '1px solid rgba(228,0,43,0.15)', background: 'rgba(228,0,43,0.03)' }}>
                <p className="font-mono text-[9px] text-[#E4002B] mb-1">SIP Warning</p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  You'd need to cut {fmt(result.impact.sip_cut_needed)}/month from investments
                </p>
              </div>
            )}

            {/* FIRE Delay */}
            {result.impact.fire_delay_months > 0 && (
              <div className="p-3" style={{ border: '1px solid rgba(251,191,36,0.15)', background: 'rgba(251,191,36,0.03)' }}>
                <p className="font-mono text-[9px] text-amber-400 mb-1">Retirement Impact</p>
                <p className="text-xs" style={{ color: 'var(--text-secondary)' }}>
                  This purchase could delay your FIRE goal by ~{result.impact.fire_delay_months} months
                </p>
              </div>
            )}
          </div>

          {/* Tips */}
          <div className="p-6 space-y-3" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Actionable Tips</p>
            {result.tips.map((tip, i) => (
              <div key={i} className="flex gap-3 p-3" style={{ border: '1px solid var(--border)' }}>
                <span className="text-[#E4002B] font-bold text-sm font-mono">{i + 1}.</span>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{tip}</p>
              </div>
            ))}
          </div>

          {/* Affordable alternative */}
          {result.max_affordable_price < result.item.cost && result.max_affordable_price > 0 && (
            <div className="p-6 flex items-center justify-between" style={{ border: '1px solid rgba(52,211,153,0.2)', background: 'rgba(52,211,153,0.03)' }}>
              <div>
                <p className="font-mono text-[9px] text-emerald-400 tracking-wider mb-1">Comfortable Budget</p>
                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>
                  A {form.item_name} up to this price keeps your DTI healthy
                </p>
              </div>
              <p className="text-massive text-2xl text-emerald-400">{fmt(result.max_affordable_price)}</p>
            </div>
          )}

          <button onClick={() => setResult(null)} className="btn-bracket text-[9px]">← Adjust and Recheck</button>
        </motion.div>
      )}
    </div>
  );
}
