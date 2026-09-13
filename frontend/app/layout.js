import "./globals.css";
import { Anton, Playfair_Display, Space_Mono, Inter } from "next/font/google";
import CustomCursor from "../components/CustomCursor";

const anton = Anton({ weight: "400", subsets: ["latin"], variable: "--font-anton" });
const playfair = Playfair_Display({ subsets: ["latin"], style: ["italic", "normal"], variable: "--font-playfair" });
const spaceMono = Space_Mono({ weight: ["400", "700"], subsets: ["latin"], variable: "--font-space-mono" });
const inter = Inter({ subsets: ["latin"], variable: "--font-inter" });

export const metadata = {
  title: "ET × MoneyMentor AI",
  description: "India's first AI-powered personal CFO — by Economic Times Wealth.",
};

export default function RootLayout({ children }) {
  return (
    <html lang="en" className={`${anton.variable} ${playfair.variable} ${spaceMono.variable} ${inter.variable}`}>
      <body className="font-sans overflow-x-hidden" style={{ background: 'var(--bg)', color: 'var(--text-primary)' }}>
        <CustomCursor />
        {children}
      </body>
    </html>
  );
}
