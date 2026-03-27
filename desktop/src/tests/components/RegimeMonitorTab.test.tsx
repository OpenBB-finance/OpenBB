/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";

import { RegimeMonitorTab } from "../../components/quant/RegimeMonitorTab";

vi.mock("recharts", () => ({
  ResponsiveContainer: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  RadarChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  PolarGrid: () => <div />,
  PolarAngleAxis: () => <div />,
  PolarRadiusAxis: () => <div />,
  Radar: () => <div />,
  Tooltip: () => <div />,
  CartesianGrid: () => <div />,
  Legend: () => <div />,
  LineChart: ({ children }: { children: React.ReactNode }) => <div>{children}</div>,
  Line: () => <div />,
  XAxis: () => <div />,
  YAxis: () => <div />,
}));

function mockJsonResponse(payload: unknown, ok = true, status = 200): Response {
  return {
    ok,
    status,
    json: async () => payload,
  } as Response;
}

class MockEventSource {
  static instances: MockEventSource[] = [];

  url: string;

  onopen: ((this: EventSource, ev: Event) => unknown) | null = null;

  onerror: ((this: EventSource, ev: Event) => unknown) | null = null;

  private listeners = new Map<string, Array<(event: MessageEvent) => void>>();

  close = vi.fn();

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    const list = this.listeners.get(type) ?? [];
    if (typeof listener === "function") {
      list.push(listener as (event: MessageEvent) => void);
    }
    this.listeners.set(type, list);
  }

  removeEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    const list = this.listeners.get(type) ?? [];
    if (typeof listener !== "function") {
      return;
    }
    this.listeners.set(
      type,
      list.filter((item) => item !== listener),
    );
  }

  emit(type: string, payload: unknown): void {
    const list = this.listeners.get(type) ?? [];
    const event = { data: JSON.stringify(payload) } as MessageEvent;
    list.forEach((listener) => listener(event));
  }

  triggerOpen(): void {
    this.onopen?.call(this as unknown as EventSource, new Event("open"));
  }

  triggerError(): void {
    this.onerror?.call(this as unknown as EventSource, new Event("error"));
  }
}

