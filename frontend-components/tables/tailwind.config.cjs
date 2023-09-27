/** @type {import('tailwindcss').Config} */
module.exports = {
  darkMode: "class",
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
      screens: {
        smh: { raw: "(max-height: 450px)" },
        mdl: { raw: "(min-width: 890px)" },
      },
      colors: {
        "grey-50": "#f6f6f6ff",
        "grey-100": "#eaeaeaff",
        "grey-200": "#dcdcdcff",
        "grey-300": "#c8c8c8ff",
        "grey-400": "#a2a2a2ff",
        "grey-500": "#808080ff",
        "grey-600": "#5a5a5aff",
        "grey-700": "#474747ff",
        "grey-800": "#2a2a2aff",
        "grey-850": "#131313ff",
        "grey-900": "#070707ff",
        "burgundy-300": "#B47DA0",
        "burgundy-400": "#9B5181",
        "burgundy-500": "#822661",
        "burgundy-900": "#340F27",
      },
    },
  },
  plugins: [],
};
