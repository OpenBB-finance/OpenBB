/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invalidateMacroCache } from "../../lib/macroApi";
import { Route as MacroRoute } from "../../routes/macro";

const backendMock = vi.fn();

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

vi.mock("../../lib/openbbBackend", () => ({
  resolveOpenBBBackend: () => backendMock(),
  buildOpenBBRequestInit: (init: RequestInit) => init,
  buildOpenBBRequestUrl: (baseUrl: string, path: string) => `${baseUrl}${path}`,
}));

vi.mock("../../components/macro/MacroStudyChart", () => ({
  MacroStudyChart: ({ title }: { title?: string }) => (
    <div data-testid="macro-study-chart">{title ?? "Macro Study Chart"}</div>
  ),
}));

const studyPayload = {
  id: "study-1",
  name: "Labor and Inflation Monitor",
  objective: "Track labor slack, inflation pressure, and policy stance.",
  series_specs: [
    {
      key: "FRED:UNRATE",
      alias: "Unemployment",
      transform_chain: [],
      freq: "M",
      fill: "ffill",
      axis: "left",
      normalize_mode: "raw",
      lag_mode: null,
      display_style: "line",
    },
    {
      key: "FRED:CPIAUCSL",
      alias: "CPI",
      transform_chain: ["yoy"],
      freq: "M",
      fill: "ffill",
      axis: "right",
      normalize_mode: "yoy",
      lag_mode: null,
      display_style: "line",
    },
  ],
  view_specs: [
    { view_id: "explorer", mode: "explorer", title: "Explorer", layout: {} },
    { view_id: "compare", mode: "compare", title: "Compare", layout: {} },
  ],
  notes: "Initial seed study.",
  conclusion: {
    summary: "",
    thesis: "",
    risk_cases: [],
    action_bias: "neutral",
    confidence: null,
    next_checks: [],
  },
  linked_assets: ["SPY", "TLT", "GLD"],
  linked_feature_set_id: null,
  created_at: "2026-03-25T00:00:00Z",
  updated_at: "2026-03-25T00:00:00Z",
};

function jsonResponse(payload: unknown) {
  return Promise.resolve({
    ok: true,
    json: async () => payload,
  });
}

