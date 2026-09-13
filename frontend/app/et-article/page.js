"use client";
import { useRouter } from "next/navigation";

export default function ETArticlePage() {
  const router = useRouter();

  return (
    <div className="space-y-8 max-w-3xl mx-auto">
      <div className="font-mono text-[10px] tracking-wider" style={{ color: 'var(--text-faint)' }}>
        <span className="text-[#E4002B]">ET Wealth</span> / Tax Planning / Budget 2025
      </div>

      <article className="space-y-6">
        <div className="space-y-3">
          <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em]">Tax Planning</span>
          <h1 className="text-massive text-3xl md:text-5xl leading-[0.9]">BUDGET 2025:<br/>NEW TAX REGIME<br/>IS NOW DEFAULT</h1>
          <p className="text-editorial text-xl" style={{ color: 'var(--text-muted)' }}>What every salaried employee must do before April 1</p>
          <div className="font-mono text-[9px] flex gap-3" style={{ color: 'var(--text-faint)' }}>
            <span>By ET Wealth Bureau</span><span>|</span><span>Mar 24, 2026</span><span>|</span><span>5 min read</span>
          </div>
        </div>

        <div className="h-48 flex items-center justify-center" style={{ border: '1px solid var(--border)', background: 'linear-gradient(135deg, rgba(228,0,43,0.05), transparent)' }}>
          <p className="text-massive text-4xl" style={{ color: 'var(--text-faint)' }}>BUDGET 2025</p>
        </div>

        <div className="space-y-5 leading-relaxed text-[15px]" style={{ color: 'var(--text-secondary)' }}>
          <p>In a significant move that impacts every salaried Indian, the government has made the <strong style={{ color: 'var(--text-primary)' }}>New Tax Regime the default</strong> starting FY 2025-26. This means if you don&apos;t proactively inform your employer about your regime preference, your TDS will be calculated under the New Regime.</p>
          <p>The New Regime offers lower slab rates and a <strong style={{ color: 'var(--text-primary)' }}>full rebate up to Rs 12 lakh</strong> of taxable income under Section 87A. However, it strips away most deductions — no 80C, no HRA exemption, no home loan interest under Section 24(b).</p>

          <div className="my-8 p-8" style={{ border: '1px solid rgba(228,0,43,0.3)', background: 'rgba(228,0,43,0.03)' }}>
            <div className="flex gap-2 mb-3">
              <span className="font-mono text-[9px] text-[#E4002B] border border-[#E4002B]/20 px-2 py-0.5">AI-Powered</span>
              <span className="font-mono text-[9px] text-[#E4002B] border border-[#E4002B]/20 px-2 py-0.5">ET Exclusive</span>
            </div>
            <h3 className="text-massive text-xl mb-2">WHICH REGIME SAVES YOU MORE?</h3>
            <p className="text-editorial mb-6" style={{ color: 'var(--text-muted)' }}>Upload your Form 16 and get an instant comparison — powered by MoneyMentor AI.</p>
            <button onClick={() => router.push("/tax")} className="btn-primary">Analyse My Tax Impact →</button>
          </div>

          <p><strong style={{ color: 'var(--text-primary)' }}>Who should stay on Old Regime?</strong> If your total deductions under 80C, 80D, HRA, and home loan interest exceed Rs 3.75 lakh, the Old Regime is likely better.</p>
          <p><strong style={{ color: 'var(--text-primary)' }}>The deadline is April 1, 2026.</strong> If you don&apos;t submit Form 12B, TDS will default to the New Regime for the entire year. The time to act is now.</p>
        </div>

        <div className="p-6 flex items-start gap-4" style={{ border: '1px solid var(--border)' }}>
          <div className="text-massive text-2xl shrink-0" style={{ color: 'var(--text-faint)' }}>X-RAY</div>
          <div>
            <p className="text-sm font-medium">Is your mutual fund portfolio underperforming?</p>
            <p className="text-xs mt-1" style={{ color: 'var(--text-muted)' }}>Upload your CAMS statement to check fund overlap and NIFTY 50 benchmark comparison.</p>
            <button onClick={() => router.push("/portfolio")} className="btn-bracket text-[9px] mt-3">Portfolio X-Ray →</button>
          </div>
        </div>

        <div className="flex flex-wrap gap-2 pt-4" style={{ borderTop: '1px solid var(--border)' }}>
          {["Budget 2025", "New Tax Regime", "Income Tax", "Section 87A", "Form 16", "Tax Saving"].map(t => (
            <span key={t} className="font-mono text-[9px] px-3 py-1 border" style={{ borderColor: 'var(--border)', color: 'var(--text-faint)' }}>{t}</span>
          ))}
        </div>
      </article>

      <div className="space-y-3 pb-8">
        <p className="font-mono text-[10px] tracking-wider" style={{ color: 'var(--text-muted)' }}>More from ET Wealth</p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            { title: "RBI Cuts Repo Rate by 25bps — Will Your EMI Fall?", tag: "RBI", cta: "/alerts" },
            { title: "ELSS vs PPF vs NPS: Where to Invest Rs 1.5 Lakh", tag: "Tax", cta: "/tax" },
            { title: "5 Signs Your Portfolio Needs a Rebalance", tag: "Invest", cta: "/portfolio" },
            { title: "How Much to Retire at 45? A FIRE Calculator", tag: "FIRE", cta: "/fire" },
          ].map(a => (
            <div key={a.title} onClick={() => router.push(a.cta)}
              className="p-4 cursor-pointer group transition-all" style={{ border: '1px solid var(--border)' }}
              onMouseEnter={e => e.currentTarget.style.borderColor = 'rgba(228,0,43,0.3)'}
              onMouseLeave={e => e.currentTarget.style.borderColor = 'var(--border)'}
            >
              <span className="font-mono text-[9px] text-[#E4002B]">{a.tag}</span>
              <p className="text-sm mt-1 group-hover:text-[#E4002B] transition-colors">{a.title}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
