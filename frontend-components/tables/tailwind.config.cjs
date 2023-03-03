/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ["./index.html", "./src/**/*.{js,ts,jsx,tsx}"],
  theme: {
    extend: {
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
      },
    },
  },
  plugins: [],
};
