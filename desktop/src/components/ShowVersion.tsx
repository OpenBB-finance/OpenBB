import { useState, useEffect } from "react";
import { getVersion } from "@tauri-apps/api/app";

let cachedVersion: string | null = null;

const safeGetVersion = async (): Promise<string> => {
  if (cachedVersion !== null) return cachedVersion;
  try {
    cachedVersion = await getVersion();
    return cachedVersion;
  } catch (error) {
    console.error("Failed to get version:", error);
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