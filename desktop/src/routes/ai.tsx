import { createFileRoute } from "@tanstack/react-router";
import { useEffect, useState } from "react";
import { askAiQuestion, buildAiIndex, clearAiIndex, getAiStatus } from "../lib/aiApi";
import type { AiAskResponse, AiCitation, AiChatRole, AiStatus } from "../types/ai";

interface ThreadMessage {
  role: AiChatRole;
  content: string;
  citations?: AiCitation[];
  usedModel?: string;
  timingMs?: number;
  retrievalMode?: AiStatus["mode"];
}

interface PersistedThreadState {
  indexSignature: string;
  messages: ThreadMessage[];
}

const AI_CHAT_MODEL_KEY = "ai.chatModel";
const AI_EMBEDDING_MODEL_KEY = "ai.embeddingModel";

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
    !parsed ||
    typeof parsed !== "object" ||
    parsed.indexSignature !== expectedSignature ||
    !Array.isArray(parsed.messages)
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
    typeof message.timingMs === "number" ? `${message.timingMs} ms` : null,
    message.retrievalMode ?? null,
  ].filter(Boolean);

  if (parts.length === 0) {
    return null;
  }

  return <p className="mt-2 body-xxs-regular text-theme-muted">{parts.join(" | ")}</p>;
}

function AiPage() {
  const [status, setStatus] = useState<AiStatus | null>(null);
  const [thread, setThread] = useState<ThreadMessage[]>([]);
  const [prompt, setPrompt] = useState("");
  const [latestCitations, setLatestCitations] = useState<AiCitation[]>([]);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [actionMessage, setActionMessage] = useState<string | null>(null);
  const [isLoadingStatus, setIsLoadingStatus] = useState(true);
  const [isIndexing, setIsIndexing] = useState(false);
  const [isClearing, setIsClearing] = useState(false);
  const [isAsking, setIsAsking] = useState(false);
  const indexSignature = getIndexSignature(status);

  useEffect(() => {
    let active = true;

    const loadStatus = async () => {
      setIsLoadingStatus(true);
      try {
        const nextStatus = await getAiStatus();
        if (!active) {
          return;
        }
        setStatus(nextStatus);
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
      return;
    }

    try {
      const stored = localStorage.getItem(storageKey);
      if (!stored) {
        setThread([]);
        setLatestCitations([]);
        return;
      }

      const parsed = parsePersistedThread(stored, indexSignature);
      setThread(parsed);
      const latestAssistant = [...parsed].reverse().find((message) => message.role === "assistant");
      setLatestCitations(latestAssistant?.citations ?? []);
    } catch {
      setThread([]);
      setLatestCitations([]);
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

  const refreshStatus = async () => {
    setIsLoadingStatus(true);
    try {
      const nextStatus = await getAiStatus();
      setStatus(nextStatus);
      setErrorMessage(null);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to refresh AI status.");
    } finally {
      setIsLoadingStatus(false);
    }
  };

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
    if (!normalizedPrompt || !status?.repoRoot || !status.indexReady) {
      return;
    }

    const previousThread = thread;
    const userMessage: ThreadMessage = { role: "user", content: normalizedPrompt };
    const nextThread = [...thread, userMessage];

    setThread(nextThread);
    setPrompt("");
    setIsAsking(true);
    setErrorMessage(null);
    setActionMessage(null);

    try {
      const response: AiAskResponse = await askAiQuestion({
        repoRoot: status.repoRoot,
        messages: nextThread.map((message) => ({
          role: message.role,
          content: message.content,
        })),
      });
      const assistantMessage: ThreadMessage = {
        role: "assistant",
        content: response.answer,
        citations: response.citations,
        usedModel: response.usedModel,
        timingMs: response.timingMs,
        retrievalMode: response.retrievalMode,
      };
      const finalThread = [...nextThread, assistantMessage];
      setThread(finalThread);
      setLatestCitations(response.citations);
    } catch (error) {
      setThread(previousThread);
      setErrorMessage(error instanceof Error ? error.message : "Failed to ask the project AI.");
    } finally {
      setIsAsking(false);
    }
  };

  const repoReady = Boolean(status?.repoReady);
  const indexReady = Boolean(status?.indexReady);
  const showLexicalWarning = status?.mode === "lexical";
  const hasExistingIndex = Boolean((status?.chunkCount ?? 0) > 0);
  const indexStateMessage = !repoReady
    ? "Set the workspace working directory to a Git repository before using the AI tab."
    : indexReady
      ? "Ask about architecture, routes, commands, or flows."
      : hasExistingIndex
        ? "Rebuild the stale index to re-enable chat for the current repository state."
        : "Build the index to enable chat.";
  const indexStatusValue = indexReady ? "Ready" : hasExistingIndex ? "Stale" : "Missing";

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex items-center justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">AI</h1>
          <p className="body-sm-regular text-theme-muted">
            Ollama-backed, read-only repository guide for the current workspace.
          </p>
        </div>
        {showLexicalWarning ? (
          <span className="rounded-sm border border-amber-500/60 bg-amber-500/10 px-3 py-2 body-xxs-medium text-amber-300">
            Lexical fallback mode
          </span>
        ) : null}
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
            <code> ollama pull qwen3-coder</code>.
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
            <StatusRow label="Chat Model" value={status?.chatModel ?? "Not detected"} />
            <StatusRow label="Embedding Model" value={status?.embeddingModel ?? "Not detected"} />
            <StatusRow label="Repo Root" value={status?.repoRoot ?? "No Git repository detected"} />
            <StatusRow
              label="Last Indexed"
              value={status ? formatTimestamp(status.lastIndexedAt) : "Loading..."}
            />
          </div>
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
                  <AssistantMeta message={message} />
                </div>
              ))
            )}
          </div>

          <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
            <label htmlFor="ai-question" className="mb-2 block body-xs-medium text-theme-primary">
              Project Question
            </label>
            <textarea
              id="ai-question"
              className="min-h-28 w-full rounded-sm border border-theme-outline bg-theme-primary px-3 py-2 body-xs-regular text-theme-primary outline-none"
              placeholder="Explain how this project resolves the OpenBB backend."
              value={prompt}
              onChange={(event) => setPrompt(event.target.value)}
              disabled={!indexReady || isAsking}
            />
            <div className="mt-3 flex justify-end">
              <button
                type="button"
                className="button-secondary rounded-sm px-4 py-2 body-xs-medium"
                onClick={() => void handleAsk()}
                disabled={!indexReady || !prompt.trim() || isAsking}
              >
                {isAsking ? "Thinking..." : "Ask AI"}
              </button>
            </div>
          </div>
        </section>

        <section className="rounded-sm border border-theme-outline bg-theme-primary p-3">
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
