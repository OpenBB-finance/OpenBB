/// <reference types="vitest/globals" />
import { render, screen, act } from '@testing-library/react';
import { vi } from 'vitest';
import { Route } from '../../routes/__root';
import { RouterProvider, createRouter, useRouter } from '@tanstack/react-router';
import { EnvironmentCreationProvider } from '../../contexts/EnvironmentCreationContext';

beforeAll(() => {
  Object.defineProperty(window, 'matchMedia', {
    writable: true,
    value: vi.fn().mockImplementation(query => ({
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

// Mock @tanstack/react-router
vi.mock('@tanstack/react-router', async () => {
  const actual = await vi.importActual('@tanstack/react-router');
  return {
    ...actual,
    useRouter: vi.fn(),
    useMatch: vi.fn(() => ({ pathname: '/' })),
  };
});

// Mock @tauri-apps/api/core
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

describe('Root Route', () => {
  const createTestRouter = (initialPath = '/') => {
    (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({
      state: { location: { pathname: initialPath } },
      navigate: vi.fn(),
    });

    const router = createRouter({
      routeTree: Route,
      defaultPreload: 'intent',
      defaultStaleTime: 0,
    });
    return router;
  };

  beforeEach(() => {
    vi.clearAllMocks();
    // Reset useRouter mock to its default for each test
    (useRouter as ReturnType<typeof vi.fn>).mockReturnValue({
      state: { location: { pathname: '/' } },
      navigate: vi.fn(),
    });
  });

  test('renders Root component without crashing', async () => {
    const router = createTestRouter();
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>
      );
    });
    expect(screen.getByText(/Copyright © 2025 OpenBB Inc./i)).toBeInTheDocument();
  });

  test('displays navigation links when not in hidden views', async () => {
    const router = createTestRouter('/'); // Explicitly set path
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>
      );
    });
    expect(screen.getByText(/Backends/i)).toBeInTheDocument();
    expect(screen.getByText(/Environments/i)).toBeInTheDocument();
    expect(screen.getByText(/API Keys/i)).toBeInTheDocument();
  });

  test('hides navigation links in Jupyter logs view', async () => {
    const router = createTestRouter('/jupyter-logs'); // Explicitly set path
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>
      );
    });
    expect(screen.queryByText(/Backends/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Environments/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/API Keys/i)).not.toBeInTheDocument();
  });

  test('hides navigation links in Backend logs view', async () => {
    const router = createTestRouter('/backend-logs'); // Explicitly set path
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>
      );
    });
    expect(screen.queryByText(/Backends/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Environments/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/API Keys/i)).not.toBeInTheDocument();
  });

  test('hides navigation links in Setup view', async () => {
    const router = createTestRouter('/setup'); // Explicitly set path
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>
      );
    });
    expect(screen.queryByText(/Backends/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Environments/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/API Keys/i)).not.toBeInTheDocument();
  });

  test('hides navigation links in Installation Progress view', async () => {
    const router = createTestRouter('/installation-progress'); // Explicitly set path
    await act(async () => {
      render(
        <EnvironmentCreationProvider>
          <RouterProvider router={router} />
        </EnvironmentCreationProvider>
      );
    });
    expect(screen.queryByText(/Backends/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/Environments/i)).not.toBeInTheDocument();
    expect(screen.queryByText(/API Keys/i)).not.toBeInTheDocument();
  });
});
