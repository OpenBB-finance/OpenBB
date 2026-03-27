import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useRef, useState } from "react";
import {
  askAiQuestion,
  buildAiIndex,
  clearAiIndex,
  getAiStatus,
  warmAiChatModel,
} from "../lib/aiApi";
import {
  AI_MARKET_BACKEND_REQUIRED_MESSAGE,
  analyzeAiMarketPrompt,
  buildAiMarketContext,
} from "../lib/aiMarketContext";
import { formatBackendDetail, resolveOpenBBBackend } from "../lib/openbbBackend";
import type { AiAskResponse, AiCitation, AiChatRole, AiStatus } from "../types/ai";
import type { BackendResolution } from "../types/quant";
import type { AiMarketSnapshot } from "../lib/aiMarketContext";

interface ThreadMessage {
  role: AiChatRole;
  content: string;
  citations?: AiCitation[];
  marketSnapshot?: AiMarketSnapshot;
  usedModel?: string;
  attemptedModels?: string[];
  modelTotalMs?: number | null;
  loadMs?: number | null;
  promptEvalMs?: number | null;
  evalMs?: number | null;
  timingMs?: number;
  retrievalMode?: AiAskResponse["retrievalMode"];
}

interface PersistedThreadState {
  indexSignature: string;
  messages: ThreadMessage[];
}

type WarmState = "idle" | "warming" | "ready" | "failed";

const AI_CHAT_MODEL_KEY = "ai.chatModel";
const AI_EMBEDDING_MODEL_KEY = "ai.embeddingModel";
const DEFAULT_ASK_CONTEXT_CHUNKS = 6;

function hashRepoRoot(input: string): string {
  let hash = 5381;
  for (let index = 0; index < input.length; index += 1) {
    hash = ((hash << 5) + hash) ^ input.charCodeAt(index);
  }
  return (hash >>> 0).toString(16);
}

function getThreadStorageKey(repoRoot: string | null): string | null {
  if (!repoRoot) {
    return null;
  }
  return `ai.thread.${hashRepoRoot(repoRoot)}`;
}

function getIndexSignature(status: AiStatus | null): string | null {
  if (!status?.repoRoot || !status.indexReady || !status.lastIndexedAt) {
    return null;
  }

  return [
    hashRepoRoot(status.repoRoot),
    status.lastIndexedAt,
    String(status.chunkCount),
    status.mode,
  ].join(":");
}

function parsePersistedThread(stored: string, expectedSignature: string): ThreadMessage[] {
  const parsed = JSON.parse(stored) as PersistedThreadState | ThreadMessage[];

  if (Array.isArray(parsed)) {
    return [];
  }

  if (
    !parsed
    || typeof parsed !== "object"
    || parsed.indexSignature !== expectedSignature
    || !Array.isArray(parsed.messages)
  ) {
    return [];
  }

  return parsed.messages;
}

function formatTimestamp(timestamp: string | null): string {
  if (!timestamp) {
    return "Not indexed yet";
  }
  const parsed = new Date(timestamp);
  return Number.isNaN(parsed.getTime()) ? timestamp : parsed.toLocaleString();
}

function formatMarketTimestamp(timestamp: string | null | undefined): string {
  if (!timestamp) {
    return "Unavailable";
  }
  const parsed = new Date(timestamp);
  return Number.isNaN(parsed.getTime()) ? timestamp : parsed.toLocaleString();
}

function formatDurationLabel(value: number | null | undefined): string | null {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return null;
  }
  if (value < 1000) {
    return `${value} ms`;
  }
  if (value < 10_000) {
    return `${(value / 1000).toFixed(1)} s`;
  }
  return `${Math.round(value / 1000)} s`;
}

function getWarmStateLabel(warmState: WarmState, warmMessage: string | null): string {
  if (warmMessage) {
    return warmMessage;
  }
  switch (warmState) {
    case "warming":
      return "Priming local chat model";
    case "ready":
      return "Warm cache ready";
    case "failed":
      return "Warm-up unavailable";
    default:
      return "Idle";
  }
}

