const DARK_MODE = "dark";
const LIGHT_MODE = "light";
const AUTO_MODE = "auto";
const THEME = "hugo-geekdoc";

const TOGGLE_MODES = [AUTO_MODE, DARK_MODE, LIGHT_MODE];

(applyTheme = function (init = true) {
  let html = document.documentElement;
  let currentMode = TOGGLE_MODES.includes(localStorage.getItem(THEME))
    ? localStorage.getItem(THEME)
    : AUTO_MODE;

  html.setAttribute("class", "color-toggle-" + currentMode);
  localStorage.setItem(THEME, currentMode);

  if (currentMode === AUTO_MODE) {
    html.removeAttribute("color-mode");
  } else {
    html.setAttribute("color-mode", currentMode);
  }

  if (!init) {
    // Reload required to re-initialise e.g. Mermaid with the new theme and re-parse the Mermaid code blocks.
    location.reload();
  }
})();

document.addEventListener("DOMContentLoaded", (event) => {
  const darkModeToggle = document.getElementById("gdoc-dark-mode");

  darkModeToggle.onclick = function () {
    let currentMode = localStorage.getItem(THEME);
    let nextMode = toggle(TOGGLE_MODES, currentMode);

    localStorage.setItem(THEME, TOGGLE_MODES[nextMode]);
    applyTheme(false);
  };
});

function toggle(list = [], value) {
  current = list.indexOf(value);
  max = list.length - 1;
  next = 0;

  if (current < max) {
    next = current + 1;
  }

  return next;
}
