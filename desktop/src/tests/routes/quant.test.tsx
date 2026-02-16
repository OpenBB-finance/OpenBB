/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as QuantRoute } from "../../routes/quant";
import { clearCachePrefix } from "../../lib/quantCache";

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
    clearCachePrefix("");
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
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockJsonResponse({
          universes: [
            { id: "default", has_file: true, path: null, count_hint: 2, minimum_required: 0 },
            { id: "sp500", has_file: true, path: "/tmp/sp500.csv", count_hint: 503, minimum_required: 450 },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/universe/resolve")) {
        return mockJsonResponse({
          universe_id: "sp500",
          mode: "train",
          count: 503,
          minimum_required: 450,
          meets_minimum: true,
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
          status: "completed",
          progress: 100,
          stage: "completed",
          created_at: "2026-02-13T00:00:00Z",
          updated_at: "2026-02-13T00:00:10Z",
          logs_tail: ["training started"],
          error: null,
        });
      }
      if (url.includes("/api/v1/quant_ml/model/ic")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          window: 6,
          points: [
            { date: "2026-02-10", ic: 0.1, rolling_ic: 0.1 },
            { date: "2026-02-11", ic: 0.15, rolling_ic: 0.12 },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/model/regime")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          regimes: {
            bull: { count: 10, mean_return: 0.01, sharpe: 1.2, ic: 0.1, turnover: 0.2 },
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/model/shap")) {
        return mockJsonResponse({
          run_id: "run-1",
          model_name: "lgbm_ranker",
          status: "ok",
          summary_points: [],
          dependence_top3: [],
          feature_stability_ts: [],
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

    const trainCall = vi
      .mocked(global.fetch)
      .mock.calls.find((call) => String(call[0]).endsWith("/api/v1/quant_ml/train"));
    expect(trainCall).toBeDefined();
    const trainBody = JSON.parse(String((trainCall?.[1] as RequestInit | undefined)?.body ?? "{}"));
    expect(trainBody.target_mode).toBe("next_open_to_close");
    expect(trainBody.include_macro_features).toBe(true);
    expect(trainBody.model_choice).toBe("dual");
    expect(Array.isArray(trainBody.symbols)).toBe(true);
    expect(trainBody.universe_id).toBeUndefined();
  });

  test("sends universe_id only in universe set mode", async () => {
    await act(async () => {
      render(<QuantComponent />);
    });

    await waitFor(() => {
      expect(screen.getByLabelText(/Universe Set/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByLabelText(/Universe Set/i), {
        target: { value: "sp500" },
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/Resolved 503 symbols/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Start Training/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/train"))).toBe(true);
    });

    const trainCall = vi
      .mocked(global.fetch)
      .mock.calls.find((call) => String(call[0]).endsWith("/api/v1/quant_ml/train"));
    expect(trainCall).toBeDefined();
    const trainBody = JSON.parse(String((trainCall?.[1] as RequestInit | undefined)?.body ?? "{}"));
    expect(trainBody.universe_id).toBe("sp500");
    expect(trainBody.symbols).toBeUndefined();
  });

  test("blocks training when universe resolve fails", async () => {
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
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockJsonResponse({
          universes: [
            { id: "default", has_file: true, path: null, count_hint: 2, minimum_required: 0 },
            { id: "sp500", has_file: true, path: "/tmp/sp500.csv", count_hint: 2, minimum_required: 450 },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/universe/resolve")) {
        return mockJsonResponse(
          {
            detail:
              "invalid_or_undersized_universe_id: sp500; actual_count: 2; minimum_required: 450; hint: run refresh_universes --all --no-validate",
          },
          false,
          400,
        );
      }
      if (url.endsWith("/api/v1/quant_ml/train")) {
        return mockJsonResponse({
          run_id: "run-1",
          status: "queued",
          artifact_root: "/tmp/run-1",
          created_at: "2026-02-13T00:00:00Z",
        });
      }
      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;

    await act(async () => {
      render(<QuantComponent />);
    });

    await waitFor(() => {
      expect(screen.getByLabelText(/Universe Set/i)).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.change(screen.getByLabelText(/Universe Set/i), {
        target: { value: "sp500" },
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/invalid_or_undersized_universe_id/i)).toBeInTheDocument();
    });

    const startButton = screen.getByRole("button", { name: /Start Training/i });
    expect(startButton).toBeDisabled();
    fireEvent.click(startButton);

    const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
    expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/train"))).toBe(false);
  });

  test("loads model diagnostics when run is completed", async () => {
    await act(async () => {
      render(<QuantComponent />);
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Start Training/i })).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Start Training/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/model/ic"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/model/regime"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/model/shap"))).toBe(true);
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
