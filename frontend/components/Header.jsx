"use client";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState, useEffect } from "react";

const NAV = [
  { label: "Tax",       href: "/tax" },
  { label: "Portfolio",  href: "/portfolio" },
  { label: "Couples",    href: "/couples" },
  { label: "Health",     href: "/health" },
  { label: "FIRE",       href: "/fire" },
  { label: "Afford",     href: "/afford" },
  { label: "Budget",     href: "/budget" },
  { label: "Alerts",     href: "/alerts" },
];

export default function Header() {
  const path = usePathname();
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
    <header className="sticky top-0 z-50 backdrop-blur-xl" style={{ background: 'color-mix(in srgb, var(--bg) 80%, transparent)', borderBottom: '1px solid var(--border)' }}>
      <div className="max-w-7xl mx-auto px-6 md:px-12 flex items-center justify-between h-14">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-1.5">
          <span className="text-[#E4002B] font-black text-lg">ET</span>
          <span style={{ color: 'var(--text-faint)' }} className="text-lg font-extralight">×</span>
          <span style={{ color: 'var(--text-primary)' }} className="font-bold text-sm tracking-wide">MoneyMentor AI</span>
        </Link>

        {/* Nav */}
        <nav className="flex items-center gap-1">
          {NAV.map((n) => {
            const active = path === n.href || (n.href !== "/" && path?.startsWith(n.href));
            return (
              <Link key={n.href} href={n.href}
                className="font-mono text-[10px] uppercase tracking-[0.1em] px-3 py-1.5 transition-all border cursor-none"
                style={{
                  borderColor: active ? 'rgba(228, 0, 43, 0.3)' : 'transparent',
                  color: active ? '#E4002B' : 'var(--text-muted)',
                  background: active ? 'rgba(228, 0, 43, 0.05)' : 'transparent',
                }}
                onMouseEnter={(e) => { if (!active) { e.target.style.color = 'var(--text-primary)'; e.target.style.borderColor = 'var(--border)'; }}}
                onMouseLeave={(e) => { if (!active) { e.target.style.color = 'var(--text-muted)'; e.target.style.borderColor = 'transparent'; }}}
              >
                [{n.label}]
              </Link>
            );
          })}
        </nav>

        {/* Right: Theme toggle + badge */}
        <div className="flex items-center gap-3">
          <button onClick={toggleTheme} title="Toggle theme"
            className="w-8 h-8 rounded-full border flex items-center justify-center transition-all hover:scale-110 cursor-none"
            style={{ borderColor: 'var(--border)', color: 'var(--text-muted)' }}>
            {theme === "dark" ? (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v2.25m6.364.386l-1.591 1.591M21 12h-2.25m-.386 6.364l-1.591-1.591M12 18.75V21m-4.773-4.227l-1.591 1.591M5.25 12H3m4.227-4.773L5.636 5.636M15.75 12a3.75 3.75 0 11-7.5 0 3.75 3.75 0 017.5 0z" />
              </svg>
            ) : (
              <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0118 15.75c-5.385 0-9.75-4.365-9.75-9.75 0-1.33.266-2.597.748-3.752A9.753 9.753 0 003 11.25C3 16.635 7.365 21 12.75 21a9.753 9.753 0 009.002-5.998z" />
              </svg>
            )}
          </button>
          <span className="hidden lg:block font-mono text-[9px] border px-3 py-1.5 tracking-wider"
            style={{ color: '#E4002B', borderColor: 'rgba(228, 0, 43, 0.25)' }}>
            ET AI HACKATHON 2026
          </span>
        </div>
      </div>
    </header>
  );
}
