/// <reference types="vitest/globals" />
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { Route as AiRoute } from "../../routes/ai";
import type {
  AiGatewaySettings,
  AiGatewayStatus,
  AiRunCreated,
  AiRunEvent,
} from "../../types/ai";

const getAiGatewayStatusMock = vi.fn();
const getAiSettingsMock = vi.fn();
const buildAiIndexMock = vi.fn();
const clearAiIndexMock = vi.fn();
const createAiRunMock = vi.fn();
const streamAiRunMock = vi.fn();
const cancelAiRunMock = vi.fn();
const listAiSessionsMock = vi.fn();
const getAiSessionMock = vi.fn();
const respondToAiApprovalMock = vi.fn();
const resolveOpenBBBackendMock = vi.fn();
const analyzeAiMarketPromptMock = vi.fn();
const buildAiMarketContextMock = vi.fn();

vi.mock("@tanstack/react-router", () => ({
  Link: ({ to, className, children }: { to: string; className?: string; children: React.ReactNode }) => (
    <a href={to} className={className}>
      {children}
    </a>
  ),
  createFileRoute: vi.fn(
    () => (options: {
      component: React.ComponentType;
    }) => ({
      options: {
        component: options.component,
      },
    }),
  ),
}));

vi.mock("../../lib/aiApi", () => ({
  getAiGatewayStatus: (...args: unknown[]) => getAiGatewayStatusMock(...args),
  getAiSettings: (...args: unknown[]) => getAiSettingsMock(...args),
  buildAiIndex: (...args: unknown[]) => buildAiIndexMock(...args),
  clearAiIndex: (...args: unknown[]) => clearAiIndexMock(...args),
  createAiRun: (...args: unknown[]) => createAiRunMock(...args),
  streamAiRun: (...args: unknown[]) => streamAiRunMock(...args),
  cancelAiRun: (...args: unknown[]) => cancelAiRunMock(...args),
  listAiSessions: (...args: unknown[]) => listAiSessionsMock(...args),
  getAiSession: (...args: unknown[]) => getAiSessionMock(...args),
  respondToAiApproval: (...args: unknown[]) => respondToAiApprovalMock(...args),
}));

vi.mock("../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: () => resolveOpenBBBackendMock(),
  formatBackendDetail: (detail: string) => detail,
}));

vi.mock("../../lib/aiMarketContext", () => ({
  AI_MARKET_BACKEND_REQUIRED_MESSAGE: "Connect an OpenBB backend to use market data in the AI tab.",
  analyzeAiMarketPrompt: (prompt: string) => analyzeAiMarketPromptMock(prompt),
  buildAiMarketContext: (prompt: string) => buildAiMarketContextMock(prompt),
}));

function makeGatewayStatus(overrides: Partial<AiGatewayStatus> = {}): AiGatewayStatus {
  return {
    gatewayVersion: "1.0.0",
    workspacePath: "C:/repo",
    workspaceReady: true,
    defaultProvider: "ollama",
    defaultMode: "ask",
    providers: [
      {
        provider: "ollama",
        installed: true,
        reachable: true,
        authenticated: true,
        degraded: false,
        version: null,
        mode: "http",
        capabilities: {
          chat: true,
          streaming: false,
          retrieval: true,
          embeddings: true,
          resumeSession: false,
          approvals: false,
          fileEdits: false,
          shellExec: false,
        },
        models: ["qwen2.5-coder:1.5b"],
        defaultModel: "qwen2.5-coder:1.5b",
        error: null,
      },
      {
        provider: "codex",
        installed: true,
        reachable: true,
        authenticated: true,
        degraded: false,
        version: "0.31.0",
        mode: "exec",
        capabilities: {
          chat: true,
          streaming: true,
          retrieval: true,
          embeddings: false,
          resumeSession: false,
          approvals: false,
          fileEdits: false,
          shellExec: false,
        },
        models: [],
        defaultModel: null,
        error: null,
      },
      {
        provider: "gemini",
        installed: true,
        reachable: true,
        authenticated: false,
        degraded: true,
        version: "0.1.0",
        mode: "headless",
        capabilities: {
          chat: true,
          streaming: true,
          retrieval: true,
          embeddings: false,
          resumeSession: false,
          approvals: false,
          fileEdits: false,
          shellExec: false,
        },
        models: [],
        defaultModel: null,
        error: {
          code: "E_PROVIDER_NOT_AUTHENTICATED",
          message: "Gemini CLI is installed but not authenticated.",
          detail: "Set GEMINI_API_KEY.",
        },
      },
    ],
    index: {
      workspacePath: "C:/repo",
      ready: true,
      lastIndexedAt: "2026-03-28T00:00:00Z",
      chunkCount: 42,
      mode: "hybrid",
      revision: null,
      embeddingProvider: "ollama",
      embeddingModel: "qwen3-embedding",
      stale: false,
    },
    settingsPath: "C:/Users/test/.openbb_platform/user_settings.json",
    featureFlags: {
      codexAgentEnabled: false,
      geminiAgentEnabled: false,
    },
    ...overrides,
  };
}

