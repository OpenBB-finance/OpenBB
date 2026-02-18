/// <reference types="vitest/globals" />
import { act, fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { invoke } from "@tauri-apps/api/core";
import { Route as OpsRoute } from "../../routes/ops";

vi.mock("@tanstack/react-router", () => ({
  createFileRoute: vi.fn(() => (options: { component: React.ComponentType }) => ({
    options: {
      component: options.component,
    },
  })),
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

describe("Ops Route", () => {
  const OpsComponent = OpsRoute.options.component as React.ComponentType;

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
      if (url.endsWith("/api/v1/system")) return mockResponse({ results: {} });
      if (url.endsWith("/api/v1/quant_ml/universe/list")) {
        return mockResponse({ universes: [{ id: "default", has_file: true, count_hint: 2 }] });
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
      expect(calls.some((url) => url.endsWith("/api/v1/quant_ml/ops/status"))).toBe(true);
    });
  });
});

