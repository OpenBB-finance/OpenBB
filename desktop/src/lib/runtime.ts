export function isTauriRuntime(): boolean {
  if (typeof window === "undefined") {
    return false;
  }

  const candidate = window as Window & { __TAURI_INTERNALS__?: unknown };
  return typeof candidate.__TAURI_INTERNALS__ !== "undefined";
}
