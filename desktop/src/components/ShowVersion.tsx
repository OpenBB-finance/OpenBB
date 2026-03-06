import { useState, useEffect } from "react";
import { getVersion } from "@tauri-apps/api/app";

let cachedVersion: string | null = null;

const isTauriRuntime = (): boolean => {
  if (typeof window === "undefined") return false;
  return typeof (window as Window & { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__ !== "undefined";
};

const safeGetVersion = async (): Promise<string> => {
  if (cachedVersion !== null) return cachedVersion;
  if (!isTauriRuntime()) {
    cachedVersion = "";
    return "";
  }
  try {
    cachedVersion = await getVersion();
    return cachedVersion;
  } catch (error) {
    // Browser mode intentionally runs without a Tauri bridge.
    if (isTauriRuntime()) {
      console.error("Failed to get version:", error);
    }
    cachedVersion = "";
    return "";
  }
};

export default function ShowVersion() {
  const [version, setVersion] = useState<string>(cachedVersion ?? "");

  useEffect(() => {
    if (cachedVersion !== null) return;
    safeGetVersion().then(setVersion);
  }, []);

  if (!version) return null;

  return (
    <div className="body-xs-regular text-theme-secondary">
      v{version}
    </div>
  );
}
