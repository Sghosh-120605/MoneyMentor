"use client";
import { useState } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";
import { uploadForm16, analyzeTax } from "../../lib/api";

export default function TaxPage() {
  const [loading, setLoading] = useState(false);
  const [step, setStep] = useState("upload");
  const [taxProfile, setTaxProfile] = useState(null);
  const [error, setError] = useState(null);
  const [dragOver, setDragOver] = useState(false);
  const [options, setOptions] = useState({
    rent_paid: 0, is_metro: true, age: 30,
    has_health_insurance: false, has_nps: false, has_home_loan: false,
  });
  const router = useRouter();

  const handleUpload = async (fileList) => {
    if (!fileList || fileList.length === 0) return;
    setLoading(true); setError(null);
    try {
      const res = await uploadForm16(fileList[0]);
      if (res.success) { setTaxProfile(res.tax_profile); setStep("options"); }
      else setError(res.message || "Upload failed");
    } catch (e) { setError(e.message); }
    finally { setLoading(false); }
  };

  const handleAnalyze = async () => {
    setStep("analyzing"); setLoading(true);
    try {
      const result = await analyzeTax(taxProfile, options);
      sessionStorage.setItem("analysisResult", JSON.stringify(result));
      router.push("/dashboard");
    } catch (e) { setError(e.message); setStep("options"); }
    finally { setLoading(false); }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div>
        <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] block mb-2">Tax Analysis</span>
        <h1 className="text-massive text-4xl md:text-6xl">TAX<br/>WIZARD</h1>
        <p className="text-editorial text-lg mt-2" style={{ color: 'var(--text-muted)' }}>
          Upload your Form 16 and get an instant Old vs New regime comparison
        </p>
      </div>

      <AnimatePresence mode="wait">
        {step === "upload" && (
          <motion.div key="upload" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <div className="relative p-8 md:p-12" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
              <div className="absolute -top-px left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#E4002B] to-transparent" />

              <div className="flex items-center gap-2 mb-6">
                <div className="w-2 h-2 rounded-full bg-[#E4002B] animate-pulse" />
                <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.15em] uppercase">Upload Form 16</span>
              </div>

              <p className="text-sm leading-relaxed mb-8" style={{ color: 'var(--text-secondary)' }}>
                Drop your Form 16 PDF and get an instant comparison between Old and New tax regimes with exact ₹ savings — powered by GPT-4o.
              </p>

              <div
                className="relative group cursor-pointer"
                onDragOver={(e) => { e.preventDefault(); setDragOver(true); }}
                onDragLeave={() => setDragOver(false)}
                onDrop={(e) => { e.preventDefault(); setDragOver(false); handleUpload(e.dataTransfer.files); }}
              >
                <div className={`h-44 border-2 border-dashed flex flex-col items-center justify-center gap-4 transition-all duration-300 ${
                  dragOver ? 'border-[#E4002B] shadow-[0_0_40px_rgba(228,0,43,0.1)]' : ''
                }`} style={{
                  borderColor: dragOver ? '#E4002B' : 'var(--border-hover)',
                  background: dragOver ? 'rgba(228, 0, 43, 0.03)' : 'transparent',
                }}>
                  {loading ? (
                    <>
                      <motion.div animate={{ rotate: 360 }} transition={{ duration: 1, repeat: Infinity, ease: "linear" }}
                        className="w-10 h-10 border-2 border-t-[#E4002B] rounded-full" style={{ borderColor: 'var(--border)', borderTopColor: '#E4002B' }} />
                      <span className="font-mono text-[10px]" style={{ color: 'var(--text-muted)' }}>Parsing with GPT-4o...</span>
                    </>
                  ) : (
                    <>
                      <div className="w-12 h-12 border rounded-sm flex items-center justify-center group-hover:border-[#E4002B]/40 transition-colors" style={{ borderColor: 'var(--border)' }}>
                        <svg className="w-6 h-6 group-hover:text-[#E4002B] transition-colors" style={{ color: 'var(--text-muted)' }} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                          <path strokeLinecap="round" strokeLinejoin="round" d="M3 16.5v2.25A2.25 2.25 0 005.25 21h13.5A2.25 2.25 0 0021 18.75V16.5m-13.5-9L12 3m0 0l4.5 4.5M12 3v13.5" />
                        </svg>
                      </div>
                      <div className="text-center">
                        <p className="text-sm" style={{ color: 'var(--text-secondary)' }}>Drag & drop PDF or <span className="text-[#E4002B] underline underline-offset-2 cursor-pointer">browse files</span></p>
                        <p className="font-mono text-[8px] mt-1" style={{ color: 'var(--text-faint)' }}>PDF • Max 15MB • Processed in-memory, never stored</p>
                      </div>
                    </>
                  )}
                  <input type="file" accept="application/pdf" onChange={(e) => handleUpload(e.target.files)}
                    className="absolute inset-0 opacity-0 cursor-pointer" />
                </div>
                {loading && (
                  <motion.div className="absolute bottom-0 left-0 h-[2px] bg-[#E4002B]"
                    animate={{ width: ["0%", "100%"] }} transition={{ duration: 4, ease: "linear" }} />
                )}
              </div>

              {error && (
                <p className="font-mono text-[10px] text-[#E4002B] mt-4 p-3" style={{ border: '1px solid rgba(228,0,43,0.2)', background: 'rgba(228,0,43,0.05)' }}>
                  ⚠ {error}
                </p>
              )}
            </div>
          </motion.div>
        )}

        {step === "options" && (
          <motion.div key="options" initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0, y: -20 }}>
            <div className="relative p-8 md:p-10" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
              <div className="absolute -top-px left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-emerald-500 to-transparent" />
              <div className="flex items-center gap-2 mb-6">
                <div className="w-2 h-2 rounded-full bg-emerald-500" />
                <span className="font-mono text-[10px] text-emerald-400 tracking-[0.15em]">Form 16 Parsed ✓</span>
              </div>
              <p className="text-sm mb-6" style={{ color: 'var(--text-secondary)' }}>Fine-tune your parameters for a precise Old vs New regime comparison.</p>

              <div className="space-y-3">
                {[
                  ["Annual Rent Paid", "rent_paid", "number"],
                  ["Metro City", "is_metro", "checkbox"],
                  ["Health Insurance", "has_health_insurance", "checkbox"],
                  ["Home Loan", "has_home_loan", "checkbox"],
                  ["NPS Contribution", "has_nps", "checkbox"],
                ].map(([label, key, type]) => (
                  <label key={key} className="flex items-center justify-between py-2 group cursor-pointer" style={{ borderBottom: '1px solid var(--border)' }}>
                    <span className="text-sm" style={{ color: 'var(--text-secondary)' }}>{label}</span>
                    {type === "checkbox" ? (
                      <input type="checkbox" checked={options[key]} onChange={e => setOptions({...options, [key]: e.target.checked})} className="accent-[#E4002B] w-4 h-4" />
                    ) : (
                      <input type="number" value={options[key]} onChange={e => setOptions({...options, [key]: +e.target.value})} placeholder="0"
                        className="bg-transparent text-right text-sm font-mono w-28 outline-none" style={{ color: 'var(--text-primary)', borderBottom: '1px solid var(--border)' }} />
                    )}
                  </label>
                ))}
              </div>

              <button onClick={handleAnalyze} disabled={loading}
                className="btn-primary w-full mt-6 text-center disabled:opacity-50">
                {loading ? "Computing..." : "Execute Analysis →"}
              </button>
              {error && <p className="font-mono text-[10px] text-[#E4002B] mt-3">⚠ {error}</p>}
            </div>
          </motion.div>
        )}

        {step === "analyzing" && (
          <motion.div key="analyzing" initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
            <div className="relative p-16 text-center" style={{ background: 'var(--bg-card)', border: '1px solid var(--border)' }}>
              <div className="absolute -top-px left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-[#E4002B] to-transparent animate-pulse" />
              <motion.div animate={{ rotate: 360 }} transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                className="w-12 h-12 border-2 border-t-[#E4002B] rounded-full mx-auto mb-6" style={{ borderColor: 'var(--border)', borderTopColor: '#E4002B' }} />
              <p className="font-mono text-[10px] tracking-wider" style={{ color: 'var(--text-muted)' }}>Analysing deductions...</p>
              <p className="font-mono text-[8px] mt-2" style={{ color: 'var(--text-faint)' }}>Comparing Old vs New regime</p>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
