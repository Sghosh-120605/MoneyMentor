"use client";
import { useRef, useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import Image from "next/image";
import { motion, useScroll, useTransform, useInView } from "framer-motion";

const FEATURES = [
  { id: "01", title: "TAX\nWIZARD",       sub: "Old vs New regime comparison with AI deduction scan",     href: "/tax",       img: "/cards/tax.png" },
  { id: "02", title: "PORTFOLIO\nX-RAY",   sub: "XIRR, fund overlap, expense drag and rebalancing",       href: "/portfolio", img: "/cards/portfolio.png" },
  { id: "03", title: "COUPLE'S\nPLANNER",  sub: "Smart deduction assignment between partners",             href: "/couples",   img: "/cards/couples.png" },
  { id: "04", title: "MONEY\nHEALTH",      sub: "6-dimension financial fitness score in 2 minutes",        href: "/health",    img: "/cards/health.png" },
  { id: "05", title: "F.I.R.E\nPLANNER",   sub: "Retire early — corpus projection and SIP plan",           href: "/fire",      img: "/cards/fire.png" },
  { id: "06", title: "AFFORD\nADVISOR",     sub: "Should you buy it now, wait, or skip? AI verdict",        href: "/afford",    img: "/cards/afford.png" },
  { id: "07", title: "AI BUDGET\nPLANNER",  sub: "50/30/20 expense optimization with instant quick wins",      href: "/budget",    img: "/cards/budget.png" },
  { id: "08", title: "PROACTIVE\nALERTS",   sub: "Budget, RBI, SEBI alerts personalised for you",           href: "/alerts",    img: "/cards/alerts.png" },
];

const STATS = [
  { num: "₹25K+", label: "Avg savings found" },
  { num: "95%",   label: "Indians overpay tax" },
  { num: "60s",   label: "Full AI analysis" },
  { num: "9",     label: "Tools in one app" },
];

const HOW_IT_WORKS = [
  { step: "01", title: "Upload Form 16", desc: "Drop your salary slip PDF. We parse it in-memory — nothing is stored." },
  { step: "02", title: "AI Computes", desc: "GPT-4o identifies missed deductions and compares Old vs New regime." },
  { step: "03", title: "Get Your Plan", desc: "Exact ₹ savings, ranked actions, and a personalised tax-saving roadmap." },
];

function Reveal({ children, delay = 0, className = "" }) {
  const ref = useRef(null);
  const inView = useInView(ref, { once: true, margin: "-60px" });
  return (
    <motion.div ref={ref} className={className}
      initial={{ opacity: 0, y: 50 }}
      animate={inView ? { opacity: 1, y: 0 } : {}}
      transition={{ duration: 0.8, delay, ease: [0.16, 1, 0.3, 1] }}
    >{children}</motion.div>
  );
}

export default function Home() {
  const router = useRouter();
  const heroRef = useRef(null);
  const { scrollYProgress } = useScroll({ target: heroRef, offset: ["start start", "end start"] });
  const heroOpacity = useTransform(scrollYProgress, [0, 0.8], [1, 0]);

  const [theme, setTheme] = useState("dark");
  useEffect(() => {
    const saved = localStorage.getItem("theme") || "dark";
    setTheme(saved);
    document.documentElement.setAttribute("data-theme", saved);
  }, []);
  const toggleTheme = () => {
    const next = theme === "dark" ? "light" : "dark";
    setTheme(next);
    localStorage.setItem("theme", next);
    document.documentElement.setAttribute("data-theme", next);
  };

  return (
    <div className="themed-bg" style={{ color: 'var(--text-primary)' }}>

      {/* ═══ NAVBAR ═══ */}
      <nav className="fixed top-0 w-full z-50 backdrop-blur-xl" style={{ background: 'color-mix(in srgb, var(--bg) 80%, transparent)', borderBottom: '1px solid var(--border)' }}>
        <div className="max-w-[1400px] mx-auto px-6 md:px-12 h-16 flex items-center justify-between">
          <a href="/" className="flex items-center gap-1.5 group">
            <span className="text-[#E4002B] font-black text-xl tracking-tight">ET</span>
            <span className="text-xl font-extralight" style={{ color: 'var(--text-faint)' }}>×</span>
            <span className="font-bold text-[15px] tracking-wide" style={{ color: 'var(--text-primary)' }}>MoneyMentor AI</span>
          </a>
          <div className="hidden md:flex items-center gap-1">
            {["Tax", "Portfolio", "Couples", "Health", "FIRE", "Afford", "Budget", "Alerts"].map(l => (
              <a key={l} href={`/${l.toLowerCase()}`}
                className="font-mono text-[10px] uppercase tracking-[0.12em] px-3 py-1.5 border border-transparent hover:border-[var(--border)] transition-all"
                style={{ color: 'var(--text-muted)' }}
                onMouseEnter={e => e.target.style.color = 'var(--text-primary)'}
                onMouseLeave={e => e.target.style.color = 'var(--text-muted)'}
              >[{l}]</a>
            ))}
          </div>
          <div className="flex items-center gap-3">
            <button onClick={toggleTheme} title="Toggle theme"
              className="w-8 h-8 rounded-full border flex items-center justify-center transition-all hover:scale-110 cursor-none"
              style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
              {theme === "dark" ? (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" /></svg>
              ) : (
                <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}><path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" /></svg>
              )}
            </button>
            
          </div>
        </div>
      </nav>

      {/* ═══ HERO ═══ */}
      <motion.section ref={heroRef} style={{ opacity: heroOpacity }} className="relative min-h-screen flex items-center pt-16">
        {/* Grid texture */}
        <div className="absolute inset-0 opacity-[0.02]" style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40' fill='%23888' fill-opacity='1'/%3E%3C/svg%3E")`,
        }} />

        <div className="relative z-10 w-full max-w-[1400px] mx-auto px-6 md:px-12 text-center">
          <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.15, duration: 0.6 }}
            className="flex items-center justify-center gap-3 mb-8">
            <span className="h-[1px] w-8 bg-[#E4002B]" />
            <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.25em] uppercase">India's First AI-Powered CFO</span>
            <span className="h-[1px] w-8 bg-[#E4002B]" />
          </motion.div>

          <motion.h1
            initial={{ opacity: 0, y: 60 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.35, duration: 0.9, ease: [0.16, 1, 0.3, 1] }}
            className="text-massive text-[clamp(3.5rem,12vw,11rem)] leading-[0.85] mx-auto"
          >
            <span className="text-[#E4002B]">ET</span>
            <span style={{ color: 'var(--text-faint)' }} className="font-extralight text-[0.6em] mx-2 md:mx-4">×</span>
            <span style={{ color: 'var(--text-primary)' }}>MONEY</span>
            <br />
            <span style={{ color: 'var(--text-primary)' }}>MENTOR</span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 0.6 }}
            transition={{ delay: 1, duration: 0.7 }}
            className="text-editorial text-[clamp(1.1rem,2.5vw,2rem)] max-w-xl mx-auto mt-6 leading-snug"
            style={{ color: 'var(--text-secondary)' }}
          >
            Maximise your take-home salary with AI-powered tax analysis
          </motion.p>

          {/* CTA buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.3, duration: 0.6 }}
            className="flex flex-col sm:flex-row gap-4 justify-center mt-10"
          >
            <button onClick={() => router.push("/onboarding")} className="btn-primary text-center px-10 shadow-lg shadow-[#E4002B]/20">
              Let AI Guide Me ✨
            </button>
            <button onClick={() => router.push("/tax")} className="btn-bracket text-center">
              Analyse My Tax →
            </button>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 1.6, duration: 0.6 }}
            className="flex justify-center gap-10 md:gap-16 mt-16"
          >
            {STATS.map(s => (
              <div key={s.label}>
                <p className="text-massive text-xl md:text-2xl text-[#E4002B]">{s.num}</p>
                <p className="font-mono text-[8px] tracking-wider mt-1" style={{ color: 'var(--text-muted)' }}>{s.label}</p>
              </div>
            ))}
          </motion.div>
        </div>

        {/* Scroll hint */}
        <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ delay: 2 }}
          className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-2">
          <motion.div animate={{ y: [0, 6, 0] }} transition={{ duration: 1.8, repeat: Infinity }}
            className="w-[1px] h-8" style={{ background: 'linear-gradient(to bottom, var(--text-muted), transparent)' }} />
          <span className="font-mono text-[7px] tracking-[0.3em]" style={{ color: 'var(--text-faint)' }}>SCROLL</span>
        </motion.div>
      </motion.section>

      {/* ═══ FEATURE CARDS ═══ */}
      <section className="section-alt py-24 md:py-36 relative overflow-hidden">
        <div className="max-w-[1400px] mx-auto px-6 md:px-12">
          <div className="mb-16 md:mb-24">
            <Reveal>
              <span className="font-mono text-[10px] tracking-[0.2em] uppercase block mb-4 opacity-30">— What we do</span>
            </Reveal>
            <Reveal delay={0.05}>
              <h2 className="text-massive text-[clamp(3rem,8vw,8rem)] leading-[0.85]">A CFO</h2>
            </Reveal>
            <Reveal delay={0.1}>
              <p className="text-editorial text-[clamp(1.5rem,4vw,3.5rem)] opacity-40 mt-2">for every Indian</p>
            </Reveal>
          </div>

          <div className="flex gap-4 md:gap-5 overflow-x-auto pb-6 hide-scrollbar snap-x snap-mandatory -mx-6 px-6 md:-mx-12 md:px-12">
            {FEATURES.map((f, i) => (
              <Reveal key={f.id} delay={i * 0.06}>
                <div onClick={() => router.push(f.href)}
                  className="min-w-[260px] md:min-w-[280px] h-[420px] border-2 border-current/20 p-0 flex flex-col cursor-pointer transition-all duration-500 snap-center group hover:scale-[1.02] overflow-hidden"
                  style={{ borderColor: 'color-mix(in srgb, currentColor 20%, transparent)' }}
                >
                  {/* Image */}
                  <div className="relative h-[200px] overflow-hidden bg-black/5">
                    <Image src={f.img} alt={f.title.replace('\n', ' ')} fill className="object-cover opacity-70 group-hover:opacity-100 group-hover:scale-105 transition-all duration-700" />
                    <div className="absolute top-3 left-3 font-mono text-[10px] opacity-30">{f.id}</div>
                    <div className="absolute top-3 right-3">
                      <svg className="w-4 h-4 opacity-20 group-hover:opacity-60 -rotate-45 group-hover:rotate-0 transition-all duration-300" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
                        <path strokeLinecap="round" strokeLinejoin="round" d="M4.5 19.5l15-15m0 0H8.25m11.25 0v11.25" />
                      </svg>
                    </div>
                  </div>
                  {/* Text */}
                  <div className="p-6 flex-1 flex flex-col justify-end">
                    <h3 className="text-massive text-[2rem] md:text-[2.2rem] tracking-tight whitespace-pre-line leading-[0.9]">{f.title}</h3>
                    <p className="text-editorial text-[12px] mt-3 opacity-40 group-hover:opacity-70 transition-opacity">{f.sub}</p>
                  </div>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ HOW IT WORKS ═══ */}
      <section className="py-24 md:py-36 px-6 md:px-12" style={{ borderTop: '1px solid var(--border)' }}>
        <div className="max-w-[1400px] mx-auto">
          <Reveal>
            <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] uppercase block mb-4">— How it works</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="text-massive text-4xl md:text-6xl mb-16">THREE STEPS</h2>
          </Reveal>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
            {HOW_IT_WORKS.map((s, i) => (
              <Reveal key={s.step} delay={i * 0.1}>
                <div className="relative p-8" style={{ border: '1px solid var(--border)' }}>
                  <span className="text-massive text-[80px] text-[#E4002B] opacity-10 absolute top-2 right-4 leading-none">{s.step}</span>
                  <h3 className="text-massive text-xl mb-3">{s.title}</h3>
                  <p className="text-sm leading-relaxed" style={{ color: 'var(--text-secondary)' }}>{s.desc}</p>
                </div>
              </Reveal>
            ))}
          </div>
        </div>
      </section>

      {/* ═══ ET INTEGRATION (centered) ═══ */}
      <section className="py-24 md:py-36 px-6 md:px-12" style={{ borderTop: '1px solid var(--border)' }}>
        <div className="max-w-3xl mx-auto text-center">
          <Reveal>
            <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] uppercase block mb-6">— ET Wealth Integration</span>
          </Reveal>
          <Reveal delay={0.05}>
            <h2 className="text-massive text-5xl md:text-7xl leading-[0.85] mb-4">
              LIVES INSIDE <span className="text-[#E4002B]">ET</span>
            </h2>
          </Reveal>
          <Reveal delay={0.1}>
            <p className="text-editorial text-xl md:text-2xl mb-12" style={{ color: 'var(--text-muted)' }}>
              Embedded as a contextual AI widget inside Economic Times Wealth articles
            </p>
          </Reveal>

          <Reveal delay={0.2}>
            <div className="text-left relative p-8" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
              <div className="absolute -top-px left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#E4002B]/40 to-transparent" />
              <div className="flex items-center gap-2 mb-3">
                <span className="text-[#E4002B] font-black text-sm">ET</span>
                <span style={{ color: 'var(--text-faint)' }}>|</span>
                <span className="font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-muted)' }}>WEALTH • TAX PLANNING</span>
              </div>
              <h3 className="text-lg font-bold mb-2 leading-snug" style={{ color: 'var(--text-primary)' }}>
                Budget 2025: New Tax Regime Is Now Default — What Should You Do?
              </h3>
              <p className="text-sm leading-relaxed mb-6" style={{ color: 'var(--text-muted)' }}>
                "95% of Indians overpay tax because they don't know which regime is better for their salary bracket. Upload your Form 16 and find out in 60 seconds."
              </p>
              <button onClick={() => router.push("/et-article")}
                className="w-full py-4 bg-[#E4002B] text-white font-bold text-sm uppercase tracking-[0.12em] hover:opacity-85 transition-opacity">
                Read Full Article & Analyse →
              </button>
            </div>
          </Reveal>
        </div>
      </section>

      {/* ═══ FOOTER ═══ */}
      <footer style={{ borderTop: '1px solid var(--border)' }} className="py-10 px-6 md:px-12">
        <div className="max-w-[1400px] mx-auto flex flex-col md:flex-row justify-between items-center gap-4">
          <div className="flex items-center gap-1.5">
            <span className="text-[#E4002B] font-black text-sm">ET</span>
            <span style={{ color: 'var(--text-faint)' }}>×</span>
            <span className="text-xs font-medium" style={{ color: 'var(--text-muted)' }}>MoneyMentor AI</span>
          </div>
          <div className="flex gap-6 font-mono text-[8px] tracking-wider" style={{ color: 'var(--text-faint)' }}>
            <span>🔒 Processed in-memory</span>
            <span>🧮 Deterministic tax engine</span>
            <span>© 2026</span>
          </div>
        </div>
      </footer>
    </div>
  );
}
