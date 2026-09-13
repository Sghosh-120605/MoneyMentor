/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./app/**/*.{js,ts,jsx,tsx,mdx}",
    "./components/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  theme: {
    extend: {
      colors: {
        unseen: {
          black: "#000000",
          offwhite: "#E5E5E5",
          red: "#E4002B",      // ET Red as main accent
          yellow: "#FACC15",   // alternative accent
          grey: "#111111"
        },
      },
      fontFamily: {
        sans: ["var(--font-inter)", "sans-serif"],
        anton: ["var(--font-anton)", "sans-serif"],
        playfair: ["var(--font-playfair)", "serif"],
        mono: ["var(--font-space-mono)", "monospace"],
      },
      backgroundImage: {
        'ascii-pattern': "url('/ascii-bg.svg')", // placeholder for texture
      }
    },
  },
  plugins: [],
};
