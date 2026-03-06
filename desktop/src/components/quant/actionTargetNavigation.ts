import type { MouseEvent } from "react";

const HIGHLIGHT_CLASS = "quant-action-highlight";
const HIGHLIGHT_DURATION_MS = 1400;

export function createActionTargetClickHandler(href: string) {
  return (event: MouseEvent<HTMLAnchorElement>) => {
    event.preventDefault();
    const id = href.startsWith("#") ? href.slice(1) : href;
    const target = document.getElementById(id);
    if (!target) {
      return;
    }

    target.classList.remove(HIGHLIGHT_CLASS);
    void target.offsetWidth;
    target.classList.add(HIGHLIGHT_CLASS);

    target.scrollIntoView({ behavior: "smooth", block: "center" });
    const path = `${window.location.pathname}${window.location.search}${href}`;
    window.history.replaceState(null, "", path);

    window.setTimeout(() => {
      target.classList.remove(HIGHLIGHT_CLASS);
    }, HIGHLIGHT_DURATION_MS);
  };
}
