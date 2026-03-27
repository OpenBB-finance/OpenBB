/// <reference types="vitest/globals" />
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { Route as AiRoute } from "../../routes/ai";

const invokeMock = vi.fn();
const resolveOpenBBBackendMock = vi.fn();
const analyzeAiMarketPromptMock = vi.fn<
  (prompt: string) => { isFinanceQuestion: boolean; symbol: string | null; searchQuery?: string | null }
>();
const buildAiMarketContextMock = vi.fn<
  (prompt: string) => Promise<{
    symbol: string;
    actionLabel: string;
    supplementalContext: string;
      snapshot: {
        symbol: string;
        resolvedName: string | null;
        currentPrice: string;
        sessionChange: string;
        targetRange: string;
        recommendation: string;
        analysts: string;
        providerSummary?: string | null;
        asOf?: string | null;
        sections: Array<{
          title: string;
          metrics: Array<{ label: string; latest: string; prior: string; trend?: string | null }>;
        }>;
      };
  } | null>
>();

function hashRepoRoot(input: string): string {
  let hash = 5381;
  for (let index = 0; index < input.length; index += 1) {
    hash = ((hash << 5) + hash) ^ input.charCodeAt(index);
  }
  return (hash >>> 0).toString(16);
}

vi.mock("@tanstack/react-router", () => ({
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

vi.mock("@tauri-apps/api/core", () => ({
  invoke: (...args: unknown[]) => invokeMock(...args),
}));

vi.mock("../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: () => resolveOpenBBBackendMock(),
  formatBackendDetail: (detail: string) => detail,
}));

vi.mock("../../lib/aiMarketContext", () => ({
  AI_MARKET_BACKEND_REQUIRED_MESSAGE: "Connect an OpenBB backend to use live market data in the AI tab.",
  analyzeAiMarketPrompt: (prompt: string) => analyzeAiMarketPromptMock(prompt),
  buildAiMarketContext: (prompt: string) => buildAiMarketContextMock(prompt),
}));

describe("AI Route", () => {
  const AiComponent = AiRoute.options.component as React.ComponentType;

  beforeEach(() => {
    invokeMock.mockReset();
    resolveOpenBBBackendMock.mockReset();
    resolveOpenBBBackendMock.mockResolvedValue({
      baseUrl: "http://127.0.0.1:6900",
      connected: true,
      detail: "Using fallback URL.",
      source: "fallback",
    });
    analyzeAiMarketPromptMock.mockReset();
    analyzeAiMarketPromptMock.mockReturnValue({ isFinanceQuestion: false, symbol: null, searchQuery: null });
    buildAiMarketContextMock.mockReset();
    buildAiMarketContextMock.mockResolvedValue(null);
    localStorage.clear();
  });

  test("shows install guidance when Ollama is offline", async () => {
    invokeMock.mockResolvedValueOnce({
      repoRoot: "C:/repo",
      repoReady: true,
      ollamaReachable: false,
      chatModel: null,
      chatCandidates: [],
      embeddingModel: null,
      availableModels: [],
      indexReady: false,
      lastIndexedAt: null,
      chunkCount: 0,
      mode: "lexical",
    });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByText(/Start Ollama at/i)).toBeInTheDocument();
    });
    expect(screen.getByRole("button", { name: /Index Now/i })).toBeEnabled();
    expect(screen.getByLabelText(/^Question$/i)).toBeEnabled();
    expect(screen.getByRole("button", { name: /Ask AI/i })).toBeDisabled();
  });

  test("renders lexical fallback badge when no embedding model is available", async () => {
    invokeMock.mockResolvedValueOnce({
      repoRoot: "C:/repo",
      repoReady: true,
      ollamaReachable: true,
      chatModel: "qwen3-coder",
      chatCandidates: ["qwen3-coder"],
      embeddingModel: null,
      availableModels: ["qwen3-coder"],
      indexReady: false,
      lastIndexedAt: null,
      chunkCount: 12,
      mode: "lexical",
    });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByText(/Lexical fallback mode/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Live Market Data Ready/i)).toBeInTheDocument();
  });

  test("shows OpenBB backend status and URL in the status panel", async () => {
    resolveOpenBBBackendMock.mockResolvedValue({
      baseUrl: "http://127.0.0.1:6901",
      connected: false,
      detail: "Backend probe failed.",
      source: "fallback",
    });
    invokeMock.mockResolvedValueOnce({
      repoRoot: "C:/repo",
      repoReady: true,
      ollamaReachable: true,
      chatModel: "qwen3-coder",
      chatCandidates: ["qwen3-coder"],
      embeddingModel: "qwen3-embedding",
      availableModels: ["qwen3-coder", "qwen3-embedding"],
      indexReady: true,
      lastIndexedAt: "2026-03-23T12:34:56Z",
      chunkCount: 42,
      mode: "semantic",
    });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByText(/^OpenBB Backend$/i)).toBeInTheDocument();
    });
    expect(screen.getByText(/Market Data Offline/i)).toBeInTheDocument();
    expect(screen.getByText(/^Offline$/i)).toBeInTheDocument();
    expect(screen.getByText("http://127.0.0.1:6901")).toBeInTheDocument();
    expect(screen.getByText(/OpenBB status: Backend probe failed\./i)).toBeInTheDocument();
  });

  test("hides stale thread history until the index is rebuilt", async () => {
    const repoRoot = "C:/repo";
    localStorage.setItem(
      `ai.thread.${hashRepoRoot(repoRoot)}`,
      JSON.stringify({
        indexSignature: `${hashRepoRoot(repoRoot)}:2026-03-20T00:00:00Z:12:semantic`,
        messages: [
          {
            role: "assistant",
            content: "Old answer that should not be shown for a stale index.",
          },
        ],
      }),
    );

    invokeMock.mockResolvedValueOnce({
      repoRoot,
      repoReady: true,
      ollamaReachable: true,
      chatModel: "qwen3-coder",
      chatCandidates: ["qwen3-coder"],
      embeddingModel: "qwen3-embedding",
      availableModels: ["qwen3-coder", "qwen3-embedding"],
      indexReady: false,
      lastIndexedAt: "2026-03-20T00:00:00Z",
      chunkCount: 12,
      mode: "semantic",
    });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getAllByText(/Rebuild the stale index/i)).toHaveLength(2);
    });
    expect(screen.queryByText(/Old answer that should not be shown/i)).not.toBeInTheDocument();
    expect(screen.getByRole("button", { name: /Ask AI/i })).toBeDisabled();
  });

  test("renders answer and citations after asking a question", async () => {
    invokeMock
      .mockResolvedValueOnce({
        repoRoot: "C:/repo",
        repoReady: true,
        ollamaReachable: true,
        chatModel: "qwen3-coder",
        chatCandidates: ["qwen3-coder", "qwen2.5:7b"],
        embeddingModel: "qwen3-embedding",
        availableModels: ["qwen3-coder", "qwen3-embedding"],
        indexReady: true,
        lastIndexedAt: "2026-03-23T12:34:56Z",
        chunkCount: 42,
        mode: "semantic",
      })
      .mockResolvedValueOnce({
        answer: "The app defines tabs in __root.tsx and mounts Tauri commands in main.rs.",
        citations: [
          {
            path: "desktop/src/routes/__root.tsx",
            startLine: 180,
            endLine: 194,
            score: 0.98,
          },
        ],
        usedModel: "qwen3-coder",
        attemptedModels: ["qwen3-coder"],
        loadMs: 1450,
        timingMs: 2450,
        retrievalMode: "semantic",
      });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/^Question$/i)).toBeEnabled();
    });

    fireEvent.change(screen.getByLabelText(/^Question$/i), {
      target: { value: "Explain the tab structure." },
    });
    fireEvent.click(screen.getByRole("button", { name: /Ask AI/i }));

    await waitFor(() => {
      expect(screen.getByText(/defines tabs in __root\.tsx/i)).toBeInTheDocument();
    });
    expect(screen.getByTestId("ai-citation")).toHaveTextContent("desktop/src/routes/__root.tsx");
    expect(screen.getByText(/score 0\.980/i)).toBeInTheDocument();
    expect(screen.getByText(/^Fallback Chain$/i)).toBeInTheDocument();
    expect(screen.getByText(/load 1\.4 s/i)).toBeInTheDocument();
  });

  test("allows finance prompts without a repo index when OpenBB market context is available", async () => {
    analyzeAiMarketPromptMock.mockImplementation((prompt: string) => {
      if (/IBM/.test(prompt)) {
        return { isFinanceQuestion: true, symbol: "IBM", searchQuery: "IBM" };
      }
      return { isFinanceQuestion: false, symbol: null, searchQuery: null };
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
        providerSummary: "openbb",
        asOf: "2026-03-28T00:00:00Z",
        sections: [
          {
            title: "Income statement",
            metrics: [
              { label: "Revenue", latest: "61.00B", prior: "59.00B", trend: "Revenue up 3.4% vs prior period" },
            ],
          },
        ],
      },
    });
    invokeMock
      .mockResolvedValueOnce({
        repoRoot: "C:/repo",
        repoReady: true,
        ollamaReachable: true,
        chatModel: "qwen3-coder",
        chatCandidates: ["qwen3-coder"],
        embeddingModel: "qwen3-embedding",
        availableModels: ["qwen3-coder", "qwen3-embedding"],
        indexReady: false,
        lastIndexedAt: null,
        chunkCount: 0,
        mode: "lexical",
      })
      .mockResolvedValueOnce({
        answer: "Using OpenBB market data, the analyst range is $175 to $225.",
        citations: [],
        usedModel: "qwen3-coder",
        attemptedModels: ["qwen3-coder"],
        timingMs: 2200,
        retrievalMode: "supplemental",
      });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/^Question$/i)).toBeEnabled();
    });

    fireEvent.change(screen.getByLabelText(/^Question$/i), {
      target: { value: "IBM의 재무제표를 분석한 후 예상 주가의 범위를 알려주세요" },
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Ask AI/i })).toBeEnabled();
    });

    fireEvent.click(screen.getByRole("button", { name: /Ask AI/i }));

    await waitFor(() => {
      expect(screen.getByText(/Using OpenBB market data, the analyst range is/i)).toBeInTheDocument();
    });
    expect(screen.getAllByTestId("ai-market-snapshot")).toHaveLength(2);
    expect(screen.getAllByText(/International Business Machines/i)).toHaveLength(2);
    expect(screen.getAllByText(/\$175\.00 - \$225\.00 \| consensus \$205\.00/i)).toHaveLength(2);
    expect(screen.getAllByText(/openbb/i).length).toBeGreaterThanOrEqual(2);
    expect(buildAiMarketContextMock).toHaveBeenCalled();
    expect(invokeMock).toHaveBeenLastCalledWith(
      "ask_ai_question",
      expect.objectContaining({
        request: expect.objectContaining({
          supplementalOnly: true,
          supplementalContext: "OpenBB market data for IBM",
        }),
      }),
    );
  });

  test("falls back to repository answers when market data is unavailable but the AI index is ready", async () => {
    analyzeAiMarketPromptMock.mockImplementation((prompt: string) => {
      if (/IBM/.test(prompt)) {
        return { isFinanceQuestion: true, symbol: "IBM", searchQuery: "IBM" };
      }
      return { isFinanceQuestion: false, symbol: null, searchQuery: null };
    });
    buildAiMarketContextMock.mockRejectedValue(
      new Error("Connect an OpenBB backend to use live market data in the AI tab."),
    );
    invokeMock
      .mockResolvedValueOnce({
        repoRoot: "C:/repo",
        repoReady: true,
        ollamaReachable: true,
        chatModel: "qwen3-coder",
        chatCandidates: ["qwen3-coder"],
        embeddingModel: "qwen3-embedding",
        availableModels: ["qwen3-coder", "qwen3-embedding"],
        indexReady: true,
        lastIndexedAt: "2026-03-28T12:00:00Z",
        chunkCount: 42,
        mode: "semantic",
      })
      .mockResolvedValueOnce({
        answer: "Repository fallback answer without live market data.",
        citations: [],
        usedModel: "qwen3-coder",
        attemptedModels: ["qwen3-coder"],
        timingMs: 1800,
        retrievalMode: "semantic",
      });

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
    expect(invokeMock).toHaveBeenLastCalledWith(
      "ask_ai_question",
      expect.objectContaining({
        request: expect.objectContaining({
          supplementalOnly: false,
          supplementalContext: undefined,
        }),
      }),
    );
  });
});
