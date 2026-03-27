/// <reference types="vitest/globals" />
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { Route as AiRoute } from "../../routes/ai";

const invokeMock = vi.fn();

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

describe("AI Route", () => {
  const AiComponent = AiRoute.options.component as React.ComponentType;

  beforeEach(() => {
    invokeMock.mockReset();
    localStorage.clear();
  });

  test("shows install guidance when Ollama is offline", async () => {
    invokeMock.mockResolvedValueOnce({
      repoRoot: "C:/repo",
      repoReady: true,
      ollamaReachable: false,
      chatModel: null,
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
    expect(screen.getByLabelText(/Project Question/i)).toBeDisabled();
  });

  test("renders lexical fallback badge when no embedding model is available", async () => {
    invokeMock.mockResolvedValueOnce({
      repoRoot: "C:/repo",
      repoReady: true,
      ollamaReachable: true,
      chatModel: "qwen3-coder",
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
    expect(screen.getByLabelText(/Project Question/i)).toBeDisabled();
  });

  test("renders answer and citations after asking a question", async () => {
    invokeMock
      .mockResolvedValueOnce({
        repoRoot: "C:/repo",
        repoReady: true,
        ollamaReachable: true,
        chatModel: "qwen3-coder",
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
        timingMs: 321,
        retrievalMode: "semantic",
      });

    render(<AiComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/Project Question/i)).toBeEnabled();
    });

    fireEvent.change(screen.getByLabelText(/Project Question/i), {
      target: { value: "Explain the tab structure." },
    });
    fireEvent.click(screen.getByRole("button", { name: /Ask AI/i }));

    await waitFor(() => {
      expect(screen.getByText(/defines tabs in __root\.tsx/i)).toBeInTheDocument();
    });
    expect(screen.getByTestId("ai-citation")).toHaveTextContent("desktop/src/routes/__root.tsx");
    expect(screen.getByText(/score 0\.980/i)).toBeInTheDocument();
  });
});