describe("Macro Route", () => {
  const MacroComponent = MacroRoute.options.component as React.ComponentType;
  const fetchMock = vi.fn();

  beforeEach(() => {
    vi.useRealTimers();
    window.history.replaceState({}, "", "/macro");
    invalidateMacroCache();
    backendMock.mockReset();
    backendMock.mockResolvedValue({
      connected: true,
      baseUrl: "http://127.0.0.1:6900",
      source: "stored-url",
      detail: "ok",
    });

    fetchMock.mockReset();
    global.fetch = fetchMock as unknown as typeof fetch;

    fetchMock.mockImplementation((input: RequestInfo | URL, init?: RequestInit) => {
      const url = String(input);
      const method = init?.method ?? "GET";

      if (url.includes("/api/v1/quant_ml/macro/health")) {
        return jsonResponse({
          status: "ok",
          fred_api_key_configured: true,
          macro_db_path: "/tmp/macro.db",
          obs_stats: {},
          feature_stats: {},
          warnings: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/catalog")) {
        return jsonResponse({
          status: "ok",
          items: [
            {
              id: "FRED:UNRATE",
              source: "FRED",
              series_id: "UNRATE",
              title: "Unemployment Rate",
              frequency: "monthly",
              units: "%",
              domain: "labor",
              default_transform: "level",
              publish_lag: 30,
              notes: null,
              active: true,
              tags: ["labor", "fred"],
              last_obs: "2026-02-28",
              stale_days: 10,
              release_frequency: "monthly",
              default_view: "explorer",
              vintage_available: true,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/studies") && method === "GET") {
        return jsonResponse({ status: "ok", items: [studyPayload] });
      }
      if (url.includes("/api/v1/quant_ml/macro/releases/calendar")) {
        return jsonResponse({
          status: "ok",
          items: [
            {
              key: "FRED:UNRATE",
              title: "Unemployment Rate",
              domain: "labor",
              release_frequency: "monthly",
              last_obs: "2026-02-28",
              stale_days: 10,
              estimated_next_release: "2026-04-05",
              vintage_available: true,
            },
          ],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/analysis/compare")) {
        return jsonResponse({
          status: "ok",
          normalization: "raw",
          series: {
            "FRED:UNRATE": {
              meta: { key: "FRED:UNRATE", title: "Unemployment", source: "FRED", transform: "raw" },
              data: [
                { date: "2026-01-31", value: 4.1 },
                { date: "2026-02-28", value: 4.2 },
              ],
              stats: { last: 4.2 },
              status: "ok",
            },
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/analysis/leadlag")) {
        return jsonResponse({
          status: "ok",
          lhs: "FRED:UNRATE",
          rhs: "FRED:CPIAUCSL",
          best_lag: -1,
          best_correlation: 0.42,
          table: [{ lag: -1, correlation: 0.42 }, { lag: 0, correlation: 0.2 }],
          rolling_corr: [{ date: "2026-02-28", value: 0.2 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/analysis/scatter")) {
        return jsonResponse({
          status: "ok",
          lhs: "FRED:UNRATE",
          rhs: "FRED:CPIAUCSL",
          correlation: -0.3,
          slope: -0.5,
          intercept: 3.1,
          points: [{ date: "2026-02-28", x: 4.2, y: 2.8 }],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime?")) {
        return jsonResponse({
          status: "ok",
          latest: {
            date: "2026-02-28",
            risk_on_score: 68,
            inflation_score: 42,
            growth_score: 61,
            liquidity_score: 57,
            credit_stress_score: 35,
          },
          data: [
            {
              date: "2026-01-31",
              risk_on_score: 61,
              inflation_score: 47,
              growth_score: 55,
              liquidity_score: 52,
              credit_stress_score: 38,
            },
            {
              date: "2026-02-07",
              risk_on_score: 63,
              inflation_score: 45,
              growth_score: 57,
              liquidity_score: 54,
              credit_stress_score: 37,
            },
            {
              date: "2026-02-14",
              risk_on_score: 64,
              inflation_score: 44,
              growth_score: 58,
              liquidity_score: 55,
              credit_stress_score: 36,
            },
            {
              date: "2026-02-21",
              risk_on_score: 66,
              inflation_score: 43,
              growth_score: 59,
              liquidity_score: 56,
              credit_stress_score: 35,
            },
            {
              date: "2026-02-28",
              risk_on_score: 68,
              inflation_score: 42,
              growth_score: 61,
              liquidity_score: 57,
              credit_stress_score: 35,
            },
          ],
        });
      }
      if (url.endsWith("/api/v1/quant_ml/macro/regime")) {
        return jsonResponse({
          status: "ok",
          date: "2026-02-28",
          inflation_up: false,
          growth_down: false,
          risk_off_proxy: false,
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/studies/study-1") && method === "PUT") {
        return jsonResponse({ status: "ok", items: [{ ...studyPayload, conclusion: { ...studyPayload.conclusion, summary: "Updated summary" } }] });
      }
      if (url.includes("/api/v1/quant_ml/macro/report")) {
        return jsonResponse({
          status: "ok",
          study_id: "study-1",
          report_path: "C:/reports/study-1.html",
          generated_at: "2026-03-25T01:00:00Z",
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/features/export")) {
        return jsonResponse({
          status: "ok",
          study_id: "study-1",
          artifact_path: "C:/exports/study-1.json",
          exported_at: "2026-03-25T01:00:00Z",
          items: [],
        });
      }

      return jsonResponse({});
    });
  });

  test("renders Macro Lab and loads the seed study", async () => {
    render(<MacroComponent />);

    await waitFor(() => {
      expect(screen.getByRole("heading", { name: "Macro Lab", level: 1 })).toBeInTheDocument();
    });
    expect(screen.getByLabelText(/Study Name/i)).toHaveValue("Labor and Inflation Monitor");
    expect(screen.getByText("Study Basket")).toBeInTheDocument();
    expect(screen.getAllByText("Unemployment Rate").length).toBeGreaterThan(0);
    expect(screen.getByText("Regime Summary")).toBeInTheDocument();
    expect(screen.getByTestId("macro-cycle-level-score")).toHaveTextContent("62.6");
  });

  test("autosaves conclusion edits", async () => {
    render(<MacroComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/Conclusion Summary/i)).toBeInTheDocument();
    });

    vi.useFakeTimers();
    try {
      fireEvent.change(screen.getByLabelText(/Conclusion Summary/i), {
        target: { value: "Updated summary" },
      });

      await act(async () => {
        vi.advanceTimersByTime(1_100);
        await Promise.resolve();
      });

      expect(
        fetchMock.mock.calls.some(([url, init]) =>
          String(url).includes("/api/v1/quant_ml/macro/studies/study-1") &&
          (init as RequestInit | undefined)?.method === "PUT",
        ),
      ).toBe(true);
    } finally {
      vi.useRealTimers();
    }
  });

  test("exports feature lineage and shows the artifact path", async () => {
    render(<MacroComponent />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Export Feature Lineage/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Export Feature Lineage/i }));

    await waitFor(() => {
      expect(screen.getByText("C:/exports/study-1.json")).toBeInTheDocument();
    });
  });

  test("hydrates deep-link search state and syncs view changes back into the URL", async () => {
    window.history.replaceState(
      {},
      "",
      "/macro?studyId=study-1&view=relationship&query=labor&domain=labor&asOfDate=2026-02-15&seriesKey=FRED:BAD",
    );
    const replaceSpy = vi.spyOn(window.history, "replaceState");

    render(<MacroComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/Study Name/i)).toHaveValue("Labor and Inflation Monitor");
      expect(screen.getByLabelText(/Search Catalog/i)).toHaveValue("labor");
      expect(screen.getByLabelText(/Domain/i)).toHaveValue("labor");
      expect(screen.getByLabelText(/As Of Date/i)).toHaveValue("2026-02-15");
      expect(screen.getByText(/Series FRED:BAD is not in the active study basket\./i)).toBeInTheDocument();
      expect(screen.getByText("Lead-Lag Table")).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: "release" }));

    await waitFor(() => {
      const nextUrl = String(replaceSpy.mock.calls.at(-1)?.[2] ?? "");
      expect(nextUrl).toContain("studyId=study-1");
      expect(nextUrl).toContain("view=release");
      expect(nextUrl).toContain("query=labor");
      expect(nextUrl).toContain("domain=labor");
      expect(nextUrl).toContain("asOfDate=2026-02-15");
    });
  });

  test("ignores invalid search params and falls back to the first available study", async () => {
    window.history.replaceState({}, "", "/macro?studyId=missing-study&view=bad-view&asOfDate=2026-99-99");

    render(<MacroComponent />);

    await waitFor(() => {
      expect(screen.getByLabelText(/Study Name/i)).toHaveValue("Labor and Inflation Monitor");
      expect(screen.getByText(/Study missing-study was not found\./i)).toBeInTheDocument();
      expect(screen.getByLabelText(/As Of Date/i)).toHaveValue("");
      expect(screen.getByText("Relationship Lens")).toBeInTheDocument();
    });
  });
});
