import { isTauriRuntimeAvailable } from "./tauriRuntime";

function isHttpUrl(path: string): boolean {
  return /^https?:\/\//i.test(path);
}

function normalizeFilePath(path: string): string {
  return path.replace(/\\/g, "/");
}

export function buildFileHref(path: string): string {
  const normalized = normalizeFilePath(path).trim();
  if (!normalized) {
    return "file:///";
  }
  if (/^file:\/\//i.test(normalized)) {
    return normalized;
  }
  if (/^[A-Za-z]:\//.test(normalized)) {
    return `file:///${normalized}`;
  }
  if (normalized.startsWith("//")) {
    return `file:${normalized}`;
  }
  if (normalized.startsWith("/")) {
    return `file://${normalized}`;
  }
  return `file:///${normalized}`;
}

export function isLocalPathOpenSupported(): boolean {
  if (isTauriRuntimeAvailable()) {
    return true;
  }
  return typeof window !== "undefined" && typeof window.open === "function";
}

export async function openPathSafely(path: string): Promise<void> {
  const target = String(path ?? "").trim();
  if (!target) {
    throw new Error("No path is available to open.");
  }

  if (isTauriRuntimeAvailable()) {
    const opener = await import("@tauri-apps/plugin-opener");
    await opener.openPath(target);
    return;
  }

  if (typeof window === "undefined" || typeof window.open !== "function") {
    throw new Error("Path opening is unavailable in this runtime.");
  }

  const href = isHttpUrl(target) ? target : buildFileHref(target);
  const opened = window.open(href, "_blank", "noopener,noreferrer");
  if (!opened) {
    throw new Error("Browser blocked the open request. Use Copy Path instead.");
  }
}
