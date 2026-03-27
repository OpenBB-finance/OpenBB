import { useEffect, useState } from "react";
import { invoke } from "@tauri-apps/api/core";
import { resolveOpenBBBackend } from "../lib/openbbBackend";
import { fetchMacroHealthWithActivation } from "../lib/macroApi";
import { probeQuantMlActivation } from "../lib/quantApi";

interface SystemReadinessBannerProps {
  hidden?: boolean;
}

function Pill({
  label,
  value,
  tone,
}: {
  label: string;
  value: string;
  tone: "ok" | "warn";
}) {
  const className =
    tone === "ok"
      ? "border-emerald-500/40 bg-emerald-500/10 text-emerald-200"
      : "border-amber-500/40 bg-amber-500/10 text-amber-200";
  return (
    <span className={`rounded-full border px-3 py-1 body-xxs-medium ${className}`}>
      {label}: {value}
    </span>
  );
}

export function SystemReadinessBanner({ hidden = false }: SystemReadinessBannerProps) {
  const [backendText, setBackendText] = useState("checking");
  const [backendTone, setBackendTone] = useState<"ok" | "warn">("warn");
  const [quantText, setQuantText] = useState("checking");
  const [quantTone, setQuantTone] = useState<"ok" | "warn">("warn");
  const [macroText, setMacroText] = useState("checking");
  const [macroTone, setMacroTone] = useState<"ok" | "warn">("warn");
  const [fredText, setFredText] = useState("checking");
  const [fredTone, setFredTone] = useState<"ok" | "warn">("warn");
  const [marketText, setMarketText] = useState("checking");
  const [marketTone, setMarketTone] = useState<"ok" | "warn">("warn");
  const [workingDirText, setWorkingDirText] = useState("checking");
  const [workingDirTone, setWorkingDirTone] = useState<"ok" | "warn">("warn");

  useEffect(() => {
    if (hidden) {
      return;
    }

    const load = async () => {
      try {
        const backend = await resolveOpenBBBackend();
        const primarySource = ["running-service-url", "command-parse", "stored-url"].includes(backend.source);
        setBackendText(`${backend.connected ? "connected" : "disconnected"} via ${backend.source}`);
        setBackendTone(backend.connected ? "ok" : "warn");
        setMarketText(primarySource ? "primary" : `fallback via ${backend.source}`);
        setMarketTone(primarySource ? "ok" : "warn");

        if (!backend.connected) {
          setQuantText("waiting for backend");
          setMacroText("waiting for backend");
          setFredText("waiting for backend");
          setWorkingDirText("waiting for desktop runtime");
          return;
        }

        const [quantActivation, macroHealth] = await Promise.all([
          probeQuantMlActivation(backend.baseUrl).catch(() => null),
          fetchMacroHealthWithActivation(backend.baseUrl).catch(() => null),
        ]);

        setQuantText(quantActivation?.available ? "ready" : (quantActivation?.detail || "unavailable"));
        setQuantTone(quantActivation?.available ? "ok" : "warn");

        setMacroText(macroHealth?.activation.available ? "ready" : (macroHealth?.activation.detail || "unavailable"));
        setMacroTone(macroHealth?.activation.available ? "ok" : "warn");

        const fredReady = Boolean(macroHealth?.data?.fred_api_key_configured);
        setFredText(fredReady ? "configured" : "fallback/cache");
        setFredTone(fredReady ? "ok" : "warn");

        try {
          const workingDir = await invoke<string>("get_working_directory", { defaultDir: "" });
          setWorkingDirText(workingDir || "not set");
          setWorkingDirTone(workingDir ? "ok" : "warn");
        } catch {
          setWorkingDirText("browser-only mode");
          setWorkingDirTone("warn");
        }
      } catch (error) {
        const message = error instanceof Error ? error.message : "unknown error";
        setBackendText(message);
        setBackendTone("warn");
        setQuantText("unresolved");
        setMacroText("unresolved");
        setFredText("unresolved");
        setMarketText("unresolved");
        setWorkingDirText("unresolved");
      }
    };

    void load();
  }, [hidden]);

  if (hidden) {
    return null;
  }

  return (
    <div className="mx-5 mt-3 rounded-md border border-theme-outline bg-theme-primary px-4 py-3">
      <div className="flex flex-wrap items-center gap-2">
        <span className="body-xs-medium text-theme-primary">System Readiness</span>
        <Pill label="Backend" value={backendText} tone={backendTone} />
        <Pill label="Quant ML" value={quantText} tone={quantTone} />
        <Pill label="Macro" value={macroText} tone={macroTone} />
        <Pill label="FRED" value={fredText} tone={fredTone} />
        <Pill label="Market Fallback" value={marketText} tone={marketTone} />
        <Pill label="Working Directory" value={workingDirText} tone={workingDirTone} />
      </div>
    </div>
  );
}
