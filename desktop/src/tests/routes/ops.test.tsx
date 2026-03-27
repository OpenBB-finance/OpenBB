/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as OpsRoute } from "../../routes/ops";

const openPathSafelyMock = vi.fn();

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(() => (options: { component: React.ComponentType }) => ({
    options: {
      component: options.component,
    },
  })),
  useNavigate: vi.fn(() => vi.fn()),
}));

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

vi.mock("@tauri-apps/plugin-opener", () => ({
  openPath: vi.fn(() => Promise.resolve()),
}));

vi.mock("../../lib/pathOpener", () => ({
  openPathSafely: (...args: unknown[]) => openPathSafelyMock(...args),
}));

function mockResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("Ops Route", () => {
  const OpsComponent = OpsRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();
    openPathSafelyMock.mockResolvedValue(undefined);
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
    if (url.endsWith("/api/v1/coverage/providers") || url.endsWith("/api/v1/system")) return mockResponse({ results: {} });
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockResponse({ universes: [{ id: "default", has_file: true, count_hint: 2 }] });
      }
      if (url.endsWith("/api/v1/quant_ml/ops/issues?limit=8")) {
        return mockResponse({
          items: [
            {
              id: "issue-1",
              severity: "warning",
              title: "Execution handoff is blocked",
              impact: "Orders cannot be submitted.",
              suggested_action: "Open execution and resolve the blocker.",
              target_route: "/execution",
              target_search: { runId: "run-1", modelName: "lgbm_ranker" },
              source: "execution",
              status: "open",
            },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/ops/status")) {
        return mockResponse({
          status: "ok",
          generated_at: "2026-02-16T00:00:00Z",
          jobs: [],
          latest_publish: {},
          versions: {},
          latest_runs: [],
          macro_health: {},
        });
      }
      if (url.endsWith("/api/v1/quant_ml/data-quality/latest")) {
        return mockResponse({
          qc_status: "NORMAL",
          gate_name: "gold_gate",
          as_of_date: "2026-02-16",
          checks: [],
          summary: {},
        });
      }
      if (url.includes("/api/v1/quant_ml/data-quality/history")) {
        return mockResponse({ items: [{ qc_status: "NORMAL", checks: [], summary: {} }] });
      }
      if (url.includes("/api/v1/quant_ml/model-registry/champion")) {
        return mockResponse({ alias: "champion", model_name: "lgbm_ranker", model_version: "1.0.0", metrics: {} });
      }
      if (url.includes("/api/v1/quant_ml/model-registry/challenger")) {
        return mockResponse({ alias: "challenger", model_name: "catboost_ranker", model_version: "0.9.0", metrics: {} });
      }
      if (url.includes("/api/v1/quant_ml/model-registry/history")) {
        return mockResponse({ items: [] });
      }
      if (url.includes("/api/v1/quant_ml/reports/latest")) {
        return mockResponse({ item: { report_type: "ops", report_path: "/tmp/ops.html", status: "ok", summary: {} } });
      }
      if (url.includes("/api/v1/quant_ml/reports/history")) {
        return mockResponse({
          items: [
            {
              id: "report-1",
              run_id: "run-1",
              report_type: "ops",
              report_path: "/tmp/ops.html",
              status: "ok",
              title: "Ops report",
              symbols: ["AAPL"],
              summary: {},
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/notifications/history")) {
        return mockResponse({ items: [] });
      }
      if (url.includes("/api/v1/quant_ml/macro/studies")) {
        return mockResponse({
          status: "ok",
          items: [
            {
              id: "study-1",
              name: "Growth Monitor",
              objective: "Monitor macro trend",
              series_specs: [],
              view_specs: [],
              notes: "",
              conclusion: {
                summary: "",
                thesis: "",
                risk_cases: [],
                action_bias: "",
                next_checks: [],
              },
              linked_assets: ["AAPL"],
              linked_reports: [],
            },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/scheduler/status")) {
        return mockResponse({
          timezone: "Asia/Seoul",
          market_schedule: { run_phase: "post_close", primary_calendar: "XNYS" },
          expected_jobs: ["daily_close"],
          jobs: [],
          macro_scheduler: {},
        });
      }
      if (url.includes("/api/v1/quant_ml/experiments/list")) {
        return mockResponse({ items: [{ run_id: "run-1", model_type: "lgbm_ranker", hyperparameters: {}, feature_set: {}, performance: {} }] });
      }
      if (url.endsWith("/api/v1/quant_ml/experiments/run-1")) {
        return mockResponse({ run_id: "run-1", model_type: "lgbm_ranker", hyperparameters: {}, feature_set: {}, performance: {} });
      }
      return mockResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("loads ops status and allows refresh", async () => {
    await act(async () => {
      render(<OpsComponent />);
    });

    await waitFor(() => {
      expect(screen.getByText("Ops")).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Refresh/i }));
    });

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => String(call[0]));
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/ops/issues?limit=8"))).toBe(true);
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/scheduler/status"))).toBe(true);
      expect(calls.some((url) => url.includes("/api/v1/quant_ml/reports/history"))).toBe(true);
    });
  });

  test("shows an inline fallback error when report opening fails in web mode", async () => {
    openPathSafelyMock.mockRejectedValueOnce(new Error("Browser blocked the open request. Use Copy Path instead."));

    await act(async () => {
      render(<OpsComponent />);
    });

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Open Report/i })).toBeInTheDocument();
    });

    await act(async () => {
      fireEvent.click(screen.getByRole("button", { name: /Open Report/i }));
    });

    await waitFor(() => {
      expect(screen.getByText(/Browser blocked the open request/i)).toBeInTheDocument();
      expect(screen.getByText("/tmp/ops.html")).toBeInTheDocument();
      expect(screen.getByRole("button", { name: /Copy Path/i })).toBeInTheDocument();
    });
  });
});
