/// <reference types="vitest/globals" />
import { render, screen, waitFor, act } from '@testing-library/react';
import { vi } from 'vitest';
import BackendLogsPage from '../../components/BackendLogsPage';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { useSearch } from '@tanstack/react-router';

// Mocks
vi.mock('@tanstack/react-router', () => ({
  useSearch: vi.fn(),
}));
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));
vi.mock('@tauri-apps/api/event', () => ({
  listen: vi.fn(),
}));

describe('BackendLogsPage', () => {
  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(invoke).mockResolvedValue(undefined);
    vi.mocked(useSearch).mockReturnValue({ id: '123' });
  });

  it('renders with a loading message and fetches initial logs', async () => {
    const mockLogs = [
      { process_id: 'backend-123', content: 'Log message 1', timestamp: Date.now() },
      { process_id: 'backend-123', content: 'Log message 2', timestamp: Date.now() },
    ];
    vi.mocked(invoke).mockResolvedValue(mockLogs);
    vi.mocked(listen).mockResolvedValue(() => {});

    await act(async () => {
      render(<BackendLogsPage />);
    });

    await waitFor(() => {
      expect(screen.getByText(/Log message 1/i)).toBeInTheDocument();
      expect(screen.getByText(/Log message 2/i)).toBeInTheDocument();
    });
  });

  it('displays new log messages from the event listener', async () => {
    let eventCallback: (event: any) => void = () => {};
    vi.mocked(listen).mockImplementation((event, callback) => {
      if (event === 'process-output') {
        eventCallback = callback as (event: any) => void;
      }
      return Promise.resolve(() => {});
    });
    vi.mocked(invoke).mockResolvedValue([]);

    await act(async () => {
      render(<BackendLogsPage />);
    });

    await act(async () => {
      eventCallback({
        payload: { processId: 'backend-123', output: 'New log message', timestamp: Date.now() },
      });
    });

    await waitFor(() => {
      expect(screen.getByText(/New log message/i)).toBeInTheDocument();
    });
  });

  it('filters logs for the correct backend ID', async () => {
    let eventCallback: (event: any) => void = () => {};
    vi.mocked(listen).mockImplementation((event, callback) => {
      if (event === 'process-output') {
        eventCallback = callback as (event: any) => void;
      }
      return Promise.resolve(() => {});
    });
    vi.mocked(invoke).mockResolvedValue([]);

    await act(async () => {
      render(<BackendLogsPage />);
    });

    await act(async () => {
      eventCallback({
        payload: { processId: 'backend-456', output: 'Wrong backend log', timestamp: Date.now() },
      });
    });

    expect(screen.queryByText(/Wrong backend log/i)).not.toBeInTheDocument();
  });
});
