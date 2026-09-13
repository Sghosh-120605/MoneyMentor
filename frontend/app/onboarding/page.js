"use client";
import { useState, useEffect } from "react";
import { useRouter } from "next/navigation";
import { motion, AnimatePresence } from "framer-motion";

const QUESTIONS = [
  {
    id: "q1",
    question: "What's your primary financial focus right now?",
    options: [
      "Saving tax and finding deductions",
      "Organizing and optimizing my investments",
      "Planning for big events or early retirement",
      "Managing day-to-day money and budgeting",
    ],
  },
  {
    id: "q2",
    question: "How would you describe your current money situation?",
    options: [
      "It's a mess, I need help sorting it out",
      "I'm okay, but I know I could be doing better",
      "I'm tracking things closely but want an expert second look",
      "I'm combining finances with my partner",
    ],
  },
  {
    id: "q3",
    question: "What do you want help with right now?",
    options: [
      "Fix my taxes and review Form 16",
      "Review my mutual funds for overlap and high expense ratios",
      "See if I can afford a big purchase right now",
      "Calculate exactly when I can afford to retire",
    ],
  },
];

export default function Onboarding() {
  const router = useRouter();
  const [step, setStep] = useState(0);
  const [answers, setAnswers] = useState({ q1: "", q2: "", q3: "" });
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [feedback, setFeedback] = useState(false);

  const handleSelect = async (option) => {
    const currentQId = QUESTIONS[step].id;
    const newAnswers = { ...answers, [currentQId]: option };
    setAnswers(newAnswers);
    setFeedback(true);

    if (step < QUESTIONS.length - 1) {
      setTimeout(() => {
        setFeedback(false);
        setStep(step + 1);
      }, 700);
    } else {
      // Finished all 3
      setTimeout(async () => {
        setLoading(true);
        setFeedback(false);
        try {
          const res = await fetch("/api/onboarding", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ answers: newAnswers }),
          });
          if (!res.ok) {
            throw new Error("API returned status " + res.status);
          }
          const data = await res.json();
          setResult(data);
        } catch (err) {
          setResult({
            recommended_path: "/health",
            tool_name: "Money Health Score",
            reasoning: "We couldn't connect, let's start with a quick health checkup!",
          });
        }
      }, 500);
    }
  };

  const handleContinue = () => {
    if (result && result.recommended_path) {
      router.push(result.recommended_path);
    }
  };

  return (
    <div className="min-h-screen themed-bg flex items-center justify-center p-6 relative overflow-hidden" style={{ color: 'var(--text-primary)' }}>
      {/* Grid texture */}
      <div className="absolute inset-0 opacity-[0.02]" style={{
        backgroundImage: `url("data:image/svg+xml,%3Csvg width='40' height='40' viewBox='0 0 40 40' xmlns='http://www.w3.org/2000/svg'%3E%3Cpath d='M0 40L40 0H20L0 20M40 40V20L20 40' fill='%23888' fill-opacity='1'/%3E%3C/svg%3E")`,
      }} />

      {/* Navbar overlay */}
      <nav className="fixed top-0 w-full z-50 p-6 flex items-center justify-between pointer-events-none">
        <div className="flex items-center gap-1.5 opacity-50">
           <span className="text-[#E4002B] font-black text-xl tracking-tight">ET</span>
           <span className="text-xl font-extralight" style={{ color: 'var(--text-faint)' }}>×</span>
           <span className="font-bold text-[15px] tracking-wide" style={{ color: 'var(--text-primary)' }}>MoneyMentor</span>
        </div>
      </nav>

      <div className="relative z-10 w-full max-w-2xl px-4 md:px-0">
        <AnimatePresence mode="wait">
          {!loading ? (
            <motion.div
              key={step}
              initial={{ opacity: 0, x: 20 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -20 }}
              transition={{ duration: 0.4 }}
              className="flex flex-col gap-8"
            >
              <div>
                <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] uppercase block mb-4">
                  Step 0{step + 1} / 03
                </span>
                <h2 className="text-massive text-3xl md:text-5xl leading-tight">
                  {QUESTIONS[step].question}
                </h2>
              </div>

              <div className="flex flex-col gap-3 min-h-[300px]">
                <AnimatePresence mode="wait">
                  {feedback ? (
                    <motion.div
                      key="feedback"
                      initial={{ opacity: 0, scale: 0.95 }}
                      animate={{ opacity: 1, scale: 1 }}
                      exit={{ opacity: 0, scale: 1.05 }}
                      className="absolute inset-x-0 h-full flex flex-col items-center justify-center pointer-events-none mt-16"
                    >
                      <span className="text-2xl font-bold" style={{ color: 'var(--text-primary)' }}>
                        {step === 0 ? "Got it 👍" : step === 1 ? "Makes sense ✅" : "Perfect. Setting things up... ✨"}
                      </span>
                    </motion.div>
                  ) : (
                    <motion.div
                      key="options"
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      exit={{ opacity: 0, x: -20 }}
                      className="flex flex-col gap-3 w-full"
                    >
                      {QUESTIONS[step].options.map((option, idx) => (
                        <button
                          key={idx}
                          onClick={() => handleSelect(option)}
                          className="text-left p-6 md:p-8 rounded-none border hover:border-[#E4002B]/60 transition-all duration-300 group hover:translate-x-2"
                          style={{ borderColor: 'color-mix(in srgb, currentColor 20%, transparent)', background: 'color-mix(in srgb, var(--bg-card) 50%, transparent)' }}
                        >
                          <span className="font-mono text-[9px] block mb-2 opacity-50 group-hover:text-[#E4002B]">OPTION {["A","B","C","D"][idx]}</span>
                          <span className="text-editorial text-lg md:text-xl group-hover:opacity-100 opacity-80 transition-opacity">
                            {option}
                          </span>
                        </button>
                      ))}
                    </motion.div>
                  )}
                </AnimatePresence>
              </div>
            </motion.div>
          ) : (
            <motion.div
              key="result"
              initial={{ opacity: 0, scale: 0.95 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{ duration: 0.6 }}
              className="text-center flex flex-col items-center gap-6"
            >
              {!result ? (
                <>
                  <div className="w-16 h-16 border-t-2 border-[#E4002B] border-r-2 border-r-transparent rounded-full animate-spin"></div>
                  <p className="font-mono text-[10px] tracking-[0.2em] animate-pulse mt-4">AI IS ANALYSING YOUR PROFILE</p>
                </>
              ) : (
                <>
                  <span className="font-mono text-[10px] text-[#E4002B] tracking-[0.2em] uppercase block mb-2">
                    Based on your answers, here's your next best financial move
                  </span>
                  
                  <h2 className="text-massive text-4xl md:text-6xl" style={{ color: 'var(--text-primary)' }}>
                    Your {(result.tool_name || "Money Health Score").replace(/^Your /i, '')}
                  </h2>
                  
                  <div className="mt-8 p-6 text-left border-l-2 border-[#E4002B]" style={{ background: 'color-mix(in srgb, var(--bg-card) 50%, transparent)' }}>
                    <div className="flex items-center gap-2 mb-2">
                       <span className="text-xs font-mono opacity-50">WHY WE RECOMMEND THIS</span>
                    </div>
                    <p className="text-editorial text-lg md:text-xl opacity-80 max-w-lg mx-auto leading-relaxed">
                      "{result.reasoning || "Let's start your journey with a quick financial health checkup!"}"
                    </p>
                  </div>

                  <button 
                    onClick={handleContinue}
                    className="btn-primary mt-12 px-12 py-4 shadow-lg shadow-[#E4002B]/20 transition-transform hover:scale-105"
                  >
                    Build My Plan →
                  </button>
                </>
              )}
            </motion.div>
          )}
        </AnimatePresence>
      </div>
    </div>
  );
}
