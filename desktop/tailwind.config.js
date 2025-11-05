/** @type {import('tailwindcss').Config} */
import conf from "@openbb/ui-pro/tailwind.config";
export default {
  presets: [conf],
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {},
    container: {
      center: true,
    },
  },
  plugins: [],
}
