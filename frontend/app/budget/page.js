"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import { getBudgetPlan } from "../../lib/api";

const fmt = (n) => "₹" + Math.round(n || 0).toLocaleString("en-IN");

export default function BudgetPage() {
  const [form, setForm] = useState({
    monthly_income: "", rent: "", groceries: "", utilities: "",
    emis: "", insurance: "", sip_investments: "", transport: "",
    dining_out: "", shopping: "", subscriptions: "", education: "",
    medical: "", other_expenses: "", dependants: 0, age: 30,
    financial_goal: "Build an emergency fund",
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const set = (k, v) => setForm((f) => ({ ...f, [k]: v }));

  const handleSubmit = async (e) => {
    e.preventDefault(); setLoading(true); setError(null);
    try {
      const payload = {};
      Object.entries(form).forEach(([k, v]) => {
        if (k === "financial_goal") payload[k] = v;
        else payload[k] = parseFloat(v) || 0;
      });
      setResult(await getBudgetPlan(payload));
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = () => {
    setForm({
      monthly_income: 120000, rent: 35000, groceries: 15000, utilities: 4000,
      emis: 12000, insurance: 3000, sip_investments: 10000, transport: 8000,
      dining_out: 12000, shopping: 8000, subscriptions: 2500, education: 0,
      medical: 2000, other_expenses: 5000, dependants: 1, age: 29,
      financial_goal: "Save for European vacation next year",
    });
    setResult(null);
  };

  const Field = ({ label, field, placeholder = "0", suffix = "₹", type = "number" }) => (
    <label className="flex items-center justify-between py-2 group" style={{ borderBottom: '1px solid var(--border)' }}>
      <span className="font-mono text-[10px] tracking-wider uppercase transition-colors" style={{ color: 'var(--text-muted)' }}>{label}</span>
      <div className="flex items-center gap-1">
        <input type={type} placeholder={placeholder} value={form[field] || ""} onChange={(e) => set(field, e.target.value)}
          className={`input-terminal text-right ${type === 'text' ? 'w-48' : 'w-24'}`} />
        {suffix && <span className="font-mono text-[8px]" style={{ color: 'var(--text-faint)' }}>{suffix}</span>}
      </div>
    </label>
  );

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">AI Budget Planner</span>
          <h1 className="text-massive text-4xl md:text-6xl">FIX MY<br/>BUDGET</h1>
          <p className="text-editorial text-lg mt-2 " style={{ color: 'var(--text-muted)' }}>
            Find where your money goes and get an optimised 50/30/20 plan in seconds.
          </p>
        </div>
        <button onClick={loadDemo} className="btn-bracket text-[9px]">Load Demo</button>
      </div>

      {!result ? (
        <form onSubmit={handleSubmit} className="space-y-6">
          <div className="p-6" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-4">Core Info</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
              <Field label="Monthly In-Hand Income" field="monthly_income" placeholder="100000" />
              <Field label="Financial Goal" field="financial_goal" placeholder="e.g. Save for a house" type="text" suffix="" />
              <Field label="Age" field="age" placeholder="30" suffix="" />
              <Field label="Dependants" field="dependants" placeholder="0" suffix="" />
            </div>
          </div>

          <div className="p-6" style={{ border: '1px solid var(--border)' }}>
            <p className="font-mono text-[10px] tracking-wider uppercase mb-4" style={{ color: 'var(--text-muted)' }}>Fixed Needs</p>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-x-8">
              <Field label="Rent / Maintenance" field="rent" placeholder="20000" />
              <Field label="Groceries & Household" field="groceries" placeholder="10000" />
              <Field label="Utilities (Electricity, WiFi)" field="utilities" placeholder="3000" />
              <Field label="Loan EMIs" field="emis" placeholder="5000" />
              <Field label="Insurance Premiums" field="insurance" placeholder="2000" />
              <Field label="Medical / Pharmacy" field="medical" placeholder="1000" />
              <Field label="Transport (Fuel, Metro)" field="transport" placeholder="4000" />
              <Field label="Education / Tuition" field="education" placeholder="0" />
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-6 flex flex-col" style={{ border: '1px solid var(--border)' }}>
              <p className="font-mono text-[10px] tracking-wider uppercase mb-4" style={{ color: 'var(--text-muted)' }}>Discretionary (Wants)</p>
              <div className="space-y-1 flex-1">
                <Field label="Dining Out / Zomato" field="dining_out" placeholder="5000" />
                <Field label="Shopping / Gadgets" field="shopping" placeholder="4000" />
                <Field label="Subscriptions (Netflix, Gym)" field="subscriptions" placeholder="1500" />
                <Field label="Other Expenses" field="other_expenses" placeholder="2000" />
              </div>
            </div>
            
            <div className="p-6 flex flex-col" style={{ border: '1px solid var(--border)' }}>
               <p className="font-mono text-[10px] tracking-wider uppercase mb-4" style={{ color: 'var(--text-muted)' }}>Current Savings</p>
               <div className="space-y-1">
                 <Field label="Monthly SIPs / RD" field="sip_investments" placeholder="10000" />
               </div>
            </div>
          </div>

          {error && <p className="font-mono text-[10px] text-[#E4002B]">⚠ {error}</p>}
          <button type="submit" disabled={loading} className="btn-primary w-full text-center disabled:opacity-50">
            {loading ? "Optimising Budget..." : "Fix My Budget →"}
          </button>
        </form>
      ) : (
        <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
          
          <div className="flex flex-col md:flex-row gap-6">
             <div className="flex-1 p-8 border-2 border-current/20 relative">
               <div className="absolute top-4 right-4 text-massive text-6xl opacity-20">{result.ai_plan.health_grade}</div>
               <p className="font-mono text-[9px] tracking-wider mb-2" style={{ color: 'var(--text-faint)' }}>AI BUDGET SUMMARY</p>
               <p className="text-sm mt-3 leading-relaxed" style={{ color: 'var(--text-primary)' }}>{result.ai_plan.summary}</p>
             </div>
             <div className="flex-1 p-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
               <p className="font-mono text-[9px] tracking-wider mb-1 uppercase" style={{ color: 'var(--text-faint)' }}>Total Expenses</p>
               <p className="text-massive text-3xl text-[#E4002B]">{fmt(result.current.total_expenses)}</p>
               <p className="font-mono text-[9px] tracking-wider mt-4 mb-1 uppercase" style={{ color: 'var(--text-faint)' }}>Current Surplus (Unallocated)</p>
               <p className="text-massive text-xl text-emerald-400">{fmt(result.current.monthly_surplus)}</p>
             </div>
          </div>

          <div className="p-6 space-y-8" style={{ border: '1px solid var(--border)' }}>
             <p className="font-mono text-[10px] text-[#E4002B] tracking-wider">The 50/30/20 Shift</p>

             <div className="space-y-6">
               {[
                 { label: "Needs", target: 50, current: result.current.current_split.needs_pct, currVal: result.current.current_split.needs, color: '#3b82f6' },
                 { label: "Wants", target: 30, current: result.current.current_split.wants_pct, currVal: result.current.current_split.wants, color: '#f59e0b' },
                 { label: "Savings", target: 20, current: result.current.current_split.savings_pct, currVal: result.current.current_split.savings, color: '#10b981' },
               ].map(cat => (
                 <div key={cat.label}>
                    <div className="flex items-end justify-between mb-2">
                       <div>
                         <span className="font-mono text-xs uppercase" style={{ color: 'var(--text-secondary)' }}>{cat.label}</span>
                         <span className="font-mono text-[9px] ml-2" style={{ color: 'var(--text-faint)' }}>(Target: {cat.target}%)</span>
                       </div>
                       <div className="text-right">
                          <span className="text-sm">{fmt(cat.currVal)}</span>
                          <span className="font-mono text-[10px] ml-2" style={{ color: cat.current > cat.target + 5 ? '#E4002B' : 'var(--text-muted)' }}>
                            {cat.current}%
                          </span>
                       </div>
                    </div>
                    {/* Bar chart */}
                    <div className="h-[6px] w-full bg-black/20 relative">
                       <div className="absolute h-full transition-all duration-1000" style={{ width: `${Math.min(100, cat.current)}%`, background: cat.color }} />
                       <div className="absolute h-full w-[2px] bg-white z-10" style={{ left: `${cat.target}%` }} title={`Target: ${cat.target}%`} />
                    </div>
                 </div>
               ))}
             </div>
          </div>

          {result.ai_plan.quick_wins && result.ai_plan.quick_wins.length > 0 && (
            <div className="p-6 border border-amber-500/20 bg-amber-500/5">
              <p className="font-mono text-[10px] text-amber-500 tracking-wider mb-4">Quick Wins</p>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                {result.ai_plan.quick_wins.map((win, i) => (
                  <div key={i} className="p-4" style={{ border: '1px solid var(--border)' }}>
                    <div className="flex justify-between items-start mb-2">
                      <p className="font-mono text-[10px] uppercase" style={{ color: 'var(--text-muted)' }}>{win.difficulty}</p>
                      <p className="font-mono text-[10px] text-emerald-400">Save {fmt(win.monthly_saving)}/mo</p>
                    </div>
                    <p className="text-sm" style={{ color: 'var(--text-primary)' }}>{win.action}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          <div className="p-6" style={{ border: '1px solid var(--border)' }}>
             <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-4">Optimised AI Budget Allocation</p>
             <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
               {Object.entries(result.ai_plan.optimised_budget || {}).map(([category, amount]) => (
                  <div key={category} className="p-3 bg-black/10 flex justify-between items-center" style={{ borderBottom: '1px solid var(--border)' }}>
                     <span className="text-xs" style={{ color: 'var(--text-secondary)' }}>{category}</span>
                     <span className="font-mono text-sm">{fmt(amount)}</span>
                  </div>
               ))}
             </div>
          </div>

          <button onClick={() => setResult(null)} className="btn-bracket text-[9px]">← Adjust Inputs</button>
        </motion.div>
      )}
    </div>
  );
}
