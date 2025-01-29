/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    "./templates/**/*.{html,js}",
    "./static/**/*.{html,js}",
    "./node_modules/flowbite/**/*.js",
  ],
  theme: {
    //   fontFamily: {
    //     poppins: ["Poppins", "sans-serif"],
    //   },
    extend: {
      keyframes: {
        wiggle: {
          "0%, 100%": { transform: "rotate(-3deg)" },
          "50%": { transform: "rotate(3deg)" },
        },
      },
      animation: {
        wiggle: "wiggle 1s ease-in-out infinite",
      },
      screens: {
        xsm: "350px",
        hxsm: "450px",
        navbarlg: "1060px",
        sm: "640px",
        md: "768px",
        lg: "1024px",
        xl: "1280px",
        "2xl": "1400px",
      },
    },
  },
  plugins: [require("flowbite/plugin")],
};
