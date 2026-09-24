/** @type {import('tailwindcss').Config} */
export default {
  darkMode: 'class',
  content: ['./index.html', './src/**/*.{vue,js}'],
  theme: {
    extend: {
      colors: {
        // Iron/blood red — the one accent. Named "primary" so every
        // existing bg-primary/text-primary/border-primary usage across
        // the app inherits it without a find-and-replace.
        primary: {
          DEFAULT: '#C31E24',
          dark: '#9E181D',
          light: '#E2585C'
        },
        // Sparing hazard-tape accent — structural details only (stripes,
        // PR highlight), never a competing second brand color.
        hazard: '#E8B23D',
        success: '#5C7A3D',
        danger: '#C31E24',
        warning: '#E8B23D',
        // Raw concrete/chalk, not a cream SaaS off-white.
        surface: '#F1EFE9',
        card: '#FFFFFF',
        ink: '#141414',
        steel: {
          50: '#F5F4F2',
          100: '#E8E6E1',
          300: '#B9B6AE',
          700: '#4A4846',
          900: '#1A1B1D',
          950: '#111213'
        }
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Oswald', '"IBM Plex Sans"', 'ui-sans-serif', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace']
      },
      borderRadius: {
        // Sharp by default everywhere (cards, buttons, inputs, pills).
        // `full` is deliberately left alone — it's how spinners and true
        // circular elements ask for a circle, and overriding it globally
        // would turn every loading spinner into a spinning square.
        DEFAULT: '2px',
        sm: '2px',
        md: '2px',
        lg: '2px',
        xl: '3px',
        '2xl': '4px'
      }
    }
  },
  plugins: []
}
