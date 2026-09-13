export default function ActionPlan({ actions, summary }) {
  if (!actions || actions.length === 0) return null;
  return (
    <div className="p-6 space-y-4" style={{ border: '1px solid var(--border)' }}>
      <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-2">Action Plan</p>
      {summary && <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{summary}</p>}
      <div className="space-y-3">
        {actions.map((a, i) => (
          <div key={i} className="flex gap-4 p-4 transition-all hover:opacity-80" style={{ border: '1px solid var(--border)' }}>
            <span className="text-massive text-3xl text-[#E4002B] opacity-30 leading-none">{String(i + 1).padStart(2, "0")}</span>
            <div className="flex-1">
              <div className="flex justify-between items-start">
                <h4 className="text-sm font-medium">{a.title}</h4>
                <span className={`font-mono text-[9px] px-2 py-0.5 border ${
                  a.difficulty === "easy" ? "text-emerald-400 border-emerald-500/20" :
                  a.difficulty === "medium" ? "text-amber-400 border-amber-500/20" : "text-[#E4002B] border-[#E4002B]/20"
                }`}>{a.difficulty}</span>
              </div>
              <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>{a.description}</p>
              {a.savings_impact && (
                <p className="text-emerald-400 font-mono text-[10px] mt-2">Impact: {a.savings_impact}</p>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
