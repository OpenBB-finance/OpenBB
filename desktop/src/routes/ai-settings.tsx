import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { PanelCard } from "../components/quant/PanelCard";
import { getAiSettings, updateAiSettings } from "../lib/aiApi";
import type { AiGatewaySettings } from "../types/ai";

function AiSettingsPage() {
  const [settings, setSettings] = useState<AiGatewaySettings | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    void getAiSettings()
      .then((result) => {
        setSettings(result);
        setError(null);
      })
      .catch((reason) => {
        setError(reason instanceof Error ? reason.message : "Failed to load AI settings.");
      });
  }, []);

  if (!settings) {
    return (
      <div className="h-full min-h-0 overflow-auto py-4">
        <p className="body-sm-regular text-theme-muted">{error ?? "Loading AI settings..."}</p>
      </div>
    );
  }

  async function handleSave() {
    if (!settings) {
      return;
    }
    setIsSaving(true);
    try {
      const saved = await updateAiSettings(settings);
      setSettings(saved);
      setMessage("AI gateway settings saved.");
      setError(null);
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "Failed to save AI settings.");
    } finally {
      setIsSaving(false);
    }
  }

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4">
        <h1 className="body-lg-medium text-theme-primary">AI Settings</h1>
        <p className="body-sm-regular text-theme-muted">
          Configure the local AI gateway. Codex and Gemini credentials continue to come from their native CLIs.
        </p>
      </div>
      {error ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-3">
          <p className="body-xs-medium text-red-300">{error}</p>
        </div>
      ) : null}
      {message ? (
        <div className="mb-3 rounded-sm border border-emerald-500/60 bg-emerald-500/10 p-3">
          <p className="body-xs-medium text-emerald-300">{message}</p>
        </div>
      ) : null}
      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <PanelCard title="Defaults" description="These defaults drive the AI tab unless you override them per run.">
          <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Default Provider</span>
              <select
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                value={settings.defaultProvider}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, defaultProvider: event.target.value as AiGatewaySettings["defaultProvider"] } : previous)}
              >
                <option value="ollama">Ollama</option>
                <option value="codex">Codex</option>
                <option value="gemini">Gemini</option>
              </select>
            </label>
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Default Mode</span>
              <select
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                value={settings.defaultMode}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, defaultMode: event.target.value as AiGatewaySettings["defaultMode"] } : previous)}
              >
                <option value="ask">Ask</option>
                <option value="agent">Agent</option>
              </select>
            </label>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-3 md:grid-cols-2">
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Retrieval Strategy</span>
              <select
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                value={settings.retrieval.strategy}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, retrieval: { ...previous.retrieval, strategy: event.target.value as AiGatewaySettings["retrieval"]["strategy"] } } : previous)}
              >
                <option value="hybrid">Hybrid</option>
                <option value="semantic">Semantic</option>
                <option value="lexical">Lexical</option>
              </select>
            </label>
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Top K</span>
              <input
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                type="number"
                min={1}
                max={16}
                value={settings.retrieval.topK}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, retrieval: { ...previous.retrieval, topK: Number(event.target.value || 8) } } : previous)}
              />
            </label>
          </div>
        </PanelCard>

        <PanelCard title="Ollama" description="Generation and embedding models are configurable independently.">
          <div className="space-y-3">
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Base URL</span>
              <input
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                value={settings.providers.ollama.baseUrl}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, providers: { ...previous.providers, ollama: { ...previous.providers.ollama, baseUrl: event.target.value } } } : previous)}
              />
            </label>
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Default Chat Model</span>
              <input
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                value={settings.providers.ollama.defaultChatModel ?? ""}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, providers: { ...previous.providers, ollama: { ...previous.providers.ollama, defaultChatModel: event.target.value } } } : previous)}
              />
            </label>
            <label className="space-y-1">
              <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Default Embedding Model</span>
              <input
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                value={settings.providers.ollama.defaultEmbeddingModel ?? ""}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, providers: { ...previous.providers, ollama: { ...previous.providers.ollama, defaultEmbeddingModel: event.target.value } } } : previous)}
              />
            </label>
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <label className="space-y-1">
                <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Keep Alive</span>
                <input
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                  value={settings.providers.ollama.keepAlive}
                  onChange={(event) => setSettings((previous) => previous ? { ...previous, providers: { ...previous.providers, ollama: { ...previous.providers.ollama, keepAlive: event.target.value } } } : previous)}
                />
              </label>
              <label className="space-y-1">
                <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Request Timeout (ms)</span>
                <input
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                  type="number"
                  min={1000}
                  step={1000}
                  value={settings.providers.ollama.requestTimeoutMs}
                  onChange={(event) => setSettings((previous) => previous ? { ...previous, providers: { ...previous.providers, ollama: { ...previous.providers.ollama, requestTimeoutMs: Number(event.target.value || 45000) } } } : previous)}
                />
              </label>
            </div>
          </div>
        </PanelCard>

        <PanelCard title="Feature Flags" description="Agent mode stays behind explicit feature flags.">
          <div className="space-y-3">
            <label className="flex items-center gap-2 body-xs-regular text-theme-primary">
              <input
                type="checkbox"
                checked={settings.featureFlags.codexAgentEnabled}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, featureFlags: { ...previous.featureFlags, codexAgentEnabled: event.target.checked } } : previous)}
              />
              Enable Codex app-server agent mode
            </label>
            <label className="flex items-center gap-2 body-xs-regular text-theme-primary">
              <input
                type="checkbox"
                checked={settings.featureFlags.geminiAgentEnabled}
                onChange={(event) => setSettings((previous) => previous ? { ...previous, featureFlags: { ...previous.featureFlags, geminiAgentEnabled: event.target.checked } } : previous)}
              />
              Enable Gemini ACP agent mode
            </label>
          </div>
        </PanelCard>

        <PanelCard title="Provider Transports" description="Transport modes are determined by the gateway runtime and shown here for reference.">
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">Codex Ask</p>
              <p className="body-xs-medium text-theme-primary">{settings.providers.codex.askTransport}</p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">Codex Agent</p>
              <p className="body-xs-medium text-theme-primary">{settings.providers.codex.agentTransport}</p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">Gemini Ask</p>
              <p className="body-xs-medium text-theme-primary">{settings.providers.gemini.askTransport}</p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
              <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">Gemini Agent</p>
              <p className="body-xs-medium text-theme-primary">{settings.providers.gemini.agentTransport}</p>
            </div>
          </div>
        </PanelCard>
      </div>
      <div className="mt-4 flex justify-end">
        <button
          type="button"
          className="button-secondary rounded-sm px-4 py-2 body-xs-medium"
          disabled={isSaving}
          onClick={() => void handleSave()}
        >
          {isSaving ? "Saving..." : "Save AI Settings"}
        </button>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/ai-settings")({
  component: AiSettingsPage,
});