function makeSettings(overrides: Partial<AiGatewaySettings> = {}): AiGatewaySettings {
  return {
    defaultProvider: "ollama",
    defaultMode: "ask",
    retrieval: {
      strategy: "hybrid",
      topK: 8,
      allowRepoSummary: true,
    },
    providers: {
      ollama: {
        enabled: true,
        baseUrl: "http://127.0.0.1:11434/api",
        defaultChatModel: "qwen2.5-coder:1.5b",
        defaultEmbeddingModel: "qwen3-embedding",
        keepAlive: "15m",
        requestTimeoutMs: 45000,
      },
      codex: {
        enabled: true,
        askTransport: "exec",
        agentTransport: "app-server",
        sandbox: "read-only",
        approvalPolicy: "on-request",
      },
      gemini: {
        enabled: true,
        askTransport: "headless",
        agentTransport: "acp",
        sandbox: "read-only",
        approvalPolicy: "default",
      },
    },
    featureFlags: {
      codexAgentEnabled: false,
      geminiAgentEnabled: false,
    },
    ...overrides,
  };
}

describe("AI Route", () => {
  const AiComponent = AiRoute.options.component as React.ComponentType;

  beforeEach(() => {
    getAiGatewayStatusMock.mockReset();
    getAiSettingsMock.mockReset();
    buildAiIndexMock.mockReset();
    clearAiIndexMock.mockReset();
    createAiRunMock.mockReset();
    streamAiRunMock.mockReset();
    cancelAiRunMock.mockReset();
    listAiSessionsMock.mockReset();
    getAiSessionMock.mockReset();
    respondToAiApprovalMock.mockReset();
    resolveOpenBBBackendMock.mockReset();
    analyzeAiMarketPromptMock.mockReset();
    buildAiMarketContextMock.mockReset();

    getAiGatewayStatusMock.mockResolvedValue(makeGatewayStatus());
    getAiSettingsMock.mockResolvedValue(makeSettings());
    resolveOpenBBBackendMock.mockResolvedValue({
      baseUrl: "http://127.0.0.1:6900",
      connected: true,
      detail: "Using fallback URL.",
      source: "fallback",
    });
    analyzeAiMarketPromptMock.mockReturnValue({
      isFinanceQuestion: false,
      symbol: null,
      searchQuery: null,
    });
    buildAiMarketContextMock.mockResolvedValue(null);
    listAiSessionsMock.mockResolvedValue([]);
    getAiSessionMock.mockResolvedValue(null);
    respondToAiApprovalMock.mockResolvedValue({ ok: true });
    createAiRunMock.mockResolvedValue({
      runId: "run-1",
      sessionId: "session-1",
      streamUrl: "/v1/runs/run-1/stream",
    } satisfies AiRunCreated);
    streamAiRunMock.mockImplementation(
      async (_runId: string, onEvent: (event: AiRunEvent) => void) => {
        onEvent({ type: "status", phase: "running" });
        onEvent({ type: "messageFinal", text: "Default AI response." });
        onEvent({
          type: "done",
          usage: {
            usedModel: "qwen2.5-coder:1.5b",
            citations: [],
            retrievalMode: "hybrid",
            timingMs: 1200,
          },
        });
      },
    );
  });

  test("renders provider, index, and backend status from the gateway", async () => {
    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByText(/Gateway-based repository and market assistant/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/Live Market Data Ready/i)).toBeInTheDocument();
    expect(screen.getByText(/Index Ready/i)).toBeInTheDocument();
    expect(screen.getByText(/^Gateway Version$/i)).toBeInTheDocument();
    expect(screen.getByText("1.0.0")).toBeInTheDocument();
    expect(screen.getByText(/^OpenBB Backend$/i)).toBeInTheDocument();
    expect(screen.getByText(/^Connected$/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: /Open AI Settings/i })).toHaveAttribute("href", "/ai-settings");
  });

  test("keeps agent mode disabled when the selected provider lacks agent capability", async () => {
    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/Mode/i)).toBeInTheDocument();
    });

    const modeSelect = screen.getByLabelText(/Mode/i) as HTMLSelectElement;
    const agentOption = Array.from(modeSelect.options).find((option) => option.value === "agent");

    expect(agentOption).toBeDefined();
    expect(agentOption?.disabled).toBe(true);
  });

  test("runs finance prompts with OpenBB market context even when the index is missing", async () => {
    getAiGatewayStatusMock.mockResolvedValue(
      makeGatewayStatus({
        index: {
          workspacePath: "C:/repo",
          ready: false,
          lastIndexedAt: null,
          chunkCount: 0,
          mode: "lexical",
          revision: null,
          embeddingProvider: null,
          embeddingModel: null,
          stale: false,
        },
      }),
    );
    analyzeAiMarketPromptMock.mockReturnValue({
      isFinanceQuestion: true,
      symbol: "IBM",
      searchQuery: "IBM",
    });
    buildAiMarketContextMock.mockResolvedValue({
      symbol: "IBM",
      actionLabel: "Using OpenBB market data for IBM.",
      supplementalContext: "OpenBB market data for IBM",
      snapshot: {
        symbol: "IBM",
        resolvedName: "International Business Machines",
        currentPrice: "$194.50",
        sessionChange: "$1.25 (0.7%)",
        targetRange: "$175.00 - $225.00 | consensus $205.00",
        recommendation: "buy (2.1)",
        analysts: "18",
        providerSummary: "openbb | yfinance",
        asOf: "2026-03-28T00:00:00Z",
        sections: [],
      },
    });
    streamAiRunMock.mockImplementation(
      async (_runId: string, onEvent: (event: AiRunEvent) => void) => {
        onEvent({ type: "messageFinal", text: "Using OpenBB data, the likely range is $175 to $225." });
        onEvent({
          type: "done",
          usage: {
            usedModel: "qwen2.5-coder:1.5b",
            citations: [],
            retrievalMode: "supplemental",
            timingMs: 2100,
          },
        });
      },
    );

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/^Question$/i)).toBeEnabled();
    });

    fireEvent.change(screen.getByLabelText(/^Question$/i), {
      target: { value: "IBM의 재무제표를 분석한 후 예상 주가의 범위를 알려줘" },
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Ask AI/i })).toBeEnabled();
    });

    fireEvent.click(screen.getByRole("button", { name: /Ask AI/i }));

    await waitFor(() => {
      expect(screen.getByText(/Using OpenBB data, the likely range is/i)).toBeInTheDocument();
    });

    expect(buildAiMarketContextMock).toHaveBeenCalled();
    expect(createAiRunMock).toHaveBeenCalledWith(
      expect.objectContaining({
        provider: "ollama",
        supplementalContext: "OpenBB market data for IBM",
        retrieval: expect.objectContaining({
          enabled: false,
        }),
      }),
    );
    expect(screen.getAllByTestId("ai-market-snapshot")).toHaveLength(2);
    expect(screen.getAllByText(/International Business Machines/i).length).toBeGreaterThanOrEqual(1);
  });

  test("falls back to repository answers when market data is unavailable but the index is ready", async () => {
    analyzeAiMarketPromptMock.mockReturnValue({
      isFinanceQuestion: true,
      symbol: "IBM",
      searchQuery: "IBM",
    });
    buildAiMarketContextMock.mockRejectedValue(
      new Error("Connect an OpenBB backend to use market data in the AI tab."),
    );
    streamAiRunMock.mockImplementation(
      async (_runId: string, onEvent: (event: AiRunEvent) => void) => {
        onEvent({ type: "messageFinal", text: "Repository fallback answer without live market data." });
        onEvent({
          type: "done",
          usage: {
            usedModel: "qwen2.5-coder:1.5b",
            citations: [],
            retrievalMode: "hybrid",
            timingMs: 1800,
          },
        });
      },
    );

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/^Question$/i)).toBeEnabled();
    });

    fireEvent.change(screen.getByLabelText(/^Question$/i), {
      target: { value: "Analyze IBM financial statements and estimate a price range." },
    });
    fireEvent.click(screen.getByRole("button", { name: /Ask AI/i }));

    await waitFor(() => {
      expect(screen.getByText(/Repository fallback answer without live market data/i)).toBeInTheDocument();
    });

    expect(screen.getByText(/OpenBB market data is unavailable\. Answering from the repository index instead\./i)).toBeInTheDocument();
    expect(createAiRunMock).toHaveBeenCalledWith(
      expect.objectContaining({
        retrieval: expect.objectContaining({
          enabled: true,
        }),
      }),
    );
  });
});
