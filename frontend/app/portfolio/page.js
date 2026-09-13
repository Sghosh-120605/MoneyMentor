"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { uploadCams, analyzePortfolio } from "../../lib/api";

const fmt = (n) => Math.round(n || 0).toLocaleString("en-IN");

export default function PortfolioPage() {
  const [step, setStep] = useState("upload");
  const [xray, setXray] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);

  const handleFile = async (file) => {
    if (!file || !file.name.endsWith(".pdf")) { setError("Upload a PDF."); return; }
    setLoading(true); setError(null); setStep("analyzing");
    try {
      const res = await uploadCams(file);
      if (!res.success) throw new Error(res.message);
      const xrayData = await analyzePortfolio(res.portfolio);
      setXray(xrayData); setStep("result");
    } catch (e) { setError(e.message); setStep("upload"); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-8">
      <div>
        <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Portfolio Analysis</span>
        <h1 className="text-massive text-4xl md:text-6xl">PORTFOLIO<br/>X-RAY</h1>
        <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>XIRR · Fund overlap · Expense ratio drag · Rebalancing</p>
      </div>

      <AnimatePresence mode="wait">
        {step === "upload" && (
          <motion.div key="upload" initial={{ opacity:0,y:20 }} animate={{ opacity:1,y:0 }} exit={{ opacity:0,y:-20 }}>
            <div onDragOver={(e) => { e.preventDefault(); setDragOver(true); }} onDragLeave={() => setDragOver(false)}
              onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]); }}
              className="p-16 text-center relative transition-all" style={{
                border: dragOver ? '2px dashed #E4002B' : '2px dashed var(--border-hover)',
                background: dragOver ? 'rgba(228,0,43,0.03)' : 'transparent',
              }}>
              <p className="text-massive text-2xl mb-4" style={{ color: 'var(--text-faint)' }}>CAMS / KFintech</p>
              <p className="font-mono text-[10px] mb-6" style={{ color: 'var(--text-muted)' }}>Drag statement PDF or click to browse</p>
              <label className="btn-primary cursor-pointer inline-block">
                Browse File
                <input type="file" accept=".pdf" className="hidden" onChange={(e) => handleFile(e.target.files[0])} />
              </label>
              {error && <p className="font-mono text-[10px] text-[#E4002B] mt-4">⚠ {error}</p>}
            </div>
          </motion.div>
        )}

        {step === "analyzing" && (
          <motion.div key="analyzing" initial={{ opacity:0 }} animate={{ opacity:1 }} className="p-16 text-center" style={{ border: '1px solid var(--border)' }}>
            <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
              className="w-12 h-12 border-2 border-t-[#E4002B] rounded-full mx-auto mb-6" style={{ borderColor: 'var(--border)', borderTopColor: '#E4002B' }} />
            <p className="font-mono text-[10px]" style={{ color: 'var(--text-muted)' }}>Extracting holdings...</p>
          </motion.div>
        )}

        {step === "result" && xray && (
          <motion.div key="result" initial={{ opacity:0,y:30 }} animate={{ opacity:1,y:0 }} className="space-y-6">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
              {[
                ["Total Value", `₹${fmt(xray.portfolio?.total_current_value)}`, "text-emerald-400"],
                ["Portfolio XIRR", xray.portfolio_xirr != null ? `${xray.portfolio_xirr}%` : "—", ""],
                ["vs Nifty 50", xray.alpha != null ? `${xray.alpha > 0 ? "+" : ""}${xray.alpha}%` : "—", xray.alpha >= 0 ? "text-emerald-400" : "text-[#E4002B]"],
                ["Annual Fee Drag", `₹${fmt(xray.expense_drag?.total_annual_drag)}`, "text-amber-400"],
              ].map((m, i) => (
                <div key={i} className="p-6" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
                  <p className="font-mono text-[9px] tracking-wider uppercase mb-2" style={{ color: 'var(--text-faint)' }}>{m[0]}</p>
                  <p className={`text-massive text-2xl ${m[2]}`} style={!m[2] ? { color: 'var(--text-primary)' } : {}}>{m[1]}</p>
                </div>
              ))}
            </div>

            <div className="p-6" style={{ border: '1px solid var(--border)' }}>
              <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-4">Holdings: {xray.portfolio?.holdings?.length} Funds</p>
              <div className="overflow-x-auto">
                <table className="w-full text-[11px]">
                  <thead>
                    <tr style={{ borderBottom: '1px solid var(--border)' }}>
                      <th className="text-left py-3 font-mono text-[9px] font-normal" style={{ color: 'var(--text-muted)' }}>Fund</th>
                      <th className="text-right py-3 font-mono text-[9px] font-normal" style={{ color: 'var(--text-muted)' }}>Value</th>
                      <th className="text-right py-3 font-mono text-[9px] font-normal" style={{ color: 'var(--text-muted)' }}>XIRR</th>
                      <th className="text-right py-3 font-mono text-[9px] font-normal" style={{ color: 'var(--text-muted)' }}>Plan</th>
                    </tr>
                  </thead>
                  <tbody className="font-mono">
                    {xray.portfolio?.holdings?.map((h, i) => (
                      <tr key={i} className="hover:opacity-80 transition-opacity" style={{ borderBottom: '1px solid var(--border)' }}>
                        <td className="py-2">
                          <p className="text-xs">{h.name}</p>
                          <p className="text-[9px] capitalize" style={{ color: 'var(--text-faint)' }}>{h.category?.replace(/_/g, " ")}</p>
                        </td>
                        <td className="py-2 text-right" style={{ color: 'var(--text-secondary)' }}>₹{fmt(h.current_value)}</td>
                        <td className="py-2 text-right">
                          {h.xirr != null ? <span className={h.xirr >= 12 ? "text-emerald-400" : h.xirr >= 8 ? "text-amber-400" : "text-[#E4002B]"}>{h.xirr}%</span> : <span style={{ color: 'var(--text-faint)' }}>—</span>}
                        </td>
                        <td className="py-2 text-right">
                          <span className={`font-mono text-[9px] px-2 py-0.5 border ${h.plan_type === "direct" ? "text-emerald-400 border-emerald-500/20" : "text-amber-400 border-amber-500/20"}`}>
                            {h.plan_type}
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {xray.overlap_alerts?.length > 0 && (
              <div className="p-6 space-y-2" style={{ border: '1px solid var(--border)' }}>
                <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-2">Overlap Alerts</p>
                {xray.overlap_alerts.map((a, i) => (
                  <div key={i} className={`p-3 border text-sm ${a.severity === "high" ? "border-[#E4002B]/20 text-[#E4002B]" : "border-amber-500/20 text-amber-400"}`}>
                    <span className="font-bold font-mono">{a.overlap_pct}%</span> — {a.message}
                  </div>
                ))}
              </div>
            )}

            {xray.expense_drag?.total_annual_drag > 0 && (
              <div className="p-6" style={{ border: '1px solid var(--border)' }}>
                <p className="font-mono text-[10px] text-amber-400 tracking-wider mb-2">Expense Drag</p>
                <p className="text-sm mb-4" style={{ color: 'var(--text-secondary)' }}>{xray.expense_drag.tip}</p>
                {xray.expense_drag.details?.slice(0, 5).map((d, i) => (
                  <div key={i} className="flex items-center justify-between text-[11px] py-2" style={{ borderBottom: '1px solid var(--border)' }}>
                    <span style={{ color: 'var(--text-secondary)' }}>{d.fund}</span>
                    <div className="text-right font-mono">
                      <span className="text-amber-400">₹{fmt(d.annual_saving)}/yr</span>
                      <span className="text-[9px] ml-2" style={{ color: 'var(--text-faint)' }}>{d.current_er}% → {d.direct_er}%</span>
                    </div>
                  </div>
                ))}
              </div>
            )}

            {xray.rebalancing_plan?.length > 0 && (
              <div className="p-6 space-y-2" style={{ border: '1px solid var(--border)' }}>
                <p className="font-mono text-[10px] tracking-wider mb-2" style={{ color: 'var(--text-muted)' }}>Rebalancing Plan</p>
                {xray.rebalancing_plan.map((r, i) => (
                  <div key={i} className={`p-3 border flex items-center justify-between ${r.action === "buy" ? "border-emerald-500/20" : "border-[#E4002B]/20"}`}>
                    <div>
                      <span className={`font-bold text-sm uppercase ${r.action === "buy" ? "text-emerald-400" : "text-[#E4002B]"}`}>{r.action}</span>
                      <span className="text-sm capitalize ml-2" style={{ color: 'var(--text-secondary)' }}>{r.category}</span>
                      <p className="text-xs mt-0.5" style={{ color: 'var(--text-faint)' }}>{r.message}</p>
                    </div>
                    <span className={`font-mono font-bold ${r.action === "buy" ? "text-emerald-400" : "text-[#E4002B]"}`}>₹{fmt(r.amount)}</span>
                  </div>
                ))}
              </div>
            )}
            <button onClick={() => { setStep("upload"); setXray(null); }} className="btn-bracket text-[9px]">← Analyse Another</button>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
