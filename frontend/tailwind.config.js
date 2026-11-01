/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./src/pages/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/components/**/*.{js,ts,jsx,tsx,mdx}",
    "./src/app/**/*.{js,ts,jsx,tsx,mdx}",
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        background: {
          DEFAULT: "#080B11",
          secondary: "#0F1420",
          card: "#141A29",
          hover: "#1A2338",
        },
        primary: {
          50: "#EEF2FF",
          100: "#E0E7FF",
          200: "#C7D2FE",
          300: "#A5B4FC",
          400: "#818CF8",
          500: "#6366F1",
          600: "#4F46E5",
          700: "#4338CA",
          800: "#3730A3",
          900: "#312E81",
        },
        accent: {
          purple: "#8B5CF6",
          cyan: "#06B6D4",
          emerald: "#10B981",
          rose: "#F43F5E",
          amber: "#F59E0B",
        },
        border: {
          subtle: "rgba(255, 255, 255, 0.08)",
          glow: "rgba(99, 102, 241, 0.3)",
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        devanagari: ['Noto Sans Devanagari', 'Mangal', 'sans-serif'],
      },
      animation: {
        'pulse-slow': 'pulse 3s cubic-bezier(0.4, 0, 0.6, 1) infinite',
        'wave': 'wave 1.2s ease-in-out infinite',
      },
      keyframes: {
        wave: {
          '0%, 100%': { height: '20%' },
          '50%': { height: '100%' },
        }
      }
    },
  },
  plugins: [],
};
