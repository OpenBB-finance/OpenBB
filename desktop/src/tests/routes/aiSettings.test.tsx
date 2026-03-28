/// <reference types="vitest/globals" />
import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import React from "react";
import { vi } from "vitest";
import { Route as AiSettingsRoute } from "../../routes/ai-settings";
import type { AiGatewaySettings } from "../../types/ai";

const getAiSettingsMock = vi.fn();
const updateAiSettingsMock = vi.fn();

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

vi.mock("../../lib/aiApi", () => ({
  getAiSettings: (...args: unknown[]) => getAiSettingsMock(...args),
  updateAiSettings: (...args: unknown[]) => updateAiSettingsMock(...args),
}));

function makeSettings(overrides: Partial<AiGatewaySettings> = {}): AiGatewaySettings {
  return {
    defaultProvider: "ollama",
    defaultMode: "ask",
    retrieval: {
      strategy: "hybrid",
      topK: 8,
      allowRepoSummary: true,
    },
    providers: {
      ollama: {
        enabled: true,
        baseUrl: "http://127.0.0.1:11434/api",
        defaultChatModel: "qwen2.5-coder:1.5b",
        defaultEmbeddingModel: "qwen3-embedding",
        keepAlive: "15m",
        requestTimeoutMs: 45000,
      },
      codex: {
        enabled: true,
        askTransport: "exec",
        agentTransport: "app-server",
        sandbox: "read-only",
        approvalPolicy: "on-request",
      },
      gemini: {
        enabled: true,
        askTransport: "headless",
        agentTransport: "acp",
        sandbox: "read-only",
        approvalPolicy: "default",
      },
    },
    featureFlags: {
      codexAgentEnabled: false,
      geminiAgentEnabled: false,
    },
    ...overrides,
  };
}

describe("AI Settings Route", () => {
  const AiSettingsComponent = AiSettingsRoute.options.component as React.ComponentType;

  beforeEach(() => {
    getAiSettingsMock.mockReset();
    updateAiSettingsMock.mockReset();
    getAiSettingsMock.mockResolvedValue(makeSettings());
    updateAiSettingsMock.mockImplementation(async (settings: AiGatewaySettings) => settings);
  });

  test("renders provider transport details and saves edited ollama settings", async () => {
    render(<AiSettingsComponent />);

    await waitFor(() => {
      expect(screen.getByText(/AI Settings/i)).toBeInTheDocument();
    });

    expect(screen.getByText("app-server")).toBeInTheDocument();
    expect(screen.getByText("headless")).toBeInTheDocument();

    fireEvent.change(screen.getByDisplayValue("15m"), { target: { value: "30m" } });
    fireEvent.change(screen.getByDisplayValue("45000"), { target: { value: "90000" } });
    fireEvent.click(screen.getByRole("button", { name: /Save AI Settings/i }));

    await waitFor(() => {
      expect(updateAiSettingsMock).toHaveBeenCalledWith(
        expect.objectContaining({
          providers: expect.objectContaining({
            ollama: expect.objectContaining({
              keepAlive: "30m",
              requestTimeoutMs: 90000,
            }),
          }),
        }),
      );
    });
  });
});
