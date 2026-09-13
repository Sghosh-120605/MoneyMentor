const fmt = (n) => "₹" + Math.round(n || 0).toLocaleString("en-IN");

export default function MissedDeductions({ deductions }) {
  if (!deductions || deductions.length === 0) return null;
  return (
    <div className="p-6 h-fit space-y-3" style={{ border: '1px solid var(--border)' }}>
      <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-2">Missed Deductions</p>
      {deductions.map((d, i) => (
        <div key={i} className="p-4 transition-all hover:opacity-80" style={{ border: '1px solid var(--border)' }}>
          <div className="flex justify-between items-start mb-1">
            <h4 className="text-sm font-medium">{d.section}</h4>
            <span className={`font-mono text-[9px] px-2 py-0.5 border ${
              d.priority === "high" ? "text-[#E4002B] border-[#E4002B]/20" :
              d.priority === "medium" ? "text-amber-400 border-amber-500/20" : "text-gray-400 border-gray-500/20"
            }`}>{d.priority}</span>
          </div>
          <p className="text-xs" style={{ color: 'var(--text-muted)' }}>{d.description}</p>
          <div className="flex gap-4 mt-2 font-mono text-[10px]">
            <span style={{ color: 'var(--text-faint)' }}>Limit: {fmt(d.limit)}</span>
            <span className="text-emerald-400">Save: {fmt(d.potential_saving)}</span>
          </div>
        </div>
      ))}
    </div>
  );
}
