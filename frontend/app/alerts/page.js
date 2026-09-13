"use client";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { getAlerts } from "../../lib/api";

const fmt = (n) => Math.round(n || 0).toLocaleString("en-IN");
const SEV = {
  high:   { label: "Urgent",    color: "text-[#E4002B]", border: "border-[#E4002B]/30" },
  medium: { label: "Important", color: "text-amber-400",  border: "border-amber-500/30" },
  low:    { label: "FYI",       color: "text-gray-400",   border: "border-gray-500/30" },
};

export default function AlertsPage() {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(false);
  const [params, setParams] = useState({ annual_income: "", has_home_loan: false, has_nps: false, monthly_emi: "", portfolio_value: "" });
  const [fetched, setFetched] = useState(false);
  const [expanded, setExpanded] = useState(null);

  const fetchAlerts = async () => {
    setLoading(true);
    try {
      const q = { annual_income: parseFloat(params.annual_income) || 0, has_home_loan: params.has_home_loan, has_nps: params.has_nps, monthly_emi: parseFloat(params.monthly_emi) || 0, portfolio_value: parseFloat(params.portfolio_value) || 0 };
      setAlerts(await getAlerts(q)); setFetched(true);
    } catch (e) { console.error(e); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-8">
      <div>
        <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Proactive Alerts</span>
        <h1 className="text-massive text-4xl md:text-6xl">ALERTS</h1>
        <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>Budget · RBI · SEBI — personalised for your profile</p>
      </div>

      <div className="p-6 space-y-4" style={{ border: '1px solid var(--border)' }}>
        <p className="font-mono text-[10px] tracking-wider uppercase" style={{ color: 'var(--text-muted)' }}>Personalisation (optional)</p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-x-8">
          {[["Annual Income", "annual_income"], ["Monthly EMI", "monthly_emi"], ["Portfolio Value", "portfolio_value"]].map(([label, field]) => (
            <label key={field} className="flex items-center justify-between py-2" style={{ borderBottom: '1px solid var(--border)' }}>
              <span className="font-mono text-[10px] tracking-wider uppercase" style={{ color: 'var(--text-muted)' }}>{label}</span>
              <input type="number" value={params[field]} onChange={(e) => setParams(p => ({...p, [field]: e.target.value}))} placeholder="0" className="input-terminal text-right w-28" />
            </label>
          ))}
        </div>
        <div className="flex gap-6">
          {[["has_home_loan", "Home Loan"], ["has_nps", "NPS Investor"]].map(([field, label]) => (
            <label key={field} className="flex items-center gap-2 font-mono text-[10px] tracking-wider uppercase cursor-pointer" style={{ color: 'var(--text-muted)' }}>
              <input type="checkbox" checked={params[field]} onChange={(e) => setParams(p => ({...p, [field]: e.target.checked}))} className="accent-[#E4002B] w-4 h-4" />
              {label}
            </label>
          ))}
        </div>
        <button onClick={fetchAlerts} disabled={loading} className="btn-primary disabled:opacity-50">
          {loading ? "Loading..." : fetched ? "Refresh Alerts" : "Get My Alerts"}
        </button>
      </div>

      {fetched && (
        <div className="space-y-3">
          {alerts.length === 0 ? (
            <div className="p-12 text-center" style={{ border: '1px solid var(--border)' }}>
              <p className="text-massive text-3xl text-emerald-400 mb-2">CLEAR</p>
              <p className="font-mono text-[10px]" style={{ color: 'var(--text-faint)' }}>No urgent alerts</p>
            </div>
          ) : (
            <>
              <p className="font-mono text-[10px]" style={{ color: 'var(--text-faint)' }}>{alerts.length} alerts found</p>
              {alerts.map(a => {
                const s = SEV[a.severity] || SEV.low;
                const open = expanded === a.id;
                return (
                  <div key={a.id} className={`border ${s.border} transition-all cursor-pointer`} onClick={() => setExpanded(open ? null : a.id)}>
                    <div className="p-4 flex items-start gap-3">
                      <div className="flex-1">
                        <div className="flex items-start justify-between gap-2">
                          <p className="text-sm font-medium">{a.title}</p>
                          <span className={`font-mono text-[9px] ${s.color} shrink-0`}>{s.label}</span>
                        </div>
                        <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{a.impact_summary}</p>
                        {a.potential_saving_or_impact > 0 && (
                          <p className="text-emerald-400 font-mono text-[10px] mt-1">Impact: ₹{fmt(a.potential_saving_or_impact)}/yr</p>
                        )}
                      </div>
                      <span style={{ color: 'var(--text-faint)' }} className="text-sm">{open ? "▲" : "▼"}</span>
                    </div>
                    <AnimatePresence>
                      {open && (
                        <motion.div initial={{ height:0,opacity:0 }} animate={{ height:"auto",opacity:1 }} exit={{ height:0,opacity:0 }}
                          className="overflow-hidden" style={{ borderTop: '1px solid var(--border)' }}>
                          <div className="p-4 space-y-3">
                            <div className="p-3" style={{ border: '1px solid rgba(228,0,43,0.1)', background: 'rgba(228,0,43,0.03)' }}>
                              <p className="font-mono text-[9px] text-[#E4002B] mb-1">Personal Impact</p>
                              <p className="text-sm">{a.personal_impact}</p>
                            </div>
                            {a.action_required && (
                              <div className="p-3" style={{ border: '1px solid var(--border)' }}>
                                <p className="font-mono text-[9px] mb-1" style={{ color: 'var(--text-muted)' }}>Action Required</p>
                                <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>{a.action_required}</p>
                              </div>
                            )}
                            <p className="font-mono text-[8px]" style={{ color: 'var(--text-faint)' }}>Source: {a.source}</p>
                          </div>
                        </motion.div>
                      )}
                    </AnimatePresence>
                  </div>
                );
              })}
            </>
          )}
        </div>
      )}

      {!fetched && !loading && (
        <div className="p-16 text-center" style={{ border: '1px solid var(--border)' }}>
          <p className="text-massive text-3xl mb-4" style={{ color: 'var(--text-faint)' }}>ALERTS</p>
          <p className="font-mono text-[10px]" style={{ color: 'var(--text-faint)' }}>Configure profile above or click Get Alerts</p>
        </div>
      )}
    </div>
  );
}
