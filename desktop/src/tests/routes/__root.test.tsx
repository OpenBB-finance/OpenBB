/// <reference types="vitest/globals" />
import { act, render, screen } from "@testing-library/react";
import { vi } from "vitest";
import { RouterProvider, createRouter, useRouter } from "@tanstack/react-router";
import { Route } from "../../routes/__root";
import { EnvironmentCreationProvider } from "../../contexts/EnvironmentCreationContext";

beforeAll(() => {
  Object.defineProperty(window, "matchMedia", {
    writable: true,
    value: vi.fn().mockImplementation((query) => ({
      matches: false,
      media: query,
      onchange: null,
      addListener: vi.fn(),
      removeListener: vi.fn(),
      addEventListener: vi.fn(),
      removeEventListener: vi.fn(),
      dispatchEvent: vi.fn(),
    })),
  });
});

vi.mock("@tanstack/react-router", async () => {
  const actual = await vi.importActual("@tanstack/react-router");
  return {
    ...actual,
    useRouter: vi.fn(),
    useMatch: vi.fn(() => ({ pathname: "/" })),
  };
});

vi.mock("@tauri-apps/api/core", () => ({
  invoke: vi.fn(),
}));

vi.mock("../../components/SystemReadinessBanner", () => ({
  SystemReadinessBanner: () => <div>System Readiness</div>,
}));

function createTestRouter(initialPath = "/") {
  (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({
    state: { location: { pathname: initialPath } },
    navigate: vi.fn(),
  });

  return createRouter({
    routeTree: Route,
    defaultPreload: "intent",
    defaultStaleTime: 0,
  });
}

describe("Root Route", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({
      state: { location: { pathname: "/" } },
      navigate: vi.fn(),
    });
  });

  test("renders root shell without crashing", async () => {
    const router = createTestRouter();
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>,
      );
    });
    expect(screen.getByText(/Copyright/i)).toBeInTheDocument();
    expect(screen.getByText(/System Readiness/i)).toBeInTheDocument();
  });

  test("shows workflow-oriented navigation links", async () => {
    const router = createTestRouter("/");
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>,
      );
    });

    expect(screen.getAllByRole("tab").map((tab) => tab.textContent)).toEqual([
      "Settings",
      "Workspace",
      "Finance Lab",
      "Watchlist",
      "Macro Lab",
      "Strategy Lab",
      "Portfolio & Execution",
      "AI",
      "Ops",
    ]);
  });

  test.each(["/jupyter-logs", "/backend-logs", "/setup", "/installation-progress"])(
    "hides navigation on %s",
    async (path) => {
      const router = createTestRouter(path);
      await act(async () => {
        render(
          <EnvironmentCreationProvider>
            <RouterProvider router={router} />
          </EnvironmentCreationProvider>,
        );
      });
      expect(screen.queryByText(/Settings/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Workspace/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Finance Lab/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Watchlist/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Macro Lab/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Strategy Lab/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Portfolio & Execution/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/AI/i)).not.toBeInTheDocument();
      expect(screen.queryByText(/Ops/i)).not.toBeInTheDocument();
    },
  );

  test("marks Workspace tab active when workspace route is selected", async () => {
    const router = createTestRouter("/workspace");
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>,
      );
    });
    expect(screen.getByRole("tab", { name: /Workspace/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: /Strategy Lab/i })).toHaveAttribute("aria-selected", "false");
  });

  test("maps execution route into the Portfolio & Execution tab", async () => {
    const router = createTestRouter("/execution");
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>,
      );
    });
    expect(screen.getByRole("tab", { name: /Portfolio & Execution/i })).toHaveAttribute("aria-selected", "true");
  });

  test("marks Finance Lab tab active when finance route is selected", async () => {
    const router = createTestRouter("/finance");
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>,
      );
    });
    expect(screen.getByRole("tab", { name: /Finance Lab/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: /Workspace/i })).toHaveAttribute("aria-selected", "false");
  });

  test("marks AI tab active when ai route is selected", async () => {
    const router = createTestRouter("/ai");
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>,
      );
    });
    expect(screen.getByRole("tab", { name: /AI/i })).toHaveAttribute("aria-selected", "true");
    expect(screen.getByRole("tab", { name: /Workspace/i })).toHaveAttribute("aria-selected", "false");
  });
});
