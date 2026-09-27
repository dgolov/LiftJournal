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
          DEFAULT: '#D92D3A',
          dark: '#B71F2C',
          light: '#F0646E'
        },
        // Sparing hazard-tape accent — structural details only (stripes,
        // PR highlight), never a competing second brand color.
        hazard: '#F0B429',
        success: '#2F9E6B',
        danger: '#D92D3A',
        warning: '#F0B429',
        // Cool graphite neutrals — a clean gym-floor grey rather than
        // warm concrete, so white cards lift off the page softly.
        surface: '#F3F4F7',
        card: '#FFFFFF',
        ink: '#171A21',
        steel: {
          50: '#F6F7F9',
          100: '#E6E8EE',
          300: '#AEB4C0',
          700: '#4B5260',
          900: '#1C2028',
          950: '#12151B'
        }
      },
      fontFamily: {
        sans: ['"IBM Plex Sans"', 'ui-sans-serif', 'system-ui', 'sans-serif'],
        display: ['Oswald', '"IBM Plex Sans"', 'ui-sans-serif', 'sans-serif'],
        mono: ['"IBM Plex Mono"', 'ui-monospace', 'monospace']
      },
      borderRadius: {
        // Soft, tiered corners: small controls < inputs/buttons < cards < sheets.
        // `full` stays a true circle for avatars, pills and spinners.
        DEFAULT: '6px',
        sm: '6px',
        md: '8px',
        lg: '10px',
        xl: '12px',
        '2xl': '16px',
        '3xl': '22px'
      },
      boxShadow: {
        // Layered, low-contrast shadows tinted with ink instead of pure black.
        soft: '0 1px 2px rgba(23,26,33,0.04), 0 2px 8px rgba(23,26,33,0.05)',
        lift: '0 2px 6px rgba(23,26,33,0.06), 0 12px 32px -8px rgba(23,26,33,0.18)',
        glow: '0 4px 14px -4px rgba(217,45,58,0.45)'
      }
    }
  },
  plugins: []
}
