/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#2563eb', // Interactive Blue
        },
        secondary: {
          DEFAULT: '#1e293b', // Foundation Navy
        },
        tertiary: {
          DEFAULT: '#64748b', // Slate gray
        },
        background: '#f8fafc', // Neutral background
        surface: '#ffffff',
        border: '#e2e8f0', // Slate 200
        success: '#10b981', // Emerald
        warning: '#f59e0b', // Amber
        error: '#ef4444', // Red
      },
      fontFamily: {
        sans: ['Inter', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
