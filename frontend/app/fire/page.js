"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { getFirePlan } from "../../lib/api";

const fmt = (n) => Math.round(n || 0).toLocaleString("en-IN");
const fmtCr = (n) => { const v = Math.round(n || 0); if (v >= 10_000_000) return `₹${(v / 10_000_000).toFixed(2)} Cr`; if (v >= 100_000) return `₹${(v / 100_000).toFixed(1)} L`; return `₹${v.toLocaleString("en-IN")}`; };

export default function FirePage() {
  const [form, setForm] = useState({ age: 30, annual_income: "", annual_expenses: "", current_savings: "", monthly_sip: "", risk_appetite: "moderate", fire_age: 45 });
  const [plan, setPlan] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));
  const num = (v) => parseFloat(v) || 0;

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null);
    try {
      const data = await getFirePlan({ age: num(form.age), annual_income: num(form.annual_income), annual_expenses: num(form.annual_expenses) || num(form.annual_income) * 0.7, current_savings: num(form.current_savings), monthly_sip: num(form.monthly_sip), risk_appetite: form.risk_appetite, fire_age: num(form.fire_age) });
      setPlan(data);
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const MilestoneChart = ({ milestones }) => {
    if (!milestones || milestones.length < 2) return null;
    const maxVal = Math.max(...milestones.map(m => Math.max(m.projected_corpus, m.target_line)));
    const W = 560, H = 200, P = { l: 40, r: 20, t: 10, b: 30 };
    const cx = (i) => P.l + (i / (milestones.length - 1)) * (W - P.l - P.r);
    const cy = (v) => P.t + (1 - v / maxVal) * (H - P.t - P.b);
    const projPath = milestones.map((m, i) => `${i === 0 ? "M" : "L"}${cx(i)},${cy(m.projected_corpus)}`).join(" ");
    const targetPath = milestones.map((m, i) => `${i === 0 ? "M" : "L"}${cx(i)},${cy(m.target_line)}`).join(" ");
    return (
      <div className="overflow-x-auto">
        <svg viewBox={`0 0 ${W} ${H}`} className="w-full h-48">
          <defs><linearGradient id="projG" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#E4002B" stopOpacity="0.2" /><stop offset="100%" stopColor="#E4002B" stopOpacity="0" /></linearGradient></defs>
          {[0, 0.25, 0.5, 0.75, 1].map(f => <line key={f} x1={P.l} x2={W-P.r} y1={P.t + f*(H-P.t-P.b)} y2={P.t + f*(H-P.t-P.b)} stroke="var(--border)" />)}
          <path d={targetPath} fill="none" stroke="#f59e0b" strokeWidth="1" strokeDasharray="4,3" />
          <path d={`${projPath} L${cx(milestones.length-1)},${H-P.b} L${cx(0)},${H-P.b} Z`} fill="url(#projG)" />
          <path d={projPath} fill="none" stroke="#E4002B" strokeWidth="2" />
          {milestones.filter((_, i) => i % 5 === 0).map(m => <text key={m.year} x={cx(milestones.indexOf(m))} y={H-6} textAnchor="middle" fill="var(--text-faint)" fontSize="9" fontFamily="monospace">{m.year}</text>)}
        </svg>
        <div className="flex gap-6 justify-center font-mono text-[9px] mt-2">
          <span className="text-[#E4002B]">— Your Projection</span>
          <span className="text-amber-400">- - Target</span>
        </div>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      <div>
        <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Financial Independence</span>
        <h1 className="text-massive text-4xl md:text-6xl">F.I.R.E<br/>PLANNER</h1>
        <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>Retire Early — plan your path to freedom</p>
      </div>

      {!plan ? (
        <form onSubmit={handleSubmit} className="p-6 space-y-4" style={{ border: '1px solid var(--border)' }}>
          <p className="font-mono text-[10px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-muted)' }}>Input Parameters</p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-x-8">
            {[["Age", "age", "30"], ["FIRE Age", "fire_age", "45"], ["Annual Income", "annual_income", "1500000"], ["Annual Expenses", "annual_expenses", "900000"], ["Current Savings", "current_savings", "500000"], ["Monthly SIP", "monthly_sip", "25000"]].map(([label, field, ph]) => (
              <label key={field} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                <span className="font-mono text-[10px] tracking-wider uppercase" style={{ color: 'var(--text-muted)' }}>{label}</span>
                <input type="number" placeholder={ph} value={form[field] || ""} onChange={(e) => set(field, e.target.value)} className="input-terminal text-right w-28" />
              </label>
            ))}
          </div>
          <div>
            <p className="font-mono text-[10px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-muted)' }}>Risk Appetite</p>
            <div className="flex gap-2">
              {["conservative", "moderate", "aggressive"].map(r => (
                <button key={r} type="button" onClick={() => set("risk_appetite", r)}
                  className="flex-1 py-3 font-mono text-[10px] uppercase transition-all border"
                  style={{
                    borderColor: form.risk_appetite === r ? '#E4002B' : 'var(--border)',
                    color: form.risk_appetite === r ? '#E4002B' : 'var(--text-muted)',
                    background: form.risk_appetite === r ? 'rgba(228,0,43,0.05)' : 'transparent',
                  }}>{r}</button>
              ))}
            </div>
          </div>
          {error && <p className="font-mono text-[10px] text-[#E4002B]">⚠ {error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full text-center disabled:opacity-50">{loading ? "Planning..." : "Generate FIRE Plan →"}</button>
        </form>
      ) : (
        <motion.div initial={{ opacity:0,y:30 }} animate={{ opacity:1,y:0 }} className="space-y-6">
          <div className="p-6" style={{ border: `1px solid ${plan.on_track ? 'rgba(52,211,153,0.3)' : 'rgba(251,191,36,0.3)'}` }}>
            <p className={`text-massive text-3xl ${plan.on_track ? "text-emerald-400" : "text-amber-400"}`}>{plan.on_track ? "ON TRACK" : "NEEDS BOOST"}</p>
            <p className="text-editorial text-lg mt-1" style={{ color: 'var(--text-muted)' }}>Retire at {plan.fire_age} in {plan.years_to_fire} years</p>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
            {[
              ["Target Corpus", fmtCr(plan.target_corpus)], ["Projected Corpus", fmtCr(plan.projected_corpus)],
              ["Shortfall", plan.shortfall > 0 ? fmtCr(plan.shortfall) : "None"], ["Current SIP", `₹${fmt(plan.monthly_sip_current)}/mo`],
              ["Required SIP", plan.monthly_sip_required > 0 ? `₹${fmt(plan.monthly_sip_required)}/mo` : "Sufficient"], ["Savings Rate", `${plan.savings_rate_pct}%`],
            ].map(([label, value], i) => (
              <div key={i} className="p-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                <p className="font-mono text-[9px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-faint)' }}>{label}</p>
                <p className="text-massive text-xl">{value}</p>
              </div>
            ))}
          </div>

          <div className="p-6" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-4">Corpus Projection</p>
            <MilestoneChart milestones={plan.milestones} />
          </div>

          {plan.asset_allocation && (
            <div className="p-6 space-y-3" style={{ border: '1px solid var(--border)' }}>
              <p className="font-mono text-[10px] tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Asset Allocation</p>
              {Object.entries(plan.asset_allocation).map(([asset, pct]) => (
                <div key={asset}>
                  <div className="flex justify-between text-sm mb-1">
                    <span className="capitalize" style={{ color: 'var(--text-secondary)' }}>{asset}</span>
                    <span className="font-mono">{pct}%</span>
                  </div>
                  <div className="h-1 overflow-hidden" style={{ background: 'var(--border)' }}>
                    <div className={`h-full ${asset === "equity" ? "bg-[#E4002B]" : asset === "debt" ? "bg-gray-400" : "bg-amber-500"}`} style={{ width: `${pct}%` }} />
                  </div>
                </div>
              ))}
              <p className="font-mono text-[9px] mt-2" style={{ color: 'var(--text-faint)' }}>Blended return: {plan.blended_return_pct}% p.a.</p>
            </div>
          )}
          <button onClick={() => setPlan(null)} className="btn-bracket text-[9px]">← Adjust Plan</button>
        </motion.div>
      )}
    </div>
  );
}
