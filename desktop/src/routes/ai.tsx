import { createFileRoute, Link } from "@tanstack/react-router";
import { useEffect, useMemo, useState } from "react";
import { PanelCard } from "../components/quant/PanelCard";
import {
  AI_MARKET_BACKEND_REQUIRED_MESSAGE,
  analyzeAiMarketPrompt,
  buildAiMarketContext,
} from "../lib/aiMarketContext";
import {
  buildAiIndex,
  cancelAiRun,
  clearAiIndex,
  createAiRun,
  getAiSession,
  getAiGatewayStatus,
  getAiSettings,
  listAiSessions,
  respondToAiApproval,
  streamAiRun,
} from "../lib/aiApi";
import { formatBackendDetail, resolveOpenBBBackend } from "../lib/openbbBackend";
import type {
  AiApprovalDecision,
  AiGatewaySettings,
  AiGatewayStatus,
  ApprovalPolicy,
  ProviderId,
  SandboxMode,
  SessionDetail,
  SessionSummary,
} from "../types/ai";
import type { BackendResolution } from "../types/quant";
import type { AiMarketSnapshot } from "../lib/aiMarketContext";

interface ThreadMessage {
  role: "user" | "assistant";
  content: string;
  citations?: Array<{ path: string; startLine: number; endLine: number; score: number }>;
  marketSnapshot?: AiMarketSnapshot | null;
  usedModel?: string;
  attemptedModels?: string[];
  timingMs?: number;
  retrievalMode?: string;
}

interface RunUsage {
  citations?: ThreadMessage["citations"];
  usedModel?: string;
  attemptedModels?: string[];
  timingMs?: number;
  retrievalMode?: string;
}

interface PendingApprovalState {
  approvalId: string;
  kind: string;
  payload: unknown;
  summary: string;
}

function StatusBadge({ label, tone }: { label: string; tone: "ok" | "warn" | "muted" }) {
  const className =
    tone === "ok"
      ? "border-emerald-500/60 bg-emerald-500/10 text-emerald-300"
      : tone === "warn"
        ? "border-amber-500/60 bg-amber-500/10 text-amber-300"
        : "border-theme-outline bg-theme-secondary text-theme-muted";
  return <span className={`rounded-sm border px-2 py-1 body-xxs-medium ${className}`}>{label}</span>;
}

function ValueRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-sm bg-theme-secondary px-3 py-2">
      <p className="body-xxs-regular text-theme-muted">{label}</p>
      <p className="body-xs-medium break-all text-theme-primary">{value}</p>
    </div>
  );
}

function formatDurationLabel(value: number | null | undefined): string | null {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return null;
  }
  if (value < 1000) {
    return `${value} ms`;
  }
  return `${(value / 1000).toFixed(1)} s`;
}

function formatTimestamp(value: string | null | undefined): string {
  if (!value) {
    return "Unavailable";
  }
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? value : parsed.toLocaleString();
}

function MarketSnapshotCard({ snapshot }: { snapshot: AiMarketSnapshot }) {
  return (
    <div className="rounded-sm border border-emerald-500/40 bg-emerald-500/5 p-3" data-testid="ai-market-snapshot">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="body-xxs-medium uppercase tracking-wide text-emerald-300">OpenBB Data Used</p>
          <p className="body-sm-medium text-theme-primary">
            {snapshot.symbol}
            {snapshot.resolvedName ? ` | ${snapshot.resolvedName}` : ""}
          </p>
        </div>
        <div className="text-right">
          <p className="body-xxs-regular text-theme-muted">Current</p>
          <p className="body-xs-medium text-theme-primary">{snapshot.currentPrice}</p>
        </div>
      </div>
      <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-3">
        <ValueRow label="Session Change" value={snapshot.sessionChange} />
        <ValueRow label="Target Range" value={snapshot.targetRange} />
        <ValueRow label="Analysts" value={`${snapshot.analysts} | ${snapshot.recommendation}`} />
      </div>
      {(snapshot.providerSummary || snapshot.asOf) ? (
        <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
          {snapshot.providerSummary ? <ValueRow label="Provider" value={snapshot.providerSummary} /> : null}
          {snapshot.asOf ? <ValueRow label="As Of" value={formatTimestamp(snapshot.asOf)} /> : null}
        </div>
      ) : null}
    </div>
  );
}

