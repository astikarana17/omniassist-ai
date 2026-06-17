import type { Config } from "tailwindcss";

const config: Config = {
  darkMode: "class",
  content: [
    "./src/pages/**/*.{ts,tsx}",
    "./src/components/**/*.{ts,tsx}",
    "./src/app/**/*.{ts,tsx}",
  ],
  theme: {
    container: {
      center: true,
      padding: "1.5rem",
      screens: { "2xl": "1280px" },
    },
    extend: {
      colors: {
        border: "hsl(var(--border))",
        "border-strong": "hsl(var(--border-strong))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        subtle: "hsl(var(--subtle))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
          hover: "hsl(var(--primary-hover))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        ai: {
          DEFAULT: "hsl(var(--ai))",
          foreground: "hsl(var(--ai-foreground))",
        },
        success: "hsl(var(--success))",
        warning: "hsl(var(--warning))",
        danger: "hsl(var(--danger))",
        info: "hsl(var(--info))",
      },
      borderRadius: {
        sm: "6px",
        md: "8px",
        lg: "12px",
        xl: "16px",
        "2xl": "20px",
        "3xl": "28px",
      },
      fontFamily: {
        sans: ["var(--font-geist-sans)", "Inter", "system-ui", "sans-serif"],
        mono: ["var(--font-geist-mono)", "monospace"],
      },
      boxShadow: {
        sm: "0 1px 2px rgba(0,0,0,0.40)",
        md: "0 4px 12px rgba(0,0,0,0.45)",
        lg: "0 12px 32px rgba(0,0,0,0.55)",
        xl: "0 24px 64px rgba(0,0,0,0.60)",
        "glow-brand": "0 0 0 1px rgba(79,70,229,0.35), 0 12px 44px -8px rgba(79,70,229,0.42)",
        "glow-ai": "0 0 36px -2px rgba(34,211,238,0.45)",
        "glow-emerald": "0 0 30px -2px rgba(16,185,129,0.40)",
        card: "inset 0 1px 0 0 rgba(255,255,255,0.05), 0 10px 34px -12px rgba(0,0,0,0.65)",
      },
      backgroundImage: {
        "gradient-brand": "linear-gradient(135deg, #4F46E5 0%, #22D3EE 100%)",
        "gradient-ai": "linear-gradient(135deg, #6366F1 0%, #22D3EE 100%)",
        "gradient-emerald": "linear-gradient(135deg, #10B981 0%, #22D3EE 100%)",
        "gradient-iris": "linear-gradient(135deg, #6366F1 0%, #4F46E5 50%, #7C3AED 100%)",
        "gradient-mesh":
          "radial-gradient(at 16% 18%, rgba(79,70,229,0.20), transparent 55%), radial-gradient(at 84% 14%, rgba(34,211,238,0.16), transparent 55%), radial-gradient(at 60% 88%, rgba(16,185,129,0.10), transparent 55%)",
      },
      keyframes: {
        "accordion-down": {
          from: { height: "0" },
          to: { height: "var(--radix-accordion-content-height)" },
        },
        "accordion-up": {
          from: { height: "var(--radix-accordion-content-height)" },
          to: { height: "0" },
        },
        shimmer: {
          "100%": { transform: "translateX(100%)" },
        },
        "gradient-x": {
          "0%, 100%": { backgroundPosition: "0% 50%" },
          "50%": { backgroundPosition: "100% 50%" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0)" },
          "50%": { transform: "translateY(-6px)" },
        },
        "float-slow": {
          "0%, 100%": { transform: "translateY(0) translateX(0)" },
          "50%": { transform: "translateY(-14px) translateX(6px)" },
        },
        aurora: {
          "0%, 100%": { transform: "translate(0,0) rotate(0deg) scale(1)" },
          "33%": { transform: "translate(4%, -3%) rotate(8deg) scale(1.05)" },
          "66%": { transform: "translate(-3%, 4%) rotate(-6deg) scale(0.97)" },
        },
        "glow-pulse": {
          "0%, 100%": { opacity: "0.55" },
          "50%": { opacity: "1" },
        },
        "spin-slow": { to: { transform: "rotate(360deg)" } },
        "pulse-dot": {
          "0%, 100%": { opacity: "1", transform: "scale(1)" },
          "50%": { opacity: "0.4", transform: "scale(0.85)" },
        },
        "pulse-ring": {
          "0%": { transform: "scale(0.9)", opacity: "0.7" },
          "70%, 100%": { transform: "scale(1.8)", opacity: "0" },
        },
      },
      animation: {
        "accordion-down": "accordion-down 0.2s ease-out",
        "accordion-up": "accordion-up 0.2s ease-out",
        shimmer: "shimmer 1.6s infinite",
        "gradient-x": "gradient-x 6s ease infinite",
        float: "float 4s ease-in-out infinite",
        "float-slow": "float-slow 9s ease-in-out infinite",
        aurora: "aurora 20s ease-in-out infinite",
        "glow-pulse": "glow-pulse 3.2s ease-in-out infinite",
        "spin-slow": "spin-slow 16s linear infinite",
        "pulse-dot": "pulse-dot 1.4s ease-in-out infinite",
        "pulse-ring": "pulse-ring 2.4s ease-out infinite",
      },
    },
  },
  plugins: [require("tailwindcss-animate")],
};

export default config;
