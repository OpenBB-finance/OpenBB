import { useState, useEffect } from "react";

export default function useDarkMode(initialTheme: "dark" | "light") {
  const [theme, setTheme] = useState(initialTheme);
  const colorTheme = theme === "dark" ? "light" : "dark";

  useEffect(() => {
    const root = window.document.documentElement;
    root.classList.remove(colorTheme);
    root.classList.add(theme);
  }, [theme, colorTheme]);

  return [colorTheme, setTheme];
}
