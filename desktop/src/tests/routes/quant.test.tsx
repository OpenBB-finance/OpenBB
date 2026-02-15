/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as QuantRoute } from "../../routes/quant";

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(() => (options: { component: React.ComponentType }) => ({
    options: {
      component: options.component,
    },
  })),
  useRouter: vi.fn(() => ({
    navigate: vi.fn(),
  })),
}));

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

function mockJsonResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("Quant Route", () => {
  const QuantComponent = QuantRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.setItem("quant_latest_run_id", "run-1");

    vi.mocked(invoke).mockResolvedValue([
      {
        id: "openbb-api",
        name: "OpenBB API",
        command: "openbb-api --host 127.0.0.1 --port 6900",
        status: "running",
        url: "http://127.0.0.1:6900",
      },
    ]);

    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);

      if (url.endsWith("/api/v1/system")) {
        return mockJsonResponse({ results: {} });
      }
      if (url.endsWith("/api/v1/quant_ml/universe")) {
        return mockJsonResponse({
          version: "v1",
          assets: [
            { symbol: "SPY", category: "us_equity_etf" },
            { symbol: "QQQ", category: "us_tech_etf" },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/train")) {
        return mockJsonResponse({
          run_id: "run-1",
          status: "queued",
          artifact_root: "/tmp/run-1",
          created_at: "2026-02-13T00:00:00Z",
        });
      }
      if (url.endsWith("/api/v1/quant_ml/runs/run-1")) {
        return mockJsonResponse({
          run_id: "run-1",
          status: "running",
          progress: 20,
          stage: "data_load",
          created_at: "2026-02-13T00:00:00Z",
          updated_at: "2026-02-13T00:00:10Z",
          logs_tail: ["training started"],
          error: null,
        });
      }

      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("renders quant controls with connected backend", async () => {
    await act(async () => {
      render(<QuantComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Quant Lab")).toBeInTheDocument();
      expect(screen.getByText(/OpenBB API connected/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Start Training/i })).toBeInTheDocument();
    });
  });

  test("starts training workflow", async () => {
    await act(async () => {
      render(<QuantComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText(/OpenBB API connected/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Start Training/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/train"))).toBe(true);
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/runs/run-1"))).toBe(true);
    });
  });

  test("shows disconnected state when health check fails", async () => {
    global.fetch = vi.fn(async (input: string | URL) => {
      const url = String(input);
      if (url.endsWith("/api/v1/system") || url.endsWith("/openapi.json") || url.endsWith("/docs")) {
        return mockJsonResponse({ detail: "unavailable" }, false, 503);
      }
      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;

    await act(async () => {
      render(<QuantComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText(/OpenBB API not connected/i)).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Go to Backends/i })).toBeInTheDocument();
    });
  });
});
