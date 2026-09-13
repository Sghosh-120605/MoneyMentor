import Header from "./Header";

export default function SubLayout({ children }) {
  return (
    <div className="min-h-screen flex flex-col themed-bg">
      <Header />
      <main className="flex-1 px-6 md:px-12 py-10 max-w-6xl mx-auto w-full">
        {children}
      </main>
      <footer style={{ borderTop: '1px solid var(--border)' }} className="py-6 px-6">
        <div className="max-w-6xl mx-auto flex flex-col md:flex-row justify-between items-center gap-3">
          <span className="font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-faint)' }}>🔒 Data processed in-memory</span>
          <span className="font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-faint)' }}>
            <span className="text-[#E4002B] font-bold">ET</span> × MoneyMentor AI
          </span>
          <span className="font-mono text-[9px] tracking-wider" style={{ color: 'var(--text-faint)' }}>🧮 Deterministic tax engine</span>
        </div>
      </footer>
    </div>
  );
}
