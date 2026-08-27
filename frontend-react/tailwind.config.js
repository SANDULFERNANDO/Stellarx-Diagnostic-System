/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        stellarNavy: '#114a72',
        stellarDark: '#0f2d4a',
        bgGray: '#f4f7f9'
      }
    },
  },
  plugins: [],
}