function AssistantMeta({ message }: { message: ThreadMessage }) {
  if (message.role !== "assistant") {
    return null;
  }
  const parts = [
    message.usedModel ? `Model ${message.usedModel}` : null,
    formatDurationLabel(message.timingMs),
    message.retrievalMode ?? null,
  ].filter(Boolean);
  if (!parts.length && !(message.attemptedModels && message.attemptedModels.length > 1)) {
    return null;
  }
  return (
    <div className="mt-2 space-y-1">
      {parts.length > 0 ? <p className="body-xxs-regular text-theme-muted">{parts.join(" | ")}</p> : null}
      {message.attemptedModels && message.attemptedModels.length > 1 ? (
        <p className="body-xxs-regular text-theme-muted">Fallback chain: {message.attemptedModels.join(" -> ")}</p>
      ) : null}
    </div>
  );
}

function providerLabel(provider: ProviderId): string {
  if (provider === "ollama") {
    return "Ollama";
  }
  if (provider === "codex") {
    return "Codex";
  }
  return "Gemini";
}

function resolveExecutionSettings(
  settings: AiGatewaySettings,
  provider: ProviderId,
  mode: "ask" | "agent",
): { sandbox: SandboxMode; approvalPolicy: ApprovalPolicy } {
  if (mode !== "agent" || provider === "ollama") {
    return {
      sandbox: "read-only",
      approvalPolicy: "default",
    };
  }

  const providerSettings = provider === "codex"
    ? settings.providers.codex
    : settings.providers.gemini;

  return {
    sandbox: providerSettings.sandbox,
    approvalPolicy: providerSettings.approvalPolicy,
  };
}

function summarizeApproval(kind: string, payload: unknown): string {
  if (!payload || typeof payload !== "object") {
    return `${kind} approval requested`;
  }
  const record = payload as Record<string, unknown>;
  if (typeof record.reason === "string" && record.reason.trim()) {
    return record.reason;
  }
  const toolCall = record.toolCall;
  if (toolCall && typeof toolCall === "object") {
    const title = (toolCall as Record<string, unknown>).title;
    if (typeof title === "string" && title.trim()) {
      return title;
    }
  }
  return `${kind} approval requested`;
}

function providerTransportLabel(providerStatus: AiGatewayStatus["providers"][number] | null): string {
  if (!providerStatus) {
    return "Unavailable";
  }
  return providerStatus.mode ?? "Unavailable";
}

function collectLatestDiffFiles(detail: SessionDetail | null): Array<{ path: string; diff: string }> {
  if (!detail) {
    return [];
  }
  for (let index = detail.recentEvents.length - 1; index >= 0; index -= 1) {
    const event = detail.recentEvents[index];
    if (event.type === "diffPreview") {
      return event.files;
    }
  }
  return [];
}

