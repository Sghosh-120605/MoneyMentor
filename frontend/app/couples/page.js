"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

const API_BASE = process.env.NEXT_PUBLIC_API_URL !== undefined 
    ? process.env.NEXT_PUBLIC_API_URL 
    : (typeof window !== 'undefined' ? "" : "http://localhost:8000");
const fmt = (n) => Math.round(n || 0).toLocaleString("en-IN");

const defaultPartner = (name) => ({
  name, annual_income: 0, section_80c: 0, section_80ccd_1b: 0,
  section_80d_self: 0, section_80d_parents: 0, hra_received: 0,
  rent_paid: 0, is_metro: true, basic_salary: 0, age: 30,
});

const Field = ({ label, value, onChange }) => (
  <label className="flex items-center justify-between py-2 group" style={{ borderBottom: '1px solid var(--border)' }}>
    <span className="font-mono text-[10px] tracking-wider uppercase transition-colors" style={{ color: 'var(--text-muted)' }}>{label}</span>
    <input type="number" value={value || ""} onChange={(e) => onChange(Number(e.target.value) || 0)}
      className="input-terminal text-right w-28" placeholder="0" />
  </label>
);

export default function CouplesPage() {
  const [partnerA, setPartnerA] = useState(defaultPartner("Partner A"));
  const [partnerB, setPartnerB] = useState(defaultPartner("Partner B"));
  const [shared, setShared] = useState({
    home_loan_interest: 0, home_loan_principal: 0,
    education_loan_interest: 0, health_insurance_family: 0,
  });
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleAnalyse = async () => {
    setLoading(true); setError(null);
    try {
      const res = await fetch(`${API_BASE}/api/couples-plan`, {
        method: "POST", headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ partner_a: partnerA, partner_b: partnerB, ...shared }),
      });
      if (!res.ok) throw new Error("Analysis failed");
      setResult(await res.json());
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const loadDemo = () => {
    setPartnerA({ name: "Arjun", annual_income: 2400000, basic_salary: 960000, section_80c: 34800, section_80ccd_1b: 0, section_80d_self: 18000, section_80d_parents: 0, hra_received: 384000, rent_paid: 360000, is_metro: false, age: 29 });
    setPartnerB({ name: "Priya", annual_income: 1200000, basic_salary: 480000, section_80c: 96000, section_80ccd_1b: 50000, section_80d_self: 12000, section_80d_parents: 0, hra_received: 192000, rent_paid: 240000, is_metro: false, age: 28 });
    setShared({ home_loan_interest: 180000, home_loan_principal: 120000, education_loan_interest: 0, health_insurance_family: 25000 });
    setResult(null);
  };

  const PartnerPanel = ({ partner, setPartner, label }) => {
    const set = (k, v) => setPartner({ ...partner, [k]: v });
    return (
      <div className="p-6 space-y-1" style={{ border: '1px solid var(--border)' }}>
        <div className="flex items-center justify-between mb-4">
          <input type="text" value={partner.name} onChange={(e) => set("name", e.target.value)}
            className="bg-transparent text-massive text-2xl outline-none border-b border-transparent hover:border-[var(--border)] focus:border-[#E4002B] transition-colors w-full"
            style={{ color: 'var(--text-primary)' }} />
          <span className="font-mono text-[9px] ml-2" style={{ color: 'var(--text-faint)' }}>{label}</span>
        </div>
        <Field label="Annual Income" value={partner.annual_income} onChange={(v) => set("annual_income", v)} />
        <Field label="Basic Salary" value={partner.basic_salary} onChange={(v) => set("basic_salary", v)} />
        <Field label="80C / EPF / ELSS" value={partner.section_80c} onChange={(v) => set("section_80c", v)} />
        <Field label="80CCD NPS" value={partner.section_80ccd_1b} onChange={(v) => set("section_80ccd_1b", v)} />
        <Field label="80D Self" value={partner.section_80d_self} onChange={(v) => set("section_80d_self", v)} />
        <Field label="80D Parents" value={partner.section_80d_parents} onChange={(v) => set("section_80d_parents", v)} />
        <Field label="HRA Received" value={partner.hra_received} onChange={(v) => set("hra_received", v)} />
        <Field label="Rent Paid" value={partner.rent_paid} onChange={(v) => set("rent_paid", v)} />
        <label className="flex items-center justify-between py-2 cursor-pointer" style={{ borderBottom: '1px solid var(--border)' }}>
          <span className="font-mono text-[10px] tracking-wider uppercase" style={{ color: 'var(--text-muted)' }}>Metro City</span>
          <input type="checkbox" checked={partner.is_metro} onChange={(e) => set("is_metro", e.target.checked)} className="accent-[#E4002B] w-4 h-4" />
        </label>
      </div>
    );
  };

  return (
    <div className="space-y-8">
      <div className="flex items-start justify-between">
        <div>
          <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Couple Tax Optimiser</span>
          <h1 className="text-massive text-4xl md:text-6xl">COUPLE&apos;S<br/>PLANNER</h1>
          <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>Smart deduction assignment between partners</p>
        </div>
        <button onClick={loadDemo} className="btn-bracket text-[9px]">Load Demo</button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
        <PartnerPanel partner={partnerA} setPartner={setPartnerA} label="P.01" />
        <PartnerPanel partner={partnerB} setPartner={setPartnerB} label="P.02" />
      </div>

      <div className="p-6" style={{ border: '1px solid var(--border)' }}>
        <p className="font-mono text-[10px] tracking-wider uppercase mb-4" style={{ color: 'var(--text-muted)' }}>Shared Deductions — Auto-assigned to optimal partner</p>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <Field label="Home Loan Int" value={shared.home_loan_interest} onChange={(v) => setShared({...shared, home_loan_interest: v})} />
          <Field label="Home Loan Principal" value={shared.home_loan_principal} onChange={(v) => setShared({...shared, home_loan_principal: v})} />
          <Field label="Edu Loan Int" value={shared.education_loan_interest} onChange={(v) => setShared({...shared, education_loan_interest: v})} />
          <Field label="Family Health" value={shared.health_insurance_family} onChange={(v) => setShared({...shared, health_insurance_family: v})} />
        </div>
      </div>

      <button onClick={handleAnalyse} disabled={loading} className="btn-primary w-full text-center disabled:opacity-50">
        {loading ? "Computing..." : "Optimise Joint Tax →"}
      </button>
      {error && <p className="font-mono text-[10px] text-[#E4002B] text-center">⚠ {error}</p>}

      <AnimatePresence>
        {result && (
          <motion.div initial={{ opacity: 0, y: 30 }} animate={{ opacity: 1, y: 0 }} className="space-y-6">
            <div className="grid grid-cols-3 gap-4">
              {[
                ["Combined Tax", `₹${fmt(result.joint_summary.combined_tax)}`, "text-emerald-400"],
                ["Smart Savings", `₹${fmt(result.joint_summary.savings_from_optimisation)}`, "text-[#E4002B]"],
                ["Combined Income", `₹${fmt(result.joint_summary.combined_income)}`, ""],
              ].map(([label, value, color], i) => (
                <div key={i} className="p-6 text-center" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                  <p className="font-mono text-[9px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-faint)' }}>{label}</p>
                  <p className={`text-massive text-2xl ${color}`} style={!color ? { color: 'var(--text-primary)' } : {}}>{value}</p>
                </div>
              ))}
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
              {[result.partner_a, result.partner_b].map((p, idx) => (
                <div key={idx} className="p-6 space-y-3" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                  <div className="flex items-center justify-between">
                    <h3 className="text-massive text-xl">{p.name}</h3>
                    <span className={`font-mono text-[9px] px-2 py-0.5 border ${p.recommended_regime === "new" ? "text-emerald-400 border-emerald-500/20" : "text-amber-400 border-amber-500/20"}`}>
                      {p.recommended_regime.toUpperCase()} ✓
                    </span>
                  </div>
                  <div className="grid grid-cols-2 gap-y-1 text-[11px] font-mono">
                    <span style={{ color: 'var(--text-muted)' }}>Income</span><span className="text-right">₹{fmt(p.income)}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Bracket</span><span className="text-right">{p.bracket}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Old Tax</span><span className="text-right">₹{fmt(p.old_regime_tax)}</span>
                    <span style={{ color: 'var(--text-muted)' }}>New Tax</span><span className="text-right">₹{fmt(p.new_regime_tax)}</span>
                    <span style={{ color: 'var(--text-muted)' }}>Deductions</span><span className="text-right text-[#E4002B]">₹{fmt(p.total_deductions)}</span>
                    <span className="font-bold" style={{ color: 'var(--text-muted)' }}>Final Tax</span><span className="text-right text-emerald-400 font-bold">₹{fmt(p.tax_payable)}</span>
                  </div>
                </div>
              ))}
            </div>

            {result.deduction_assignments?.length > 0 && (
              <div className="p-6 space-y-3" style={{ border: '1px solid var(--border)' }}>
                <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-2">Smart Assignments</p>
                {result.deduction_assignments.map((d, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 transition-all" style={{ border: '1px solid var(--border)' }}>
                    <span className={`font-mono text-[9px] px-2 py-0.5 border mt-0.5 ${d.assigned_to === "A" ? "border-white/20" : "text-[#E4002B] border-[#E4002B]/20"}`}>
                      {d.assigned_to === "A" ? result.partner_a.name : result.partner_b.name}
                    </span>
                    <div className="flex-1">
                      <p className="text-sm">{d.deduction} — ₹{fmt(d.amount)}</p>
                      <p className="text-xs mt-0.5" style={{ color: 'var(--text-muted)' }}>{d.reason}</p>
                    </div>
                    {d.extra_saving_vs_wrong_partner > 0 && (
                      <span className="text-emerald-400 font-mono text-[10px]">+₹{fmt(d.extra_saving_vs_wrong_partner)}</span>
                    )}
                  </div>
                ))}
              </div>
            )}

            {result.tips?.length > 0 && (
              <div className="p-6 space-y-2" style={{ border: '1px solid var(--border)' }}>
                <p className="font-mono text-[10px] tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Optimisation Tips</p>
                {result.tips.map((tip, i) => (
                  <div key={i} className="flex gap-3 p-3" style={{ border: '1px solid var(--border)' }}>
                    <span className="text-[#E4002B] font-bold text-sm font-mono">{i+1}.</span>
                    <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{tip}</p>
                  </div>
                ))}
              </div>
            )}
            <button onClick={() => setResult(null)} className="btn-bracket text-[9px]">← Adjust and Rerun</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