function getAskPhase(elapsedMs: number): string {
  if (elapsedMs < 900) {
    return "Ranking repository context...";
  }
  if (elapsedMs < 7_000) {
    return "Loading local model...";
  }
  return "Generating answer...";
}

function copyCitationToClipboard(citation: AiCitation) {
  if (!navigator?.clipboard?.writeText) {
    return;
  }
  void navigator.clipboard.writeText(`${citation.path}:${citation.startLine}-${citation.endLine}`);
}

function StatusRow({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-sm bg-theme-secondary px-3 py-2">
      <p className="body-xxs-regular text-theme-muted">{label}</p>
      <p className="body-xs-medium break-all text-theme-primary">{value}</p>
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
    message.modelTotalMs ? `ollama ${formatDurationLabel(message.modelTotalMs)}` : null,
    message.loadMs ? `load ${formatDurationLabel(message.loadMs)}` : null,
    message.retrievalMode ?? null,
  ].filter(Boolean);

  if (parts.length === 0 && !(message.attemptedModels && message.attemptedModels.length > 1)) {
    return null;
  }

  return (
    <div className="mt-2 space-y-1">
      {parts.length > 0 ? (
        <p className="body-xxs-regular text-theme-muted">{parts.join(" | ")}</p>
      ) : null}
      {message.attemptedModels && message.attemptedModels.length > 1 ? (
        <p className="body-xxs-regular text-theme-muted">
          Fallback chain: {message.attemptedModels.join(" -> ")}
        </p>
      ) : null}
    </div>
  );
}

