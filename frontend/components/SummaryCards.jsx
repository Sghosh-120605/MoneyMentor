"use client";
import { useEffect, useState } from "react";

function AnimatedNumber({ value, prefix = "₹", duration = 1500 }) {
  const [display, setDisplay] = useState(0);
  useEffect(() => {
    if (!value) return;
    let start = 0;
    const step = value / (duration / 16);
    const timer = setInterval(() => {
      start += step;
      if (start >= value) { setDisplay(value); clearInterval(timer); }
      else setDisplay(Math.round(start));
    }, 16);
    return () => clearInterval(timer);
  }, [value, duration]);
  return <>{prefix}{display.toLocaleString("en-IN")}</>;
}

export default function SummaryCards({ comparison, totalSavings, tds }) {
  if (!comparison) return null;
  const { old_regime_tax, new_regime_tax, recommended_regime, savings_amount } = comparison;
  const overpaying = recommended_regime === "new" ? old_regime_tax - new_regime_tax : new_regime_tax - old_regime_tax;

  const cards = [
    {
      label: "You Are Overpaying",
      value: overpaying,
      sub: `Switch to ${recommended_regime} regime`,
      color: "red",
      icon: "🔴",
    },
    {
      label: "Total Potential Savings",
      value: totalSavings + savings_amount,
      sub: "From regime switch + missed deductions",
      color: "green",
      icon: "💰",
    },
    {
      label: "TDS Already Paid",
      value: tds || 0,
      sub: "Deducted by your employer",
      color: "blue",
      icon: "🏦",
    },
    {
      label: "Recommended Regime",
      value: null,
      sub: recommended_regime === "old" ? "Old Regime is better for you" : "New Regime is better for you",
      color: "amber",
      icon: "⭐",
      textValue: recommended_regime.toUpperCase(),
    },
  ];

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 animate-slide-up">
      {cards.map((c, i) => (
        <div
          key={i}
          className={`glass-card p-5 glow-${c.color}`}
          style={{ animationDelay: `${i * 100}ms` }}
        >
          <div className="flex justify-between items-start mb-3">
            <span className="text-xs text-gray-400 uppercase tracking-wider font-medium">{c.label}</span>
            <span className="text-2xl">{c.icon}</span>
          </div>
          <div className={`text-2xl font-bold text-${c.color === "red" ? "red" : c.color === "green" ? "green" : c.color === "amber" ? "amber" : "indigo"}-400`}>
            {c.textValue || <AnimatedNumber value={c.value} />}
          </div>
          <p className="text-xs text-gray-500 mt-2">{c.sub}</p>
        </div>
      ))}
    </div>
  );
}
