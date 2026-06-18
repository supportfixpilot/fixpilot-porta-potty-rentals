/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./*.html",
    "./porta-potty-rental-*-*/index.html",
    "./services/*.html",
    "./blog/*.html",
    "./industries/*.html",
    "./compare/*.html",
    "./use-cases/*.html",
    "./es/**/*.html",
    "./zip/**/*.html",
    "./calculator/**/*.html",
    "./about/**/*.html",
  ],
  // Per-page brand color is supplied via CSS custom properties on :root.
  // Safe fallback values match the most common (blue) palette so nothing
  // looks broken even if a page forgets to declare its brand vars.
  theme: {
    extend: {
      fontFamily: {
        sans: ['"Plus Jakarta Sans"', '"Rubik"', '"Inter"', "system-ui", "sans-serif"],
      },
      colors: {
        brand: {
          50: "var(--brand-50, #eff6ff)",
          100: "var(--brand-100, #dbeafe)",
          200: "var(--brand-200, #bfdbfe)",
          300: "var(--brand-300, #93c5fd)",
          400: "var(--brand-400, #60a5fa)",
          500: "var(--brand-500, #3b82f6)",
          600: "var(--brand-600, #2563eb)",
          700: "var(--brand-700, #1d4ed8)",
          800: "var(--brand-800, #1e40af)",
          900: "var(--brand-900, #1e3a8a)",
          950: "var(--brand-950, #172554)",
        },
        cta: "var(--cta, #ea580c)",
      },
      keyframes: {
        "pulse-shadow": {
          "0%": { boxShadow: "0 0 0 0 rgba(234, 88, 12, 0.7)" },
          "70%": { boxShadow: "0 0 0 15px rgba(234, 88, 12, 0)" },
          "100%": { boxShadow: "0 0 0 0 rgba(234, 88, 12, 0)" },
        },
      },
      animation: {
        "pulse-shadow": "pulse-shadow 2s infinite",
      },
    },
  },
  // Safelist common dynamic classes that may be generated at template time.
  safelist: [
    { pattern: /^(bg|text|border|ring|from|to|via|fill|stroke)-brand-(50|100|200|300|400|500|600|700|800|900|950)$/ },
    { pattern: /^(bg|text|border)-cta$/ },
    // group-hover variants used in city card grids
    { pattern: /^group-hover:/, variants: ["group-hover"] },
    "pulse-btn",
    "group",
    "group-hover:brightness-110",
    "group-hover:text-cta",
    "group-hover:text-white",
    "group-hover:shadow-xl",
    "group-hover:scale-105",
    "hover:-translate-y-0.5",
    "hover:-translate-y-1",
    "hover:-translate-y-2",
    "mt-0.5",
  ],
  plugins: [],
};
