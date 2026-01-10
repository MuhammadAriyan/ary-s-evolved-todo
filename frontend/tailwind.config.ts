import type { Config } from "tailwindcss"

const config: Config = {
  darkMode: ["class"],
  content: [
    "./pages/**/*.{ts,tsx}",
    "./components/**/*.{ts,tsx}",
    "./app/**/*.{ts,tsx}",
    "./src/**/*.{ts,tsx}",
  ],
  theme: {
    extend: {
      fontFamily: {
        chelsea: ["Chelsea Market", "system-ui", "sans-serif"],
        sans: ["system-ui", "-apple-system", "BlinkMacSystemFont", "Segoe UI", "Roboto", "sans-serif"],
      },
      colors: {
        border: "hsl(var(--border))",
        input: "hsl(var(--input))",
        ring: "hsl(var(--ring))",
        background: "hsl(var(--background))",
        foreground: "hsl(var(--foreground))",
        primary: {
          DEFAULT: "hsl(var(--primary))",
          foreground: "hsl(var(--primary-foreground))",
        },
        secondary: {
          DEFAULT: "hsl(var(--secondary))",
          foreground: "hsl(var(--secondary-foreground))",
        },
        destructive: {
          DEFAULT: "hsl(var(--destructive))",
          foreground: "hsl(var(--destructive-foreground))",
        },
        muted: {
          DEFAULT: "hsl(var(--muted))",
          foreground: "hsl(var(--muted-foreground))",
        },
        accent: {
          DEFAULT: "hsl(var(--accent))",
          foreground: "hsl(var(--accent-foreground))",
        },
        popover: {
          DEFAULT: "hsl(var(--popover))",
          foreground: "hsl(var(--popover-foreground))",
        },
        card: {
          DEFAULT: "hsl(var(--card))",
          foreground: "hsl(var(--card-foreground))",
        },
        // Sky-Aura Glass Color Palette
        "aura-purple": {
          DEFAULT: "#9929EA",
          50: "#faf5ff",
          100: "#f3e8ff",
          200: "#e9d5ff",
          300: "#d8b4fe",
          400: "#c084fc",
          500: "#9929EA",
          600: "#7c3aed",
          700: "#6d28d9",
          800: "#5b21b6",
          900: "#4c1d95",
        },
        "aura-magenta": {
          DEFAULT: "#FF5FCF",
          50: "#fdf2f8",
          100: "#fce7f3",
          200: "#fbcfe8",
          300: "#f9a8d4",
          400: "#FF5FCF",
        },
        "aura-gold": {
          DEFAULT: "#FAEB92",
          50: "#fefce8",
          100: "#FAEB92",
        },
      },
      borderRadius: {
        lg: "var(--radius)",
        md: "calc(var(--radius) - 2px)",
        sm: "calc(var(--radius) - 4px)",
        glass: "1.5rem",
        "glass-lg": "2rem",
      },
      backdropBlur: {
        xs: "2px",
        glass: "12px",
        heavy: "20px",
      },
      boxShadow: {
        "glass-sm": "0 0 10px rgba(125, 211, 252, 0.2), 0 0 20px rgba(186, 230, 253, 0.1)",
        "glass-md": "0 0 20px rgba(125, 211, 252, 0.3), 0 0 40px rgba(186, 230, 253, 0.2)",
        "glass-lg": "0 0 30px rgba(125, 211, 252, 0.4), 0 0 60px rgba(186, 230, 253, 0.3)",
        bloom: "0 0 20px rgba(125, 211, 252, 0.3), 0 0 40px rgba(186, 230, 253, 0.2), 0 8px 32px rgba(224, 242, 254, 0.4)",
      },
      animation: {
        fadeIn: "fadeIn 0.3s ease-in-out",
        float: "float 4s ease-in-out infinite",
        breathe: "breathe 3s ease-in-out infinite",
        gradient: "gradient 12s ease infinite",
        "tasks-fade": "tasksFade 0.5s ease-out forwards",
        "content-bounce": "contentBounce 1s ease-out forwards",
      },
      keyframes: {
        fadeIn: {
          "0%": { opacity: "0", transform: "translateY(10px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
        float: {
          "0%, 100%": { transform: "translateY(0px)" },
          "50%": { transform: "translateY(-8px)" },
        },
        breathe: {
          "0%, 100%": { transform: "scale(1)", opacity: "0.8" },
          "50%": { transform: "scale(1.02)", opacity: "1" },
        },
        gradient: {
          "0%, 100%": {
            backgroundPosition: "0% 50%",
          },
          "25%": {
            backgroundPosition: "50% 50%",
          },
          "50%": {
            backgroundPosition: "100% 50%",
          },
          "75%": {
            backgroundPosition: "50% 50%",
          },
        },
        tasksFade: {
          "0%": { opacity: "0" },
          "100%": { opacity: "1" },
        },
        contentBounce: {
          "0%": { opacity: "0", transform: "translateY(40px)" },
          "60%": { transform: "translateY(-10px)" },
          "80%": { transform: "translateY(5px)" },
          "100%": { opacity: "1", transform: "translateY(0)" },
        },
      },
    },
  },
  plugins: [],
}

export default config
