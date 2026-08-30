/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        primary: {
          DEFAULT: '#6366f1',
          dark: '#4f46e5',
          light: '#a5b4fc'
        },
        success: '#22c55e',
        danger: '#ef4444',
        warning: '#f59e0b',
        surface: '#f8fafc'
      }
    }
  },
  plugins: []
}
