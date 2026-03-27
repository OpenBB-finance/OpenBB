/// <reference types="vitest/globals" />
// @vitest-environment node

import { describe, expect, test } from "vitest";
import { __aiBrowserFallbackInternals } from "../../../dev/aiBrowserFallback";

describe("aiBrowserFallback internals", () => {
  test("prefers smaller coder chat models and filters embedding-only models", () => {
    const candidates = __aiBrowserFallbackInternals.sortChatCandidates([
      {
        name: "qwen3-embedding:latest",
        size: 900_000_000,
        details: { parameter_size: "0.6B" },
      },
      {
        name: "qwen2.5:7b",
        size: 4_700_000_000,
        details: { parameter_size: "7B" },
      },
      {
        name: "qwen3-coder:latest",
        size: 18_000_000_000,
        details: { parameter_size: "30.5B" },
      },
      {
        name: "qwen2.5-coder:1.5b",
        size: 986_000_000,
        details: { parameter_size: "1.5B" },
      },
    ]).map((model) => model.name);

    expect(candidates).toEqual([
      "qwen2.5-coder:1.5b",
      "qwen3-coder:latest",
      "qwen2.5:7b",
    ]);
  });

  test("merges adjacent citations from the same file", () => {
    const citations = __aiBrowserFallbackInternals.compactCitations([
      { path: "desktop/src/routes/ai.tsx", startLine: 10, endLine: 40, score: 0.9 },
      { path: "desktop/src/routes/ai.tsx", startLine: 48, endLine: 72, score: 0.8 },
      { path: "desktop/src/lib/aiApi.ts", startLine: 1, endLine: 24, score: 0.7 },
    ]);

    expect(citations).toEqual([
      { path: "desktop/src/routes/ai.tsx", startLine: 10, endLine: 72, score: 0.9 },
      { path: "desktop/src/lib/aiApi.ts", startLine: 1, endLine: 24, score: 0.7 },
    ]);
  });

  test("converts Ollama nanosecond timings to milliseconds", () => {
    expect(__aiBrowserFallbackInternals.ollamaDurationToMs(2_550_000_000)).toBe(2550);
    expect(__aiBrowserFallbackInternals.ollamaDurationToMs(null)).toBeNull();
  });

  test("prefers literal route-definition chunks for endpoint questions", () => {
    const chunks = [
      {
        path: "desktop/dev/aiBrowserFallback.ts",
        startLine: 100,
        endLine: 140,
        sha1: "a",
        language: "ts",
        text: "function createAiBrowserFallbackPlugin() { return true; }",
      },
      {
        path: "desktop/dev/aiBrowserFallback.ts",
        startLine: 1300,
        endLine: 1380,
        sha1: "b",
        language: "ts",
        text: `server.middlewares.use("/__ai", async (req, res) => {
if (req.method === "GET" && requestUrl.pathname === "/status") {}
if (req.method === "POST" && requestUrl.pathname === "/ask") {}
}`,
      },
      {
        path: "README.md",
        startLine: 1,
        endLine: 20,
        sha1: "c",
        language: "md",
        text: "AI browser fallback overview",
      },
    ];

    const ranked = __aiBrowserFallbackInternals
      .rankChunksLexical(
        "Which file implements the browser AI fallback, and what endpoints does it expose?",
        chunks,
      )
      .map((entry: { index: number }) => chunks[entry.index]?.path);

    expect(ranked[0]).toBe("desktop/dev/aiBrowserFallback.ts");
    expect(ranked.slice(0, 2)).toContain("desktop/dev/aiBrowserFallback.ts");
  });

  test("disables repository summary for endpoint lookups", () => {
    expect(
      __aiBrowserFallbackInternals.shouldIncludeRepositorySummary(
        "Which endpoints does the browser AI fallback expose?",
      ),
    ).toBe(false);
    expect(
      __aiBrowserFallbackInternals.shouldIncludeRepositorySummary(
        "How does the AI tab work overall?",
      ),
    ).toBe(true);
  });

  test("skips noisy HTTP record fixtures from the browser AI index", () => {
    expect(
      __aiBrowserFallbackInternals.shouldSkipRelativePath(
        "openbb_platform/providers/fred/tests/record/http/test_fred_fetchers/example.yaml",
      ),
    ).toBe(true);
    expect(
      __aiBrowserFallbackInternals.shouldSkipRelativePath("desktop/src/routes/ai.tsx"),
    ).toBe(false);
  });

  test("truncates oversized lines and chunks during indexing", () => {
    const giantLine = "x".repeat(20_000);
    const chunks = __aiBrowserFallbackInternals.chunkText(
      "desktop/src/components/GamestonkIcon.tsx",
      `${giantLine}\n${giantLine}`,
    );

    expect(chunks).toHaveLength(1);
    expect(chunks[0]?.text.length).toBeLessThanOrEqual(8_200);
    expect(chunks[0]?.text).toContain("truncated for AI index");
  });
});