function MarketSnapshotCard({ snapshot }: { snapshot: AiMarketSnapshot }) {
  return (
    <div className="mt-3 rounded-sm border border-emerald-500/30 bg-emerald-500/5 p-3" data-testid="ai-market-snapshot">
      <div className="flex items-start justify-between gap-3">
        <div>
          <p className="body-xxs-medium uppercase tracking-wide text-emerald-300">OpenBB Data Used</p>
          <p className="body-sm-medium text-theme-primary">
            {snapshot.symbol}
            {snapshot.resolvedName ? ` · ${snapshot.resolvedName}` : ""}
          </p>
        </div>
        <div className="text-right">
          <p className="body-xxs-regular text-theme-muted">Current</p>
          <p className="body-xs-medium text-theme-primary">{snapshot.currentPrice}</p>
        </div>
      </div>

      <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-3">
        <StatusRow label="Session Change" value={snapshot.sessionChange} />
        <StatusRow label="Target Range" value={snapshot.targetRange} />
        <StatusRow label="Analysts" value={`${snapshot.analysts} | ${snapshot.recommendation}`} />
      </div>
      {snapshot.providerSummary || snapshot.asOf ? (
        <div className="mt-2 grid grid-cols-1 gap-2 md:grid-cols-2">
          {snapshot.providerSummary ? (
            <StatusRow label="Provider" value={snapshot.providerSummary} />
          ) : null}
          {snapshot.asOf ? (
            <StatusRow label="As Of" value={formatMarketTimestamp(snapshot.asOf)} />
          ) : null}
        </div>
      ) : null}

      {snapshot.sections.length > 0 ? (
        <div className="mt-3 space-y-3">
          {snapshot.sections.map((section) => (
            <div key={section.title} className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">{section.title}</p>
              <div className="mt-2 space-y-2">
                {section.metrics.map((metric) => (
                  <div key={`${section.title}-${metric.label}`} className="grid grid-cols-[minmax(0,1fr)_auto] gap-2">
                    <div>
                      <p className="body-xs-medium text-theme-primary">{metric.label}</p>
                      <p className="body-xxs-regular text-theme-muted">
                        Latest {metric.latest} | Prior {metric.prior}
                      </p>
                    </div>
                    <p className="body-xxs-regular text-theme-muted text-right">
                      {metric.trend ?? "Trend unavailable"}
                    </p>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      ) : null}
    </div>
  );
}

function AiPage() {
  const [status, setStatus] = useState<AiStatus | null>(null);
  const [backendResolution, setBackendResolution] = useState<BackendResolution | null>(null);
  const [thread, setThread] = useState<ThreadMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [latestCitations, setLatestCitations] = useState<AiCitation[]>([]);
  const [latestMarketSnapshot, setLatestMarketSnapshot] = useState<AiMarketSnapshot | null>(null);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const [askElapsedMs, setAskElapsedMs] = useState(0);
  const [warmState, setWarmState] = useState<WarmState>("idle");
  const [warmMessage, setWarmMessage] = useState<string | null>(null);
  const indexSignature = getIndexSignature(status);
  const warmedModelRef = useRef<string | null>(null);
  const marketPromptInfo = analyzeAiMarketPrompt(prompt);

  async function refreshStatus() {
    setIsLoadingStatus(true);
    try {
      const [nextStatus, nextBackend] = await Promise.all([
        getAiStatus(),
        resolveOpenBBBackend().catch(() => null),
      ]);
      setStatus(nextStatus);
      setBackendResolution(nextBackend);
      setErrorMessage(null);
      if (nextStatus.chatModel) {
        localStorage.setItem(AI_CHAT_MODEL_KEY, nextStatus.chatModel);
      }
      if (nextStatus.embeddingModel) {
        localStorage.setItem(AI_EMBEDDING_MODEL_KEY, nextStatus.embeddingModel);
      }
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to refresh AI status.");
    } finally {
      setIsLoadingStatus(false);
    }
  }

  useEffect(() => {
    let active = true;

    const loadStatus = async () => {
      setIsLoadingStatus(true);
      try {
        const [nextStatus, nextBackend] = await Promise.all([
          getAiStatus(),
          resolveOpenBBBackend().catch(() => null),
        ]);
        if (!active) {
          return;
        }
        setStatus(nextStatus);
        setBackendResolution(nextBackend);
        setErrorMessage(null);
        if (nextStatus.chatModel) {
          localStorage.setItem(AI_CHAT_MODEL_KEY, nextStatus.chatModel);
        }
        if (nextStatus.embeddingModel) {
          localStorage.setItem(AI_EMBEDDING_MODEL_KEY, nextStatus.embeddingModel);
        }
      } catch (error) {
        if (!active) {
          return;
        }
        setErrorMessage(error instanceof Error ? error.message : "Failed to load AI status.");
      } finally {
        if (active) {
          setIsLoadingStatus(false);
        }
      }
    };

    void loadStatus();

    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    const storageKey = getThreadStorageKey(status?.repoRoot ?? null);
    if (!storageKey || !indexSignature) {
      setThread([]);
      setLatestCitations([]);
      setLatestMarketSnapshot(null);
      return;
    }

    try {
      const stored = localStorage.getItem(storageKey);
      if (!stored) {
        setThread([]);
        setLatestCitations([]);
        setLatestMarketSnapshot(null);
        return;
      }

      const parsed = parsePersistedThread(stored, indexSignature);
      setThread(parsed);
      const latestAssistant = [...parsed].reverse().find((message) => message.role === "assistant");
      setLatestCitations(latestAssistant?.citations ?? []);
      setLatestMarketSnapshot(latestAssistant?.marketSnapshot ?? null);
    } catch {
      setThread([]);
      setLatestCitations([]);
      setLatestMarketSnapshot(null);
    }
  }, [indexSignature, status?.repoRoot]);

  useEffect(() => {
    const storageKey = getThreadStorageKey(status?.repoRoot ?? null);
    if (!storageKey || !indexSignature) {
      return;
    }

    const payload: PersistedThreadState = {
      indexSignature,
      messages: thread,
    };
    localStorage.setItem(storageKey, JSON.stringify(payload));
  }, [indexSignature, thread, status?.repoRoot]);

  useEffect(() => {
    if (!isAsking) {
      setAskElapsedMs(0);
      return;
    }

    const startedAt = Date.now();
    const timer = window.setInterval(() => {
      setAskElapsedMs(Date.now() - startedAt);
    }, 250);

    return () => {
      window.clearInterval(timer);
    };
  }, [isAsking]);

  useEffect(() => {
    if (import.meta.env.MODE === "test") {
      return;
    }
    if (!status?.ollamaReachable || !status.chatModel) {
      setWarmState("idle");
      setWarmMessage(null);
      return;
    }
    if (warmedModelRef.current === status.chatModel) {
      setWarmState("ready");
      setWarmMessage(`${status.chatModel} ready`);
      return;
    }

    let active = true;
    setWarmState("warming");
    setWarmMessage(`Priming ${status.chatModel}...`);

    void warmAiChatModel()
      .then((result) => {
        if (!active) {
          return;
        }
        if (result.ok) {
          const warmedModel = result.usedModel ?? status.chatModel;
          warmedModelRef.current = warmedModel;
          setWarmState("ready");
          setWarmMessage(`${warmedModel} ready`);
          return;
        }
        setWarmState("failed");
        setWarmMessage("Warm-up unavailable. The first answer may be slower.");
      })
      .catch(() => {
        if (!active) {
          return;
        }
        setWarmState("failed");
        setWarmMessage("Warm-up unavailable. The first answer may be slower.");
      });

    return () => {
      active = false;
    };
  }, [status?.chatModel, status?.ollamaReachable]);

  const handleIndex = async (force: boolean) => {
    if (!status?.repoRoot) {
      return;
    }

    setIsIndexing(true);
    setActionMessage(null);

    try {
      const result = await buildAiIndex(status.repoRoot, force);
      setThread([]);
      setLatestCitations([]);
      setLatestMarketSnapshot(null);
      setActionMessage(
        `Indexed ${result.indexedFiles}/${result.scannedFiles} files into ${result.chunkCount} chunks.`,
      );
      await refreshStatus();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to build AI index.");
    } finally {
      setIsIndexing(false);
    }
  };

  const handleClearIndex = async () => {
    if (!status?.repoRoot) {
      return;
    }

    setIsClearing(true);
    setActionMessage(null);

    try {
      await clearAiIndex(status.repoRoot);
      const storageKey = getThreadStorageKey(status.repoRoot);
      if (storageKey) {
        localStorage.removeItem(storageKey);
      }
      setThread([]);
      setLatestCitations([]);
      setLatestMarketSnapshot(null);
      setActionMessage("AI index cleared.");
      await refreshStatus();
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to clear AI index.");
    } finally {
      setIsClearing(false);
    }
  };

  const handleAsk = async () => {
    const normalizedPrompt = prompt.trim();
    if (!normalizedPrompt) {
      return;
    }

    let marketContext = null;
    let marketDataFallbackMessage: string | null = null;
    if (marketPromptInfo.isFinanceQuestion) {
      try {
        marketContext = await buildAiMarketContext(normalizedPrompt);
      } catch (error) {
        const detail = error instanceof Error
          ? error.message
          : "Failed to load OpenBB market data for this question.";
        if (!status?.indexReady) {
          setErrorMessage(
            detail === AI_MARKET_BACKEND_REQUIRED_MESSAGE
              ? "Connect an OpenBB backend for live market-data answers, or build the AI index to fall back to repository guidance."
              : detail,
          );
          return;
        }
        marketDataFallbackMessage = detail === AI_MARKET_BACKEND_REQUIRED_MESSAGE
          ? "OpenBB market data is unavailable. Answering from the repository index instead."
          : `OpenBB market data is unavailable. ${detail}`;
      }
    }

    if (!status?.repoRoot && !marketContext) {
      return;
    }

    if (!status?.indexReady && !marketContext) {
      return;
    }

    const previousThread = thread;
    const userMessage: ThreadMessage = { role: "user", content: normalizedPrompt };
    const nextThread = [...thread, userMessage];

    setThread(nextThread);
    setPrompt("");
    setIsAsking(true);
    setErrorMessage(null);
    setActionMessage(marketContext?.actionLabel ?? marketDataFallbackMessage);

    try {
      const response: AiAskResponse = await askAiQuestion({
        repoRoot: status?.repoRoot ?? ".",
        maxContextChunks: DEFAULT_ASK_CONTEXT_CHUNKS,
        supplementalContext: marketContext?.supplementalContext,
        supplementalOnly: Boolean(marketContext),
        messages: nextThread.map((message) => ({
          role: message.role,
          content: message.content,
        })),
      });
      const assistantMessage: ThreadMessage = {
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        marketSnapshot: marketContext?.snapshot,
        usedModel: response.usedModel,
        attemptedModels: response.attemptedModels,
        modelTotalMs: response.modelTotalMs,
        loadMs: response.loadMs,
        promptEvalMs: response.promptEvalMs,
        evalMs: response.evalMs,
        timingMs: response.timingMs,
        retrievalMode: response.retrievalMode,
      };
      const finalThread = [...nextThread, assistantMessage];
      setThread(finalThread);
      setLatestCitations(response.citations);
      setLatestMarketSnapshot(marketContext?.snapshot ?? null);
    } catch (error) {
      setThread(previousThread);
      setErrorMessage(error instanceof Error ? error.message : "Failed to ask the project AI.");
    } finally {
      setIsAsking(false);
    }
  };

  const repoReady = Boolean(status?.repoReady);
  const indexReady = Boolean(status?.indexReady);
  const canAskFromMarketData = marketPromptInfo.isFinanceQuestion;
  const askEnabled = Boolean(prompt.trim()) && !isAsking && (indexReady || canAskFromMarketData);
  const showLexicalWarning = status?.mode === "lexical";
  const hasExistingIndex = Boolean((status?.chunkCount ?? 0) > 0);
  const marketDataBadge = backendResolution
    ? backendResolution.connected
      ? {
        label: "Live Market Data Ready",
        className: "border-emerald-500/60 bg-emerald-500/10 text-emerald-300",
      }
      : {
        label: "Market Data Offline",
        className: "border-amber-500/60 bg-amber-500/10 text-amber-300",
      }
    : null;
  const indexStateMessage = !repoReady
    ? "Set the workspace working directory to a Git repository before using the AI tab."
    : indexReady
      ? "Ask about routes, commands, state flow, or backend resolution."
      : hasExistingIndex
        ? "Rebuild the stale index to re-enable chat for the current repository state."
        : "Build the index to enable chat.";
  const chatHelperMessage = marketPromptInfo.isFinanceQuestion
    ? marketPromptInfo.symbol
      ? indexReady
        ? `Finance prompts for ${marketPromptInfo.symbol} use OpenBB market data when available and fall back to repository context if the backend is offline.`
        : `Finance prompts for ${marketPromptInfo.symbol} can use live OpenBB market data even without a repo index.`
      : indexReady
        ? "Finance prompts use OpenBB market data when available. A ticker is best, and repository context remains available as fallback."
        : "Finance prompts can use OpenBB market data. A ticker is best, but an official company name also works."
    : `Fast mode uses ${DEFAULT_ASK_CONTEXT_CHUNKS} context chunks and a local fallback chain.`;
  const indexStatusValue = indexReady ? "Ready" : hasExistingIndex ? "Stale" : "Missing";
  const askPhaseLabel = isAsking ? getAskPhase(askElapsedMs) : null;
  const fallbackChain = status?.chatCandidates?.length
    ? status.chatCandidates.slice(0, 3).join(" -> ")
    : status?.chatModel ?? "Not detected";

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">AI</h1>
          <p className="body-sm-regular text-theme-muted">
            Local Ollama-backed repository guide tuned for fast, grounded answers.
          </p>
        </div>
        <div className="flex flex-wrap items-center justify-end gap-2">
          {marketDataBadge ? (
            <span
              className={`rounded-sm border px-3 py-2 body-xxs-medium ${marketDataBadge.className}`}
            >
              {marketDataBadge.label}
            </span>
          ) : null}
          {showLexicalWarning ? (
            <span className="rounded-sm border border-amber-500/60 bg-amber-500/10 px-3 py-2 body-xxs-medium text-amber-300">
              Lexical fallback mode
            </span>
          ) : null}
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
      {!status?.ollamaReachable ? (
        <div className="mb-3 rounded-sm border border-amber-500/60 bg-amber-500/10 p-3">
          <p className="body-xs-medium text-amber-300">
            Start Ollama at <code>http://localhost:11434</code> and install a chat model with
            <code> ollama pull qwen2.5-coder:1.5b</code>.
          </p>
          <p className="mt-1 body-xxs-regular text-amber-200">
            For semantic retrieval, also install <code>ollama pull qwen3-embedding</code>.
          </p>
        </div>
      ) : null}

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-2">
        <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h2 className="mb-3 body-sm-medium text-theme-primary">Status</h2>
          <div className="grid grid-cols-1 gap-2 md:grid-cols-2">
            <StatusRow label="Ollama" value={status?.ollamaReachable ? "Connected" : "Offline"} />
            <StatusRow label="Retrieval" value={status?.mode ?? "lexical"} />
            <StatusRow label="Preferred Chat Model" value={status?.chatModel ?? "Not detected"} />
            <StatusRow label="Fallback Chain" value={fallbackChain} />
            <StatusRow label="Embedding Model" value={status?.embeddingModel ?? "Not detected"} />
            <StatusRow label="OpenBB Backend" value={backendResolution ? (backendResolution.connected ? "Connected" : "Offline") : "Resolving..."} />
            <StatusRow label="OpenBB URL" value={backendResolution?.baseUrl ?? "Unavailable"} />
            <StatusRow label="Model Cache" value={getWarmStateLabel(warmState, warmMessage)} />
            <StatusRow label="Repo Root" value={status?.repoRoot ?? "No Git repository detected"} />
            <StatusRow
              label="Last Indexed"
              value={status ? formatTimestamp(status.lastIndexedAt) : "Loading..."}
            />
          </div>
          {backendResolution ? (
            <p className="mt-3 body-xxs-regular text-theme-muted">
              OpenBB status: {formatBackendDetail(backendResolution.detail, backendResolution.connected)}
            </p>
          ) : null}
          <p className="mt-3 body-xxs-regular text-theme-muted">
            {isLoadingStatus
              ? "Refreshing status..."
              : `${status?.availableModels.length ?? 0} local Ollama models detected.`}
          </p>
        </section>

        <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <h2 className="mb-3 body-sm-medium text-theme-primary">Index</h2>
          <div className="grid grid-cols-1 gap-2 md:grid-cols-3">
            <button
              type="button"
              className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
              onClick={() => void handleIndex(false)}
              disabled={!repoReady || isIndexing}
            >
              {isIndexing ? "Indexing..." : "Index Now"}
            </button>
            <button
              type="button"
              className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
              onClick={() => void handleIndex(true)}
              disabled={!repoReady || isIndexing}
            >
              Rebuild
            </button>
            <button
              type="button"
              className="button-secondary rounded-sm px-3 py-2 body-xs-medium"
              onClick={() => void handleClearIndex()}
              disabled={!repoReady || isClearing}
            >
              {isClearing ? "Clearing..." : "Clear Index"}
            </button>
          </div>
          <div className="mt-3 grid grid-cols-1 gap-2 md:grid-cols-3">
            <StatusRow label="Index State" value={indexStatusValue} />
            <StatusRow label="Chunks" value={String(status?.chunkCount ?? 0)} />
            <StatusRow label="Repo Status" value={repoReady ? "Ready" : "Needs Git root"} />
          </div>
          {!repoReady || (hasExistingIndex && !indexReady) ? (
            <p className="mt-3 body-xxs-regular text-theme-muted">{indexStateMessage}</p>
          ) : null}
        </section>
      </div>

      <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-[1.35fr_0.65fr]">
        <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          <div className="mb-3 flex items-center justify-between">
            <h2 className="body-sm-medium text-theme-primary">Chat</h2>
            <p className="body-xxs-regular text-theme-muted">{indexStateMessage}</p>
          </div>

          <div className="mb-3 max-h-[460px] space-y-3 overflow-auto rounded-sm border border-theme-outline bg-theme-secondary p-3">
            {thread.length === 0 ? (
              <p className="body-xs-regular text-theme-muted">
                Ask for a project explanation after the index is ready. Example: "Explain the tab structure."
              </p>
            ) : (
              thread.map((message, index) => (
                <div
                  key={`${message.role}-${index}`}
                  className={`rounded-sm border px-3 py-2 ${
                    message.role === "assistant"
                      ? "border-sky-500/30 bg-sky-500/5"
                      : "border-theme-outline bg-theme-primary"
                  }`}
                >
                  <p className="body-xxs-medium uppercase tracking-wide text-theme-muted">
                    {message.role}
                  </p>
                  <div className="mt-1 whitespace-pre-wrap body-xs-regular text-theme-primary">
                    {message.content}
                  </div>
                  {message.marketSnapshot ? (
                    <MarketSnapshotCard snapshot={message.marketSnapshot} />
                  ) : null}
                  <AssistantMeta message={message} />
                </div>
              ))
            )}
          </div>

          <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
            <label htmlFor="ai-question" className="mb-2 block body-xs-medium text-theme-primary">
              Question
            </label>
            <textarea
              id="ai-question"
              className="min-h-28 w-full rounded-sm border border-theme-outline bg-theme-primary px-3 py-2 body-xs-regular text-theme-primary outline-none"
              placeholder="Explain how this project resolves the OpenBB backend, or ask: Analyze IBM financial statements and estimate a price range."
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              disabled={isAsking}
            />
            {isAsking ? (
              <p className="mt-3 body-xxs-regular text-theme-muted" role="status">
                {askPhaseLabel} {formatDurationLabel(askElapsedMs)} elapsed.
              </p>
            ) : (
              <p className="mt-3 body-xxs-regular text-theme-muted">
                {chatHelperMessage}
              </p>
            )}
            <div className="mt-3 flex justify-end">
              <button
                type="button"
                className="button-secondary rounded-sm px-4 py-2 body-xs-medium"
                onClick={() => void handleAsk()}
                disabled={!askEnabled}
              >
                {isAsking ? "Working..." : "Ask AI"}
              </button>
            </div>
          </div>
        </section>

        <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
          {latestMarketSnapshot ? (
            <div className="mb-4">
              <div className="mb-3 flex items-center justify-between">
                <h2 className="body-sm-medium text-theme-primary">OpenBB Data</h2>
                <p className="body-xxs-regular text-theme-muted">Latest market context used by AI.</p>
              </div>
              <MarketSnapshotCard snapshot={latestMarketSnapshot} />
            </div>
          ) : null}
          <div className="mb-3 flex items-center justify-between">
            <h2 className="body-sm-medium text-theme-primary">Sources</h2>
            <p className="body-xxs-regular text-theme-muted">Click to copy a file range.</p>
          </div>
          <div className="space-y-2">
            {latestCitations.length === 0 ? (
              <p className="body-xs-regular text-theme-muted">
                Sources from the latest AI answer will appear here.
              </p>
            ) : (
              latestCitations.map((citation, index) => (
                <button
                  key={`${citation.path}-${citation.startLine}-${index}`}
                  type="button"
                  data-testid="ai-citation"
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 text-left"
                  onClick={() => copyCitationToClipboard(citation)}
                >
                  <p className="body-xs-medium text-theme-primary">{citation.path}</p>
                  <p className="body-xxs-regular text-theme-muted">
                    lines {citation.startLine}-{citation.endLine} | score {citation.score.toFixed(3)}
                  </p>
                </button>
              ))
            )}
          </div>
        </section>
      </div>
    </div>
  );
}

export const Route = createFileRoute("/ai")({
  component: AiPage,
});