describe("RegimeMonitorTab", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    MockEventSource.instances = [];
    vi.stubGlobal("EventSource", MockEventSource as unknown as typeof EventSource);

    global.fetch = vi.fn(async (input: string | URL, init?: RequestInit) => {
      const url = String(input);
      const method = (init?.method ?? "GET").toUpperCase();
      if (url.includes("/api/v1/quant_ml/macro/regime?") && method === "GET") {
        return mockJsonResponse({
          status: "ok",
          data: [
            {
              date: "2026-02-01",
              risk_on_score: 55,
              inflation_score: 52,
              growth_score: 48,
              liquidity_score: 51,
              credit_stress_score: 49,
            },
          ],
          latest: {
            date: "2026-02-01",
            risk_on_score: 55,
            inflation_score: 52,
            growth_score: 48,
            liquidity_score: 51,
            credit_stress_score: 49,
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime/hmm") && method === "GET") {
        return mockJsonResponse({
          status: "ok",
          states: [
            {
              date: "2026-02-01",
              state: 0,
              label: "Transitional",
              probability: [0.7, 0.1, 0.1, 0.1],
            },
          ],
          state_meta: {
            "0": { label: "Transitional", risk_on_score: 50 },
          },
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime/transitions") && method === "GET") {
        return mockJsonResponse({
          status: "ok",
          transitions: [
            {
              date: "2026-02-01",
              axis: "risk_on_score",
              from_score: 40,
              to_score: 55,
              delta: 15,
              direction: "rising",
              severity: "minor",
            },
          ],
          regime_label_history: [{ date: "2026-02-01", label: "Transitional" }],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/alerts") && method === "GET") {
        return mockJsonResponse({
          status: "ok",
          current: [
            {
              rule_id: "credit_stress",
              severity: "warning",
              triggered_at: "2026-02-01T00:00:00Z",
              message: "Credit stress increasing",
              value: 65,
              threshold: 60,
              context: {},
            },
          ],
          history: [],
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime/scheduler/status") && method === "GET") {
        return mockJsonResponse({
          running: true,
          last_market_refresh: "2026-02-01T00:00:00Z",
          last_fred_update: "2026-02-01T01:00:00Z",
          next_market_refresh: "2026-02-01T00:30:00Z",
          next_fred_update: "2026-02-02T01:00:00Z",
        });
      }
      if (url.includes("/api/v1/quant_ml/macro/regime/refresh") && method === "POST") {
        return mockJsonResponse({ status: "ok" });
      }
      return mockJsonResponse({ detail: "not-found" }, false, 404);
    }) as unknown as typeof fetch;
  });

  test("renders regime monitor tab with initial data", async () => {
    await act(async () => {
      render(<RegimeMonitorTab baseUrl="http://127.0.0.1:6900" />);
    });

    await waitFor(() => {
      expect(screen.getByText("Current Regime")).toBeInTheDocument();
      expect(screen.getByText("5-Axis Radar")).toBeInTheDocument();
      expect(screen.getByText("Regime Timeline")).toBeInTheDocument();
      expect(screen.getByText("Recent Transitions")).toBeInTheDocument();
      expect(screen.getByText("Macro Alerts")).toBeInTheDocument();
      expect(screen.getByText(/Scheduler: running/i)).toBeInTheDocument();
    });

    expect(MockEventSource.instances).toHaveLength(1);
    expect(MockEventSource.instances[0]?.url).toContain(
      "/api/v1/quant_ml/macro/regime/stream?interval_sec=60",
    );
  });

  test("applies SSE updates and reconnects after baseUrl change", async () => {
    const { rerender } = render(<RegimeMonitorTab baseUrl="http://127.0.0.1:6900" />);

    await waitFor(() => {
      expect(MockEventSource.instances).toHaveLength(1);
    });

    const first = MockEventSource.instances[0];
    act(() => {
      first.triggerOpen();
      first.emit("scores_update", {
        event_type: "scores_update",
        timestamp: "2026-02-10T00:00:00Z",
        data: {
          date: "2026-02-10",
          risk_on_score: 70,
          inflation_score: 45,
          growth_score: 66,
          liquidity_score: 63,
          credit_stress_score: 30,
        },
        label: "Risk-On / Bull",
      });
    });

    await waitFor(() => {
      expect(screen.getByText("LIVE")).toBeInTheDocument();
      expect(screen.getByText("Risk-On / Bull")).toBeInTheDocument();
    });

    act(() => {
      first.emit("transition", {
        event_type: "transition",
        timestamp: "2026-02-10T00:10:00Z",
        data: {},
        from_label: "Risk-On / Bull",
        to_label: "Risk-Off / Crisis",
      });
    });

    await waitFor(() => {
      expect(screen.getByText("Risk-Off / Crisis")).toBeInTheDocument();
    });

    rerender(<RegimeMonitorTab baseUrl="http://127.0.0.1:7000" />);

    await waitFor(() => {
      expect(first.close).toHaveBeenCalledTimes(1);
      expect(MockEventSource.instances).toHaveLength(2);
      expect(MockEventSource.instances[1]?.url).toContain("http://127.0.0.1:7000");
    });
  });

  test("refresh button triggers refresh endpoint and reloads data", async () => {
    render(<RegimeMonitorTab baseUrl="http://127.0.0.1:6900" />);

    await waitFor(() => {
      expect(screen.getByRole("button", { name: /Refresh Now/i })).toBeInTheDocument();
    });

    fireEvent.click(screen.getByRole("button", { name: /Refresh Now/i }));

    await waitFor(() => {
      const calls = vi.mocked(global.fetch).mock.calls.map((call) => [String(call[0]), call[1]] as const);
      const refreshCalls = calls.filter(([url, init]) =>
        url.includes("/api/v1/quant_ml/macro/regime/refresh") &&
        String(init?.method ?? "GET").toUpperCase() === "POST",
      );
      expect(refreshCalls.length).toBeGreaterThan(0);
    });
  });
});
