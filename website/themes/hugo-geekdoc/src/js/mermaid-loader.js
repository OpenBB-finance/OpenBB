document.addEventListener("DOMContentLoaded", function (event) {
  let currentMode = localStorage.getItem(THEME);
  let darkModeQuery = window.matchMedia("(prefers-color-scheme: dark)");
  let primaryColor = "#ececff";
  let darkMode = false;

  if (
    currentMode === DARK_MODE ||
    (currentMode === AUTO_MODE && darkModeQuery.matches)
  ) {
    primaryColor = "#6C617E";
    darkMode = true;
  }

  mermaid.initialize({
    flowchart: { useMaxWidth: true },
    theme: "base",
    themeVariables: {
      darkMode: darkMode,
      primaryColor: primaryColor,
    },
  });
});
