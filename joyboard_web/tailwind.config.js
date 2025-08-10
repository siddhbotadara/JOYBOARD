/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './templates/**/*.html',
    './**/templates/**/*.html',
    './static/**/*.css',
    './**/*.js',
  ],
  safelist: [
    'font-heading',
    'font-section',
    'font-button',
    'font-body',
    'font-logo',

  ],
  theme: {
    extend: {
      fontFamily: {
        heading: ['Unbounded', 'sans-serif'],
        section: ['Rajdhani', 'sans-serif'],
        button: ['Audiowide', 'sans-serif'],
        body: ['JetBrains Mono', 'monospace'],
        logo: ['Orbitron', 'sans-serif'],
      },
    },
  },
  plugins: [],
}