function AiPage() {
  const [gatewayStatus, setGatewayStatus] = useState<AiGatewayStatus | null>(null);
  const [settings, setSettings] = useState<AiGatewaySettings | null>(null);
  const [backendResolution, setBackendResolution] = useState<BackendResolution | null>(null);
  const [selectedProvider, setSelectedProvider] = useState<ProviderId | null>(null);
  const [selectedMode, setSelectedMode] = useState<"ask" | "agent" | null>(null);
  const [thread, setThread] = useState<ThreadMessage[]>([]);
  const [activity, setActivity] = useState<string[]>([]);
  const [prompt, setPrompt] = useState("");
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [latestMarketSnapshot, setLatestMarketSnapshot] = useState<AiMarketSnapshot | null>(null);
  const [sessions, setSessions] = useState<SessionSummary[]>([]);
  const [selectedSessionId, setSelectedSessionId] = useState<string | null>(null);
  const [selectedSession, setSelectedSession] = useState<SessionDetail | null>(null);
  const [pendingApproval, setPendingApproval] = useState<PendingApprovalState | null>(null);
  const [liveDiffFiles, setLiveDiffFiles] = useState<Array<{ path: string; diff: string }>>([]);
  const [selectedDiffPath, setSelectedDiffPath] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isRunning, setIsRunning] = useState(false);
  const [activeRunId, setActiveRunId] = useState<string | null>(null);

  const marketPromptInfo = analyzeAiMarketPrompt(prompt);
  const activeProvider = selectedProvider ?? settings?.defaultProvider ?? "ollama";
  const activeMode = selectedMode ?? settings?.defaultMode ?? "ask";
  const currentProviderStatus = useMemo(
    () => gatewayStatus?.providers.find((provider) => provider.provider === activeProvider) ?? null,
    [activeProvider, gatewayStatus],
  );
  const canUseAgent = Boolean(
    activeProvider !== "ollama"
    && currentProviderStatus?.installed
    && currentProviderStatus?.authenticated
    && currentProviderStatus?.capabilities.resumeSession
    && currentProviderStatus?.capabilities.approvals,
  );
  const sessionDiffFiles = useMemo(() => collectLatestDiffFiles(selectedSession), [selectedSession]);
  const visibleDiffFiles = liveDiffFiles.length > 0 ? liveDiffFiles : sessionDiffFiles;
  const selectedDiff = visibleDiffFiles.find((file) => file.path === selectedDiffPath) ?? visibleDiffFiles[0] ?? null;

  useEffect(() => {
    if (activeMode === "agent" && !canUseAgent) {
      setSelectedMode("ask");
    }
  }, [activeMode, canUseAgent]);

  useEffect(() => {
    if (visibleDiffFiles.length === 0) {
      setSelectedDiffPath(null);
      return;
    }
    if (!selectedDiffPath || !visibleDiffFiles.some((file) => file.path === selectedDiffPath)) {
      setSelectedDiffPath(visibleDiffFiles[0]?.path ?? null);
    }
  }, [selectedDiffPath, visibleDiffFiles]);

  async function refreshStatus() {
    setIsLoading(true);
    try {
      const [nextStatus, nextSettings, nextBackend, nextSessions] = await Promise.all([
        getAiGatewayStatus("."),
        getAiSettings(),
        resolveOpenBBBackend().catch(() => null),
        listAiSessions().catch(() => [] as SessionSummary[]),
      ]);
      setGatewayStatus(nextStatus);
      setSettings(nextSettings);
      setBackendResolution(nextBackend);
      setSessions(nextSessions);
      setSelectedSessionId((previous) => previous ?? nextSessions[0]?.sessionId ?? null);
      setSelectedProvider((previous) => previous ?? nextSettings.defaultProvider);
      setSelectedMode((previous) => previous ?? nextSettings.defaultMode);
      setErrorMessage(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to load AI gateway status.");
    } finally {
      setIsLoading(false);
    }
  }

  useEffect(() => {
    void refreshStatus();
  }, []);

  useEffect(() => {
    if (!selectedSessionId) {
      setSelectedSession(null);
      return;
    }
    void getAiSession(selectedSessionId)
      .then((detail) => {
        setSelectedSession(detail);
        setSelectedDiffPath((previous) => previous ?? collectLatestDiffFiles(detail)[0]?.path ?? null);
      })
      .catch(() => {
        setSelectedSession(null);
      });
  }, [selectedSessionId]);

  const indexReady = Boolean(gatewayStatus?.index.ready);
  const workspacePath = gatewayStatus?.workspacePath ?? ".";
  const canAskFromMarketData = marketPromptInfo.isFinanceQuestion;
  const askEnabled = Boolean(prompt.trim()) && !isRunning && (indexReady || canAskFromMarketData);
  const marketDataBadge = backendResolution
    ? backendResolution.connected
      ? { label: "Live Market Data Ready", tone: "ok" as const }
      : { label: "Market Data Offline", tone: "warn" as const }
    : null;

  async function handleBuildIndex(force: boolean) {
    setIsIndexing(true);
    setActionMessage(null);
    try {
      const result = await buildAiIndex(workspacePath, force);
      setActionMessage(
        `Indexed ${result.indexedFiles}/${result.scannedFiles} files into ${result.chunkCount} chunks.`,
      );
      await refreshStatus();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to build the AI index.");
    } finally {
      setIsIndexing(false);
    }
  }

  async function handleClearIndex() {
    setIsClearing(true);
    setActionMessage(null);
    try {
      await clearAiIndex(workspacePath);
      setThread([]);
      setLatestMarketSnapshot(null);
      setActivity([]);
      setActionMessage("AI index cleared.");
      await refreshStatus();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to clear the AI index.");
    } finally {
      setIsClearing(false);
    }
  }

  async function handleAsk() {
    const normalizedPrompt = prompt.trim();
    if (!normalizedPrompt || !settings) {
      return;
    }

    let marketContext = null;
    let marketFallbackMessage: string | null = null;
    if (marketPromptInfo.isFinanceQuestion) {
      try {
        marketContext = await buildAiMarketContext(normalizedPrompt);
      } catch (error) {
        const detail = error instanceof Error
          ? error.message
          : "Failed to load OpenBB market data for this question.";
        if (!indexReady) {
          setErrorMessage(
            detail === AI_MARKET_BACKEND_REQUIRED_MESSAGE
              ? "Connect an OpenBB backend for live market-data answers, or build the AI index to fall back to repository guidance."
              : detail,
          );
          return;
        }
        marketFallbackMessage = detail === AI_MARKET_BACKEND_REQUIRED_MESSAGE
          ? "OpenBB market data is unavailable. Answering from the repository index instead."
          : `OpenBB market data is unavailable. ${detail}`;
      }
    }

    const userMessage: ThreadMessage = { role: "user", content: normalizedPrompt };
    setThread((previous) => [...previous, userMessage]);
    setPrompt("");
    setActivity([]);
    setLiveDiffFiles([]);
    setPendingApproval(null);
    setIsRunning(true);
    setErrorMessage(null);
    setActionMessage(marketContext?.actionLabel ?? marketFallbackMessage);

    try {
      const execution = resolveExecutionSettings(settings, activeProvider, activeMode);
      const created = await createAiRun({
        provider: activeProvider,
        mode: activeMode,
        workspacePath,
        prompt: normalizedPrompt,
        supplementalContext: marketContext?.supplementalContext,
        retrieval: {
          enabled: !marketContext,
          topK: settings.retrieval.topK,
          strategy: settings.retrieval.strategy,
        },
        execution,
      });
      setActiveRunId(created.runId);
      if (created.sessionId) {
        setSelectedSessionId(created.sessionId);
      }

      let assistantText = "";
      let latestUsage: RunUsage | null = null;
      await streamAiRun(created.runId, (event) => {
        switch (event.type) {
          case "status":
            setActivity((previous) => [...previous, `Status: ${event.phase}`]);
            break;
          case "toolStarted":
            setActivity((previous) => [...previous, `Tool: ${event.name}`]);
            break;
          case "toolOutput":
            setActivity((previous) => [...previous, `${event.name}: ${event.text}`]);
            break;
          case "approvalRequest":
            setPendingApproval({
              approvalId: event.approvalId,
              kind: event.kind,
              payload: event.payload,
              summary: summarizeApproval(event.kind, event.payload),
            });
            setActivity((previous) => [...previous, `Approval required: ${summarizeApproval(event.kind, event.payload)}`]);
            break;
          case "diffPreview":
            setLiveDiffFiles(event.files);
            setSelectedDiffPath(event.files[0]?.path ?? null);
            setActivity((previous) => [...previous, `Diff updated: ${event.files.length} file(s)`]);
            break;
          case "messageDelta":
            assistantText += event.text;
            break;
          case "messageFinal":
            assistantText = event.text;
            break;
          case "done":
            latestUsage = (event.usage as RunUsage | null | undefined) ?? null;
            break;
          case "error":
            throw new Error(event.message);
          default:
            break;
        }
      });

      const usage: RunUsage = latestUsage ?? {};
      const assistantMessage: ThreadMessage = {
        role: "assistant",
        content: assistantText,
        citations: usage.citations ?? [],
        marketSnapshot: marketContext?.snapshot ?? null,
        usedModel: usage.usedModel ?? currentProviderStatus?.defaultModel ?? providerLabel(activeProvider),
        attemptedModels: usage.attemptedModels,
        timingMs: usage.timingMs,
        retrievalMode: usage.retrievalMode,
      };
      setThread((previous) => [...previous, assistantMessage]);
      setLatestMarketSnapshot(marketContext?.snapshot ?? null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to run the AI request.");
    } finally {
      setIsRunning(false);
      setActiveRunId(null);
      await refreshStatus();
    }
  }

  async function handleCancel() {
    if (!activeRunId) {
      return;
    }
    await cancelAiRun(activeRunId);
    setIsRunning(false);
    setActiveRunId(null);
    setPendingApproval(null);
    await refreshStatus();
  }

  async function handleApproval(decision: AiApprovalDecision) {
    if (!pendingApproval) {
      return;
    }
    try {
      await respondToAiApproval(pendingApproval.approvalId, decision);
      setActionMessage(`Approval ${decision.decision} sent.`);
      setPendingApproval(null);
      await refreshStatus();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to respond to the approval request.");
    }
  }

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">AI</h1>
          <p className="body-sm-regular text-theme-muted">
            Gateway-based repository and market assistant with Ollama, Codex, and Gemini providers.
          </p>
        </div>
        <div className="flex flex-wrap gap-2">
          {marketDataBadge ? <StatusBadge label={marketDataBadge.label} tone={marketDataBadge.tone} /> : null}
          <StatusBadge label={`Index ${indexReady ? "Ready" : "Missing"}`} tone={indexReady ? "ok" : "warn"} />
          <StatusBadge label={`Provider ${providerLabel(activeProvider)}`} tone="muted" />
        </div>
      </div>

      {errorMessage ? (
        <div className="mb-3 rounded-sm border border-red-500/60 bg-red-500/10 p-3">
          <p className="body-xs-medium text-red-300">{errorMessage}</p>
        </div>
      ) : null}
      {actionMessage ? (
        <div className="mb-3 rounded-sm border border-sky-500/60 bg-sky-500/10 p-3">
          <p className="body-xs-medium text-sky-300">{actionMessage}</p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-[1.4fr_0.6fr]">
        <div className="space-y-4">
          <PanelCard
            title="AI Gateway"
            description="Choose the provider and interaction mode. Agent mode remains gated behind provider capability flags."
          >
            <div className="grid grid-cols-1 gap-3 md:grid-cols-2">
              <label className="space-y-1">
                <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Provider</span>
                <select
                  aria-label="Provider"
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                  value={activeProvider}
                  onChange={(event) => setSelectedProvider(event.target.value as ProviderId)}
                >
                  {(["ollama", "codex", "gemini"] as ProviderId[]).map((provider) => {
                    const providerStatus = gatewayStatus?.providers.find((item) => item.provider === provider);
                    return (
                      <option key={provider} value={provider} disabled={!providerStatus?.installed}>
                        {providerLabel(provider)}
                      </option>
                    );
                  })}
                </select>
              </label>
              <label className="space-y-1">
                <span className="body-xxs-medium uppercase tracking-wide text-theme-muted">Mode</span>
                <select
                  aria-label="Mode"
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
                  value={activeMode}
                  onChange={(event) => setSelectedMode(event.target.value as "ask" | "agent")}
                >
                  <option value="ask">Ask</option>
                  <option value="agent" disabled={!canUseAgent}>
                    Agent
                  </option>
                </select>
              </label>
            </div>
            {activeMode === "agent" ? (
              <p className="mt-3 body-xxs-regular text-theme-muted">
                Agent mode uses the provider transport if the feature flag and transport are available. Unsupported providers stay in ask mode.
              </p>
            ) : null}
          </PanelCard>

          <PanelCard
            title="Prompt"
            description="Finance prompts can use live OpenBB market data even when the repository index is missing."
          >
            <label htmlFor="ai-question" className="mb-2 block body-xs-medium text-theme-primary">
              Question
            </label>
            <textarea
              id="ai-question"
              className="min-h-28 w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xs-regular text-theme-primary"
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              placeholder="Explain backend resolution, or ask: IBM financial statements and estimate a price range."
              disabled={isRunning}
            />
            <p className="mt-3 body-xxs-regular text-theme-muted">
              {marketPromptInfo.isFinanceQuestion
                ? "Finance prompts use OpenBB market data first when the backend is connected."
                : "Repository questions use the shared gateway index and provider adapters."}
            </p>
            <div className="mt-3 flex flex-wrap justify-end gap-2">
              {isRunning ? (
                <button
                  type="button"
                  className="button-secondary rounded-sm px-4 py-2 body-xs-medium"
                  onClick={() => void handleCancel()}
                >
                  Cancel
                </button>
              ) : null}
              <button
                type="button"
                className="button-secondary rounded-sm px-4 py-2 body-xs-medium"
                onClick={() => void handleAsk()}
                disabled={!askEnabled}
              >
                {isRunning ? "Running..." : activeMode === "agent" ? "Run Agent" : "Ask AI"}
              </button>
            </div>
          </PanelCard>

          <PanelCard title="Conversation" description="Gateway events stream back into the same thread.">
            <div className="space-y-3">
              {thread.length === 0 ? (
                <p className="body-xs-regular text-theme-muted">
                  Start with repository questions after indexing, or ask a market-data question with a ticker or company name.
                </p>
              ) : (
                thread.map((message, index) => (
                  <div
                    key={`${message.role}-${index}`}
                    className={`rounded-sm border px-3 py-2 ${
                      message.role === "assistant"
                        ? "border-sky-500/30 bg-sky-500/5"
                        : "border-theme-outline bg-theme-secondary"
                    }`}
                  >
                    <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">{message.role}</p>
                    <div className="mt-1 whitespace-pre-wrap body-xs-regular text-theme-primary">{message.content}</div>
                    {message.marketSnapshot ? <div className="mt-3"><MarketSnapshotCard snapshot={message.marketSnapshot} /></div> : null}
                    <AssistantMeta message={message} />
                  </div>
                ))
              )}
            </div>
          </PanelCard>
        </div>

        <div className="space-y-4">
          <PanelCard title="Status" description="Provider, index, and backend state come from the local AI gateway.">
            <div className="grid grid-cols-1 gap-2">
              <ValueRow label="Gateway Version" value={gatewayStatus?.gatewayVersion ?? (isLoading ? "Loading..." : "Unavailable")} />
              <ValueRow label="Workspace" value={gatewayStatus?.workspacePath ?? "Unavailable"} />
              <ValueRow label="Index State" value={gatewayStatus?.index.ready ? "Ready" : "Missing"} />
              <ValueRow label="Provider Ready" value={currentProviderStatus ? `${currentProviderStatus.installed ? "Installed" : "Missing"} | ${currentProviderStatus.authenticated ? "Authenticated" : "Auth needed"}` : "Unavailable"} />
              <ValueRow label="Default Model" value={currentProviderStatus?.defaultModel ?? "Not detected"} />
              <ValueRow label="OpenBB Backend" value={backendResolution ? (backendResolution.connected ? "Connected" : "Offline") : "Resolving..."} />
              <ValueRow label="OpenBB URL" value={backendResolution?.baseUrl ?? "Unavailable"} />
            </div>
            <div className="mt-3 grid grid-cols-1 gap-2">
              <ValueRow label="Installed" value={currentProviderStatus ? (currentProviderStatus.installed ? "Yes" : "No") : "Unavailable"} />
              <ValueRow label="Reachable" value={currentProviderStatus ? (currentProviderStatus.reachable ? "Yes" : "No") : "Unavailable"} />
              <ValueRow label="Authenticated" value={currentProviderStatus ? (currentProviderStatus.authenticated ? "Yes" : "No") : "Unavailable"} />
              <ValueRow label="Transport" value={providerTransportLabel(currentProviderStatus)} />
              <ValueRow label="Version" value={currentProviderStatus?.version ?? "Unavailable"} />
              <ValueRow
                label="Provider Error"
                value={currentProviderStatus?.error ? `${currentProviderStatus.error.code} | ${currentProviderStatus.error.message}` : "None"}
              />
            </div>
            {backendResolution ? (
              <p className="mt-3 body-xxs-regular text-theme-muted">
                OpenBB status: {formatBackendDetail(backendResolution.detail, backendResolution.connected)}
              </p>
            ) : null}
          </PanelCard>

          <PanelCard title="Index Controls" description="The gateway stores repository indexes under ~/.openbb_platform/ai_gateway/index.">
            <div className="grid grid-cols-1 gap-2">
              <ValueRow label="Chunks" value={String(gatewayStatus?.index.chunkCount ?? 0)} />
              <ValueRow label="Last Indexed" value={formatTimestamp(gatewayStatus?.index.lastIndexedAt)} />
              <ValueRow label="Retrieval" value={gatewayStatus?.index.mode ?? "lexical"} />
            </div>
            <div className="mt-3 flex flex-wrap gap-2">
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleBuildIndex(false)} disabled={isIndexing}>
                {isIndexing ? "Indexing..." : "Index Now"}
              </button>
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleBuildIndex(true)} disabled={isIndexing}>
                Rebuild
              </button>
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleClearIndex()} disabled={isClearing}>
                {isClearing ? "Clearing..." : "Clear"}
              </button>
            </div>
          </PanelCard>

          <PanelCard title="Activity" description="Provider tool and status events are normalized by the gateway.">
            {activity.length === 0 ? (
              <p className="body-xs-regular text-theme-muted">Provider activity will appear here while a run is in progress.</p>
            ) : (
              <div className="space-y-2">
                {activity.slice(-8).map((entry, index) => (
                  <div key={`${entry}-${index}`} className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                    <p className="body-xxs-regular text-theme-primary">{entry}</p>
                  </div>
                ))}
              </div>
            )}
          </PanelCard>

          <PanelCard title="Agent Sessions" description="Gateway sessions remain available for inspection while the app stays open.">
            {sessions.length === 0 ? (
              <p className="body-xs-regular text-theme-muted">No sessions yet. Run Ask or Agent mode to populate this list.</p>
            ) : (
              <div className="space-y-2">
                {sessions.map((session) => (
                  <button
                    key={session.sessionId}
                    type="button"
                    className={`w-full rounded-sm border px-3 py-2 text-left ${
                      selectedSessionId === session.sessionId
                        ? "border-sky-500/60 bg-sky-500/10"
                        : "border-theme-outline bg-theme-secondary"
                    }`}
                    onClick={() => setSelectedSessionId(session.sessionId)}
                  >
                    <p className="body-xs-medium text-theme-primary">{session.title}</p>
                    <p className="body-xxs-regular text-theme-muted">
                      {providerLabel(session.provider)} | {session.mode} | {session.status} | {formatTimestamp(session.updatedAt)}
                    </p>
                  </button>
                ))}
              </div>
            )}
            {selectedSession ? (
              <div className="mt-3 rounded-sm border border-theme-outline bg-theme-secondary p-3">
                <p className="body-xs-medium text-theme-primary">{selectedSession.summary.title}</p>
                <p className="body-xxs-regular text-theme-muted">
                  Latest run {selectedSession.summary.latestRunId} | {selectedSession.pendingApprovals.length} pending approval(s)
                </p>
                {selectedSession.pendingApprovals.length > 0 ? (
                  <div className="mt-2 space-y-2">
                    {selectedSession.pendingApprovals.map((approval) => (
                      <div key={approval.approvalId} className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-3 py-2">
                        <p className="body-xxs-medium text-amber-300">{approval.kind}</p>
                        <p className="body-xxs-regular text-theme-primary">{approval.summary}</p>
                      </div>
                    ))}
                  </div>
                ) : null}
              </div>
            ) : null}
          </PanelCard>

          <PanelCard title="Diff Preview" description="Latest file-change diff from the current or selected agent session.">
            {visibleDiffFiles.length === 0 ? (
              <p className="body-xs-regular text-theme-muted">No diff preview has been emitted yet.</p>
            ) : (
              <div className="space-y-3">
                <div className="flex flex-wrap gap-2">
                  {visibleDiffFiles.map((file) => (
                    <button
                      key={file.path}
                      type="button"
                      className={`rounded-sm border px-2 py-1 body-xxs-medium ${
                        selectedDiff?.path === file.path
                          ? "border-sky-500/60 bg-sky-500/10 text-sky-300"
                          : "border-theme-outline bg-theme-secondary text-theme-primary"
                      }`}
                      onClick={() => setSelectedDiffPath(file.path)}
                    >
                      {file.path}
                    </button>
                  ))}
                </div>
                <pre className="max-h-80 overflow-auto rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xxs-regular text-theme-primary">
                  {selectedDiff?.diff ?? ""}
                </pre>
              </div>
            )}
          </PanelCard>

          {latestMarketSnapshot ? (
            <PanelCard title="OpenBB Data" description="Latest market snapshot supplied to the AI run.">
              <MarketSnapshotCard snapshot={latestMarketSnapshot} />
            </PanelCard>
          ) : null}

          <PanelCard title="Provider Settings" description="Use the dedicated settings route to change defaults and transports.">
            <Link to="/ai-settings" className="body-sm-medium text-theme-accent">
              Open AI Settings
            </Link>
          </PanelCard>
        </div>
      </div>

      {pendingApproval ? (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/60 px-4">
          <div className="w-full max-w-2xl rounded-sm border border-theme-outline bg-theme-panel p-4 shadow-2xl">
            <div>
              <p className="body-xxs-medium uppercase tracking-wide text-amber-300">Approval Required</p>
              <h2 className="body-md-medium text-theme-primary">{pendingApproval.summary}</h2>
              <p className="mt-1 body-xs-regular text-theme-muted">
                {pendingApproval.kind} approval requested by the provider runtime.
              </p>
            </div>
            <pre className="mt-3 max-h-64 overflow-auto rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-xxs-regular text-theme-primary">
              {JSON.stringify(pendingApproval.payload, null, 2)}
            </pre>
            <div className="mt-4 flex flex-wrap justify-end gap-2">
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleApproval({ decision: "decline", scope: "once" })}>
                Decline
              </button>
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleApproval({ decision: "accept", scope: "once" })}>
                Accept Once
              </button>
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleApproval({ decision: "acceptForSession", scope: "session" })}>
                Accept For Session
              </button>
              <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={() => void handleApproval({ decision: "cancel", scope: "once" })}>
                Cancel Run
              </button>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export const Route = createFileRoute("/ai")({
  component: AiPage,
});
