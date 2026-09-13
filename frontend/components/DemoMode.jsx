/**
 * DemoMode — Persona picker that loads pre-built demo data.
 * Drop this into any page to add instant demo functionality.
 *
 * Usage:
 *   <DemoMode section="tax" onLoad={(data) => setResult(data)} />
 */
"use client";
import { useState } from "react";

const PERSONAS = [
  { id: "sunita", name: "Sunita Verma", role: "Teacher · Delhi", income: "₹8L/yr", emoji: "👩‍🏫", color: "from-pink-600/20 to-rose-600/20 border-pink-500/30" },
  { id: "arjun", name: "Arjun Mehta", role: "Software Engineer · Bengaluru", income: "₹24L/yr", emoji: "👨‍💻", color: "from-indigo-600/20 to-blue-600/20 border-indigo-500/30" },
  { id: "kavita", name: "Kavita Shah", role: "Business Owner · Mumbai", income: "₹50L/yr", emoji: "👩‍💼", color: "from-amber-600/20 to-orange-600/20 border-amber-500/30" },
];

const API_BASE = process.env.NEXT_PUBLIC_API_URL !== undefined 
    ? process.env.NEXT_PUBLIC_API_URL 
    : (typeof window !== 'undefined' ? "" : "http://localhost:8000");

export default function DemoMode({ section, onLoad, className = "" }) {
  const [loading, setLoading] = useState(null);
  const [open, setOpen] = useState(false);

  const load = async (persona) => {
    setLoading(persona);
    try {
      const res = await fetch(`${API_BASE}/api/demo/${section}/${persona}`);
      if (!res.ok) throw new Error("Demo data not found for this section.");
      const data = await res.json();
      onLoad(data, persona);
      setOpen(false);
    } catch (e) {
      console.error(e);
    } finally {
      setLoading(null);
    }
  };

  return (
    <div className={`${className}`}>
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-2 px-4 py-2 rounded-xl bg-white/5 border border-white/10 text-gray-400 text-sm hover:text-white hover:bg-white/10 transition-all"
      >
        <span>🎭</span>
        <span>Try Demo Persona</span>
        <span className="text-xs bg-indigo-500/20 text-indigo-400 px-1.5 py-0.5 rounded-full">No upload needed</span>
        <span className="ml-auto">{open ? "▲" : "▼"}</span>
      </button>

      {open && (
        <div className="mt-2 grid grid-cols-1 sm:grid-cols-3 gap-3 animate-fade-in">
          {PERSONAS.map((p) => (
            <button
              key={p.id}
              onClick={() => load(p.id)}
              disabled={!!loading}
              className={`p-4 rounded-xl bg-gradient-to-br border text-left hover:scale-[1.02] transition-all disabled:opacity-60 ${p.color}`}
            >
              <div className="flex items-center gap-2 mb-2">
                <span className="text-2xl">{p.emoji}</span>
                {loading === p.id && (
                  <div className="w-4 h-4 rounded-full border-2 border-white/30 border-t-white animate-spin" />
                )}
              </div>
              <p className="text-white font-semibold text-sm">{p.name}</p>
              <p className="text-gray-400 text-xs mt-0.5">{p.role}</p>
              <p className="text-gray-500 text-xs">{p.income}</p>
            </button>
          ))}
        </div>
      )}
    </div>
  );
}
