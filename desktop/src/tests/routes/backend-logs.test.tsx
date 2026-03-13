/// <reference types="vitest/globals" />
import { render, screen } from '@testing-library/react';
import { vi } from 'vitest';
import React from 'react';

// Fix: Mock @tanstack/react-router to match the real API
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => (opts: any) => ({
    ...opts,
    options: opts,
  })),
}));

// Mock the BackendLogsPage component
vi.mock('../../components/BackendLogsPage', () => ({
  __esModule: true,
  default: vi.fn(() => <div>Mocked BackendLogsPage</div>),
}));

// Import after mocks so Route uses the mocks
import { Route as BackendLogsRoute } from '../../routes/backend-logs';

describe('BackendLogs Route', () => {
  const BackendLogsWrapperComponent = BackendLogsRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();
    // Clean up body class for each test
    document.body.classList.remove('jupyter-logs-view');
  });

  test('renders BackendLogsWrapper and BackendLogsPage component', () => {
    render(<BackendLogsWrapperComponent />);
    expect(screen.getByText(/Mocked BackendLogsPage/i)).toBeInTheDocument();
  });

  test('adds and removes "jupyter-logs-view" class to body on mount and unmount', () => {
    const { unmount } = render(<BackendLogsWrapperComponent />);
    expect(document.body.classList.contains('jupyter-logs-view')).toBe(true);
    unmount();
    expect(document.body.classList.contains('jupyter-logs-view')).toBe(false);
  });

  test('validates search parameters correctly', () => {
    const validateSearch = BackendLogsRoute.options.validateSearch as (search: Record<string, unknown>) => Record<string, unknown>;
    expect(validateSearch({ id: 'some-id' })).toEqual({ id: 'some-id' });
    expect(validateSearch({})).toEqual({ id: undefined });
  });
});
