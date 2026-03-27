/// <reference types="vitest/globals" />
import { render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as WorkspaceRoute } from "../../routes/workspace";

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

function mockResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

describe("Workspace Route", () => {
  const WorkspaceComponent = WorkspaceRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();
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
      if (url.endsWith("/api/v1/coverage/providers") || url.endsWith("/api/v1/system")) {
        return mockResponse({ results: {} });
      }
      if (url.endsWith("/api/v1/quant_ml/workspace/brief")) {
        return mockResponse({
          status: "ok",
          active_macro_study: {
            study_id: "study-1",
            name: "Growth Monitor",
            objective: "Track growth slowdown.",
            conclusion_summary: "Growth is slowing.",
            linked_assets: ["SPY", "TLT"],
            latest_feature_export: "/tmp/study-1.json",
            latest_attached_report: "/tmp/study-1.html",
          },
          current_strategy_candidate: {
            run_id: "run-1",
            model_name: "lgbm_ranker",
            as_of_date: "2026-03-25",
            feature_lineage: ["study-1", "fs-v1"],
            promotion_readiness: "ready",
            training_window: "2021-01-01 -> 2026-03-25",
            macro_study_links: ["study-1"],
          },
          portfolio_snapshot: {
            run_id: "run-1",
            model_name: "lgbm_ranker",
            vol_ex_ante: 0.12,
            cvar_95: 0.08,
            top_risk_contributors: [{ symbol: "SPY", contribution: 0.31 }],
            blocked_constraints: ["Turnover constraint is blocking execution."],
          },
          ops_issue_queue: [
            {
              id: "issue-1",
              severity: "warning",
              title: "Execution blocked",
              impact: "Orders are blocked.",
              suggested_action: "Review execution blockers.",
              target_route: "/execution",
              target_search: { runId: "run-1" },
              source: "execution",
              status: "open",
            },
          ],
          latest_report: {
            report_id: "report-1",
            title: "Macro report",
            report_type: "macro",
            report_path: "/tmp/report.html",
            created_at: "2026-03-25T00:00:00Z",
          },
          pending_actions: [
            {
              id: "action-1",
              title: "Open Strategy Lab",
              detail: "Review the latest candidate.",
              target_route: "/quant",
              target_search: { runId: "run-1" },
            },
          ],
        });
      }
      return mockResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("renders aggregated workspace brief cards", async () => {
    render(<WorkspaceComponent />);

    await waitFor(() => {
      expect(screen.getByText("Workspace")).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Active Macro Study" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Current Strategy Candidate" })).toBeInTheDocument();
      expect(screen.getByRole("heading", { name: "Portfolio Snapshot" })).toBeInTheDocument();
    });

    expect(screen.getByText("Growth Monitor")).toBeInTheDocument();
    expect(screen.getByText("run-1")).toBeInTheDocument();
    expect(screen.getByText(/Turnover constraint is blocking execution/i)).toBeInTheDocument();
    expect(screen.getByRole("link", { name: "Open Strategy Lab" })).toHaveAttribute("href", "/quant?runId=run-1");
  });
});
