/** @type {import('tailwindcss').Config} */
export default {
  content: ['./index.html', './src/**/*.{js,ts,jsx,tsx}'],
  theme: {
    extend: {
      fontFamily: {
        mono: ["'Courier New'", 'Courier', 'monospace'],
        sans: ["'Courier New'", 'Courier', 'monospace'],
      },
      colors: {
        'retro-bg': '#0a0a0a',
        'retro-surface': '#141414',
        'retro-border': '#2a2a2a',
        'retro-cyan': '#00fff8',
        'retro-magenta': '#ff00ff',
        'retro-green': '#00ff41',
        'retro-yellow': '#ffff00',
        'retro-red': '#ff3355',
        'retro-blue': '#3388ff',
        'retro-orange': '#ff8800',
        agent: {
          security: '#EF4444',
          architecture: '#3B82F6',
          quality: '#22C55E',
          performance: '#F59E0B',
          ux: '#A855F7',
          vision: '#EC4899',
        },
      },
      animation: {
        'pulse-dot': 'pulse-dot 1.4s ease-in-out infinite',
        'fade-in': 'fadeIn 0.5s ease-out forwards',
        'slide-up': 'slideUp 0.5s ease-out forwards',
        blink: 'blink 1s step-end infinite',
      },
      keyframes: {
        'pulse-dot': {
          '0%, 80%, 100%': { opacity: '0' },
          '40%': { opacity: '1' },
        },
        fadeIn: {
          from: { opacity: '0', transform: 'translateY(10px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(20px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
        blink: {
          '0%, 100%': { opacity: '1' },
          '50%': { opacity: '0' },
        },
      },
    },
  },
  plugins: [],
};
