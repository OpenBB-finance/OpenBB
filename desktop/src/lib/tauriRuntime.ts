export function isTauriRuntimeAvailable(): boolean {
  if (import.meta.env.MODE === "test") {
    return true;
  }

  if (typeof window === "undefined") {
    return true;
  }

  return typeof (window as Window & { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ !== "undefined";
}

export function getDesktopRuntimeMessage(tabName: string): string {
  return `The ${tabName} tab requires the Tauri desktop runtime. Browser-only mode is not supported.`;
}
