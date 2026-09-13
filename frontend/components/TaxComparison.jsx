const fmt = (n) => "₹" + Math.round(n || 0).toLocaleString("en-IN");

export default function TaxComparison({ comparison }) {
  if (!comparison) return null;
  const rows = [
    ["Gross Income", comparison.gross_income, comparison.gross_income],
    ["Deductions", comparison.old_total_deductions, comparison.new_standard_deduction],
    ["Taxable Income", comparison.old_taxable_income, comparison.new_taxable_income],
    ["Tax Before Rebate", comparison.old_regime_tax_before_rebate, comparison.new_regime_tax_before_rebate],
    ["Rebate u/s 87A", comparison.old_87a_rebate || 0, comparison.new_87a_rebate || 0],
    ["Cess", comparison.old_cess, comparison.new_cess],
    ["Final Tax", comparison.old_regime_tax, comparison.new_regime_tax],
  ];

  return (
    <div className="p-6 h-fit" style={{ border: '1px solid var(--border)' }}>
      <p className="font-mono text-[10px] text-[#E4002B] tracking-wider mb-4">Old vs New Regime</p>
      <table className="w-full text-[12px]">
        <thead>
          <tr style={{ borderBottom: '1px solid var(--border)' }}>
            <th className="text-left font-normal py-2 font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-muted)' }}>Item</th>
            <th className="text-right font-normal py-2 font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-muted)' }}>Old</th>
            <th className="text-right font-normal py-2 font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-muted)' }}>New</th>
          </tr>
        </thead>
        <tbody className="font-mono">
          {rows.map(([label, oldVal, newVal], i) => (
            <tr key={i} className={i === rows.length - 1 ? "font-bold" : ""} style={{ borderBottom: '1px solid var(--border)' }}>
              <td className="py-2" style={{ color: 'var(--text-secondary)' }}>{label}</td>
              <td className="py-2 text-right">{fmt(oldVal)}</td>
              <td className="py-2 text-right">{fmt(newVal)}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <div className="mt-4 p-3 text-center" style={{ border: '1px solid rgba(228,0,43,0.2)', background: 'rgba(228,0,43,0.03)' }}>
        <p className="font-mono text-[9px] tracking-wider mb-1" style={{ color: 'var(--text-muted)' }}>Recommended Regime</p>
        <p className="text-massive text-2xl text-[#E4002B]">{comparison.recommended_regime.toUpperCase()}</p>
        <p className="text-emerald-400 font-mono text-[10px] mt-1">Saves {fmt(comparison.savings_amount)}</p>
      </div>
    </div>
  );
}
