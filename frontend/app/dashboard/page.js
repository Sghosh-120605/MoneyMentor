"use client";
import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { motion } from "framer-motion";
import Header from "../../components/Header";
import TaxComparison from "../../components/TaxComparison";
import MissedDeductions from "../../components/MissedDeductions";
import ActionPlan from "../../components/ActionPlan";

const fmt = (n) => "₹" + Math.round(n || 0).toLocaleString("en-IN");

export default function Dashboard() {
  const [data, setData] = useState(null);
  const router = useRouter();

  useEffect(() => {
    const raw = sessionStorage.getItem("analysisResult");
    if (!raw) { router.push("/tax"); return; }
    try { setData(JSON.parse(raw)); } catch { router.push("/tax"); }
  }, [router]);

  if (!data) {
    return (
      <div className="min-h-screen flex items-center justify-center themed-bg">
        <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
          className="w-12 h-12 border-2 border-t-[#E4002B] rounded-full" style={{ borderColor: 'var(--border)', borderTopColor: '#E4002B' }} />
      </div>
    );
  }

  const { comparison, missed_deductions, action_plan, total_potential_savings, summary, tax_profile } = data;
  const overpaying = comparison.recommended_regime === "new"
    ? comparison.old_regime_tax - comparison.new_regime_tax
    : comparison.new_regime_tax - comparison.old_regime_tax;

  return (
    <div className="min-h-screen flex flex-col themed-bg">
      <Header />
      <main className="flex-1 px-6 md:px-12 py-10 max-w-7xl mx-auto w-full space-y-8">
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Tax Analysis Report</span>
          <h1 className="text-massive text-5xl md:text-7xl">YOUR TAX</h1>
          <p className="text-editorial text-xl md:text-3xl mt-1" style={{ color: 'var(--text-muted)' }}>
            Gross: {fmt(tax_profile.salary.gross_salary)} · FY 2025-26
          </p>
        </motion.div>

        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 0.3 }}
          className="grid grid-cols-2 lg:grid-cols-4 gap-4">
          {[
            { label: "Overpaying", value: fmt(overpaying), accent: "text-[#E4002B]" },
            { label: "Potential Savings", value: fmt(total_potential_savings + comparison.savings_amount), accent: "text-emerald-400" },
            { label: "TDS Paid", value: fmt(tax_profile.tds_deducted), accent: "" },
            { label: "Recommended", value: comparison.recommended_regime.toUpperCase(), accent: "text-[#E4002B]" },
          ].map((s, i) => (
            <div key={i} className="p-6 md:p-8" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
              <p className="font-mono text-[9px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-faint)' }}>{s.label}</p>
              <p className={`text-massive text-2xl md:text-3xl ${s.accent}`} style={!s.accent ? { color: 'var(--text-primary)' } : {}}>{s.value}</p>
            </div>
          ))}
        </motion.div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          <TaxComparison comparison={comparison} />
          <MissedDeductions deductions={missed_deductions} />
        </div>

        <ActionPlan actions={action_plan} summary={summary} />

        <div className="flex flex-col sm:flex-row gap-3 pt-4">
          <button onClick={() => { sessionStorage.removeItem("analysisResult"); router.push("/tax"); }} className="btn-bracket">
            ← Analyse Another
          </button>
          <button onClick={() => window.print()} className="btn-primary">Export PDF</button>
        </div>
      </main>

      <footer style={{ borderTop: '1px solid var(--border)' }} className="py-6 px-6 text-center">
        <span className="font-mono text-[9px]" style={{ color: 'var(--text-faint)' }}>
          <span className="text-[#E4002B] font-bold">ET</span> × MoneyMentor AI · CFO for Every Indian
        </span>
      </footer>
    </div>
  );
}
