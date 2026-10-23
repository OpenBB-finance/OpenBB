(function () {
  "use strict";

  var root = document.documentElement;
  var PYWRY_CLASSES = ["pywry-theme-light", "pywry-theme-dark", "pywry-theme-system"];
  var applying = false;

  function requested() {
    var match = /[?&]theme=(light|dark)/i.exec(window.location.search || "");
    if (match) return match[1].toLowerCase();
    if (root.classList.contains("pywry-theme-light")) return "light";
    if (root.getAttribute("data-theme") === "light") return "light";
    return "dark";
  }

  var theme = requested();

  function paint() {
    applying = true;
    root.setAttribute("data-theme", theme);
    if (root.className.indexOf("pywry-theme-") !== -1) {
      PYWRY_CLASSES.forEach(function (name) {
        root.classList.remove(name);
      });
      root.classList.remove("light", "dark");
      root.classList.add("pywry-theme-" + theme, theme);
    }
    var grids = document.querySelectorAll('[class*="ag-theme-"]');
    for (var i = 0; i < grids.length; i += 1) {
      var grid = grids[i];
      var base = null;
      grid.classList.forEach(function (name) {
        if (name.indexOf("ag-theme-") === 0) base = name.replace(/-dark$/, "");
      });
      if (!base) continue;
      grid.classList.remove(base, base + "-dark");
      grid.classList.add(theme === "dark" ? base + "-dark" : base);
    }
    applying = false;
  }

  paint();

  if (window.MutationObserver) {
    new MutationObserver(function () {
      if (!applying) paint();
    }).observe(root, { attributes: true, attributeFilter: ["class", "data-theme"] });
  }

  function hostWindow() {
    var target = window.top || window.parent;
    return target && target !== window ? target : null;
  }

  var target = hostWindow();

  if (target) {
    target.postMessage(
      {
        type: "openbb-connect",
        widgets: window.__OPENBB_WIDGETS__ || [],
        params: [{ paramName: "theme", label: "Theme", type: "text", value: theme }]
      },
      "*"
    );
  }

  window.addEventListener("message", function (event) {
    var data = event.data;
    if (!data || typeof data !== "object") return;
    if (
      data.type !== "openbb-params-update" &&
      data.type !== "openbb:widget-params:update"
    ) {
      return;
    }
    var params = data.params || {};
    if (data.paramName) params[data.paramName] = data.value;
    var next = String(params.theme || "").toLowerCase();
    if ((next === "light" || next === "dark") && next !== theme) {
      theme = next;
      paint();
    }
  });
})();
