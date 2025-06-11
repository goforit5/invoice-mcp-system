/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        'electric-cyan': '#00D4FF',
        'deep-purple': '#6366F1',
        'soft-mint': '#F0FDF4',
        'warm-peach': '#FEF3E2',
        'gentle-rose': '#FDF2F8',
        'cool-gray': '#F8FAFC',
        'invoice-blue': '#3B82F6',
        'invoice-green': '#10B981',
        'invoice-orange': '#F59E0B',
      },
      fontFamily: {
        'sf-pro': ['-apple-system', 'BlinkMacSystemFont', 'SF Pro Display', 'SF Pro Text', 'system-ui', 'sans-serif'],
      },
      borderRadius: {
        '2xl': '16px',
        '3xl': '24px',
      },
      scale: {
        '98': '0.98',
      }
    },
  },
  plugins: [],
}