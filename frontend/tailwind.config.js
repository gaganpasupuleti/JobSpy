/** @type {import('tailwindcss').Config} */
export default {
  content: ["./index.html", "./src/**/*.{js,jsx}"],
  theme: {
    extend: {
      colors: {
        navy: {
          DEFAULT: "#1e3a5f",
          dark: "#152a45",
          light: "#2d4f7c",
        },
        cream: {
          DEFAULT: "#faf8f5",
          dark: "#f0ebe3",
        },
      },
      fontFamily: {
        sans: ["Inter", "system-ui", "sans-serif"],
      },
    },
  },
  plugins: [],
};
