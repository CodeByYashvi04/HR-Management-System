module.exports = {
  content: [
    "./pages/**/*.{html,js}",
    "./components/**/*.{html,js}",
    "./index.html",
    "./*.html"
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        // Primary Colors - Confident Blue
        primary: {
          DEFAULT: '#2563EB', // blue-600
          50: '#EFF6FF', // blue-50
          100: '#DBEAFE', // blue-100
          200: '#BFDBFE', // blue-200
          300: '#93C5FD', // blue-300
          400: '#60A5FA', // blue-400
          500: '#3B82F6', // blue-500
          600: '#2563EB', // blue-600
          700: '#1D4ED8', // blue-700
          800: '#1E40AF', // blue-800
          900: '#1E3A8A', // blue-900
          foreground: '#FFFFFF', // white
        },
        // Secondary Colors - Professional Slate
        secondary: {
          DEFAULT: '#64748B', // slate-500
          50: '#F8FAFC', // slate-50
          100: '#F1F5F9', // slate-100
          200: '#E2E8F0', // slate-200
          300: '#CBD5E1', // slate-300
          400: '#94A3B8', // slate-400
          500: '#64748B', // slate-500
          600: '#475569', // slate-600
          700: '#334155', // slate-700
          800: '#1E293B', // slate-800
          900: '#0F172A', // slate-900
          foreground: '#FFFFFF', // white
        },
        // Accent Colors - Warm Amber
        accent: {
          DEFAULT: '#F59E0B', // amber-500
          50: '#FFFBEB', // amber-50
          100: '#FEF3C7', // amber-100
          200: '#FDE68A', // amber-200
          300: '#FCD34D', // amber-300
          400: '#FBBF24', // amber-400
          500: '#F59E0B', // amber-500
          600: '#D97706', // amber-600
          700: '#B45309', // amber-700
          800: '#92400E', // amber-800
          900: '#78350F', // amber-900
          foreground: '#1F2937', // gray-800
        },
        // Background Colors
        background: {
          DEFAULT: '#FAFAFA', // gray-50
          foreground: '#1F2937', // gray-800
        },
        // Surface Colors
        surface: {
          DEFAULT: '#FFFFFF', // white
          foreground: '#374151', // gray-700
          hover: '#F9FAFB', // gray-50
          active: '#F3F4F6', // gray-100
        },
        // Text Colors
        'text-primary': '#1F2937', // gray-800
        'text-secondary': '#6B7280', // gray-500
        'text-tertiary': '#9CA3AF', // gray-400
        'text-disabled': '#D1D5DB', // gray-300
        // Status Colors - Success
        success: {
          DEFAULT: '#059669', // emerald-600
          50: '#ECFDF5', // emerald-50
          100: '#D1FAE5', // emerald-100
          200: '#A7F3D0', // emerald-200
          300: '#6EE7B7', // emerald-300
          400: '#34D399', // emerald-400
          500: '#10B981', // emerald-500
          600: '#059669', // emerald-600
          700: '#047857', // emerald-700
          800: '#065F46', // emerald-800
          900: '#064E3B', // emerald-900
          foreground: '#FFFFFF', // white
        },
        // Status Colors - Warning
        warning: {
          DEFAULT: '#D97706', // amber-600
          50: '#FFFBEB', // amber-50
          100: '#FEF3C7', // amber-100
          200: '#FDE68A', // amber-200
          300: '#FCD34D', // amber-300
          400: '#FBBF24', // amber-400
          500: '#F59E0B', // amber-500
          600: '#D97706', // amber-600
          700: '#B45309', // amber-700
          800: '#92400E', // amber-800
          900: '#78350F', // amber-900
          foreground: '#FFFFFF', // white
        },
        // Status Colors - Error
        error: {
          DEFAULT: '#DC2626', // red-600
          50: '#FEF2F2', // red-50
          100: '#FEE2E2', // red-100
          200: '#FECACA', // red-200
          300: '#FCA5A5', // red-300
          400: '#F87171', // red-400
          500: '#EF4444', // red-500
          600: '#DC2626', // red-600
          700: '#B91C1C', // red-700
          800: '#991B1B', // red-800
          900: '#7F1D1D', // red-900
          foreground: '#FFFFFF', // white
        },
        // Border Colors
        border: {
          DEFAULT: 'rgba(0, 0, 0, 0.08)',
          light: 'rgba(0, 0, 0, 0.04)',
          strong: 'rgba(0, 0, 0, 0.12)',
        },
      },
      fontFamily: {
        heading: ['Inter', 'sans-serif'],
        body: ['Source Sans Pro', 'sans-serif'],
        caption: ['IBM Plex Sans', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace'],
      },
      fontSize: {
        xs: ['0.875rem', { lineHeight: '1.4' }], // 14px
        sm: ['0.9375rem', { lineHeight: '1.6' }], // 15px
        base: ['1rem', { lineHeight: '1.6' }], // 16px
        lg: ['1.125rem', { lineHeight: '1.5' }], // 18px
        xl: ['1.25rem', { lineHeight: '1.4' }], // 20px
        '2xl': ['1.5rem', { lineHeight: '1.3' }], // 24px
        '3xl': ['1.875rem', { lineHeight: '1.25' }], // 30px
        '4xl': ['2.25rem', { lineHeight: '1.2' }], // 36px
      },
      spacing: {
        '1': '0.5rem', // 8px
        '2': '1rem', // 16px
        '3': '1.5rem', // 24px
        '4': '2rem', // 32px
        '6': '3rem', // 48px
        '8': '4rem', // 64px
        '12': '6rem', // 96px
      },
      borderRadius: {
        sm: '0.375rem', // 6px
        base: '0.75rem', // 12px
        md: '1.125rem', // 18px
        lg: '1.5rem', // 24px
        xl: '0.75rem', // 12px (for cards)
      },
      boxShadow: {
        sm: '0 2px 4px rgba(0, 0, 0, 0.08)',
        base: '0 4px 8px rgba(0, 0, 0, 0.1)',
        md: '0 6px 12px rgba(0, 0, 0, 0.12)',
        lg: '0 12px 24px rgba(0, 0, 0, 0.15)',
        xl: '0 20px 40px -8px rgba(0, 0, 0, 0.15)',
      },
      transitionDuration: {
        '250': '250ms',
        '350': '350ms',
      },
      transitionTimingFunction: {
        'out': 'cubic-bezier(0.4, 0, 0.2, 1)',
      },
      zIndex: {
        'base': '0',
        'card': '1',
        'dropdown': '50',
        'navigation': '100',
        'modal': '200',
        'toast': '300',
      },
      ringWidth: {
        '3': '3px',
      },
      ringOffsetWidth: {
        '2': '2px',
      },
      minWidth: {
        '44': '44px',
      },
      minHeight: {
        '44': '44px',
      },
      maxWidth: {
        'measure': '70ch',
      },
      letterSpacing: {
        'caption': '0.025em',
      },
    },
  },
  plugins: [
    function({ addUtilities }) {
      const newUtilities = {
        '.transition-base': {
          transition: 'all 250ms cubic-bezier(0.4, 0, 0.2, 1)',
        },
        '.transition-fast': {
          transition: 'all 150ms cubic-bezier(0.4, 0, 0.2, 1)',
        },
        '.transition-slow': {
          transition: 'all 350ms cubic-bezier(0.4, 0, 0.2, 1)',
        },
      }
      addUtilities(newUtilities)
    },
  ],
}