/// <reference types="vitest/globals" />

import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import { vi } from 'vitest';
import InstallationProgress from '../../routes/installation-progress';
import { invoke } from '@tauri-apps/api/core';
import { listen } from '@tauri-apps/api/event';
import { useNavigate } from '@tanstack/react-router';

// --- Mocks ---
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: () => () => ({}),
  useNavigate: vi.fn(),
  useSearch: vi.fn(),
  useRouter: vi.fn(() => ({
    invalidate: vi.fn(),
  })),
}));
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));
vi.mock('@tauri-apps/api/event', () => ({
  listen: vi.fn(),
}));
vi.mock('../../components/InstallComponents', () => ({
  PythonVersionSelector: ({ onSelectVersion, onNext }: { onSelectVersion: (v: string) => void; onNext: () => void }) => (
    <div>
      <p>Select Python Version</p>
      <button onClick={() => onSelectVersion('3.10')}>Select Python 3.10</button>
      <button onClick={onNext}>Next Python Step</button>
    </div>
  ),
  ExtensionSelector: ({ onInstallExtensions, onSkip }: { onInstallExtensions: (exts: string[]) => void; onSkip: () => void }) => (
    <div>
      <p>Select Extensions</p>
      <button onClick={() => onInstallExtensions(['openbb-finance'])}>Install</button>
      <button onClick={onSkip}>Skip</button>
    </div>
  ),
}));


type InstallProgressPayload = Record<string, unknown>;
type InstallProgressHandler = (event: { payload: InstallProgressPayload }) => void;

describe('InstallationProgressPage', () => {
  const mockNavigate = vi.fn();
  const originalLocation = window.location;
  let installProgressHandler: InstallProgressHandler | undefined;

  beforeAll(() => {
    Object.defineProperty(window, 'location', {
      configurable: true,
      value: {
        ...window.location,
        href: '',
        reload: vi.fn(),
        assign: vi.fn(),
        replace: vi.fn(),
      },
    });
  });

  afterAll(() => {
    Object.defineProperty(window, 'location', {
      writable: true,
      value: originalLocation,
    });
  });

  beforeEach(() => {
    vi.clearAllMocks();
    window.location.href = '';
    (invoke as unknown as { mockClear: () => void }).mockClear();
    (listen as unknown as { mockClear: () => void }).mockClear();
    (useNavigate as unknown as { mockReturnValue: (v: unknown) => void }).mockReturnValue(mockNavigate);

    (invoke as unknown as { mockResolvedValue: (v: unknown) => void }).mockResolvedValue(undefined);

    Object.defineProperty(window, 'URLSearchParams', {
      writable: true,
      value: class {
        private params: Record<string, string> = {
          directory: '/mock/install/dir',
          userDataDir: '/mock/user/data/dir',
        };
        get(key: string) {
          return this.params[key] ?? null;
        }
        append(key: string, value: string) {
          this.params[key] = value;
        }
        toString() {
          return Object.entries(this.params)
            .map(([k, v]) => `${encodeURIComponent(k)}=${encodeURIComponent(v)}`)
            .join('&');
        }
      },
    });

    (listen as unknown as { mockImplementation: (fn: unknown) => void }).mockImplementation(
      async (event: string, handler: InstallProgressHandler) => {
        if (event === 'install-progress') {
          installProgressHandler = handler;
        }
        return vi.fn();
      }
    );
  });

  function triggerProgress(payload: InstallProgressPayload): void {
    if (typeof installProgressHandler === 'function') {
      act(() => {
        installProgressHandler!({ payload });
      });
    } else {
      throw new Error('installProgressHandler is not set');
    }
  }

  test('renders initial loading state', async () => {
    await act(async () => {
      render(<InstallationProgress />);
    });
    // Wrap assertions in waitFor to ensure state updates are flushed
    await waitFor(() => {
      expect(screen.getByText(/Installation & Setup/i)).toBeInTheDocument();
    });
  });

  test('transitions to downloading phase via event', async () => {
    act(() => {
      render(<InstallationProgress />);
    });
    act(() => {
      triggerProgress({ step: 'download', progress: 0.1, message: 'Downloading Miniforge' });
    });
    await waitFor(() => expect(screen.getByText(/Downloading Miniforge/i)).toBeInTheDocument());
  });

  test('transitions to version selection phase after install-conda completes', async () => {
    (invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.resolve(undefined);
      return Promise.resolve(undefined);
    });

    act(() => {
      render(<InstallationProgress />);
    });
    act(() => {
      triggerProgress({ step: 'install', progress: 1, message: 'Miniforge installation completed' });
    });

    await waitFor(() => {
      expect(screen.getAllByText(/Select Python Version/i).length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/Select Python 3.10/i)).toBeInTheDocument();
  });

  test('transitions to extension selection phase after setup_python_environment completes', async () => {
    (invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.resolve(undefined);
      if (cmd === 'setup_python_environment') return Promise.resolve(undefined);
      return Promise.resolve(undefined);
    });

    act(() => {
      render(<InstallationProgress />);
    });

    // Simulate Miniforge install completion, which triggers Python version selection
    act(() => {
      triggerProgress({ step: 'install', progress: 1, message: 'Miniforge installation completed' });
    });

    // Wait for Python version selection UI
    await waitFor(() => {
      expect(screen.getAllByText(/Select Python Version/i).length).toBeGreaterThan(0);
    });

    // Select a version and proceed
    act(() => {
      fireEvent.click(screen.getByText('Select Python 3.10'));
      fireEvent.click(screen.getByText('Next Python Step'));
    });

    // Simulate backend reporting environment setup complete, which triggers extension selection
    act(() => {
      triggerProgress({ step: 'config', progress: 1, message: 'environment set up successfully' });
    });

    // Wait for the unique "Install" button, which only appears in extension selection phase
    await screen.findByRole('button', { name: 'Install' });

    // Optionally, assert that the extension selector container is present
    expect(screen.getByRole('button', { name: 'Install' })).toBeInTheDocument();
    expect(screen.getByRole('button', { name: 'Skip' })).toBeInTheDocument();
  });

  test('completes installation when extensions are installed', async () => {
    (invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.resolve(undefined);
      if (cmd === 'setup_python_environment') return Promise.resolve(undefined);
      if (cmd === 'install_extensions') return Promise.resolve(undefined);
      return Promise.resolve(undefined);
    });

    render(<InstallationProgress />);
    triggerProgress({ step: 'install', progress: 1, message: 'Miniforge installation completed' });
    await waitFor(() => {
      expect(screen.getAllByText(/Select Python Version/i).length).toBeGreaterThan(0);
    });
    act(() => {
      fireEvent.click(screen.getByText('Select Python 3.10'));
      fireEvent.click(screen.getByText('Next Python Step'));
    });

    triggerProgress({ step: 'config', progress: 1, message: 'environment set up successfully' });

    await waitFor(() => expect(screen.getByText('Install')).toBeInTheDocument());
    act(() => {
      fireEvent.click(screen.getByText('Install'));
    });

    triggerProgress({ step: 'complete', progress: 1, message: 'Installation completed successfully' });

    await waitFor(() => expect(screen.getByText(/Installation completed successfully!/i)).toBeInTheDocument());

    act(() => {
      fireEvent.click(screen.getByText('Done'));
    });

    await waitFor(() => expect(window.location.href).toBe('/environments?directory=%2Fmock%2Finstall%2Fdir&userDataDir=%2Fmock%2Fuser%2Fdata%2Fdir'));
  });

  test('completes installation when extensions are skipped', async () => {
    (invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.resolve(undefined);
      if (cmd === 'setup_python_environment') return Promise.resolve(undefined);
      return Promise.resolve(undefined);
    });

    render(<InstallationProgress />);
    triggerProgress({ step: 'install', progress: 1, message: 'Miniforge installation completed' });
    await waitFor(() => {
      expect(screen.getAllByText(/Select Python Version/i).length).toBeGreaterThan(0);
    });
    act(() => {
      fireEvent.click(screen.getByText('Select Python 3.10'));
      fireEvent.click(screen.getByText('Next Python Step'));
    });

    triggerProgress({ step: 'config', progress: 1, message: 'environment set up successfully' });

    await waitFor(() => expect(screen.getByText('Skip')).toBeInTheDocument());
    act(() => {
      fireEvent.click(screen.getByText('Skip'));
    });

    await waitFor(() => expect(screen.getByText(/Installation completed successfully!/i)).toBeInTheDocument());

    act(() => {
      fireEvent.click(screen.getByText('Done'));
    });

    await waitFor(() => expect(window.location.href).toBe('/environments?directory=%2Fmock%2Finstall%2Fdir&userDataDir=%2Fmock%2Fuser%2Fdata%2Fdir'));
  });

  test('displays error message on installation failure', async () => {
    (invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.reject(new Error('Conda install failed'));
      return Promise.resolve(undefined);
    });

    act(() => {
      render(<InstallationProgress />);
    });
    act(() => {
      triggerProgress({ step: 'install', progress: 0.5, message: 'Conda install failed' });
    });

    await waitFor(() => {
      expect(screen.getAllByText(/Installation failed/i).length).toBeGreaterThan(0);
    });
    expect(screen.getByText(/Try Again/i)).toBeInTheDocument();
  });

  test('handles cancellation during installation', async () => {
    let cancelPromiseResolve: (() => void) | undefined;

    (invoke as unknown as { mockImplementation: (fn: unknown) => void }).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') {
        // Simulate a long-running install
        return new Promise(() => {});
      }
      if (cmd === 'abort_installation') {
        return new Promise<void>((resolve) => {
          cancelPromiseResolve = resolve;
        });
      }
      return Promise.resolve(undefined);
    });

    act(() => {
      render(<InstallationProgress />);
    });

    // Simulate backend progress to get to downloading phase
    act(() => {
      triggerProgress({ step: 'downloading', progress: 0.1, message: 'Downloading Miniforge' });
    });

    // Wait for the Cancel button to appear
    await waitFor(() => expect(screen.getByText('Cancel')).toBeInTheDocument());

    // Click Cancel
    act(() => {
      fireEvent.click(screen.getByText('Cancel'));
    });

    // Wait for the Cancelling... state
    await waitFor(() => expect(screen.getByText(/Cancelling/i)).toBeInTheDocument());

    // Resolve the abort_installation promise
    act(() => {
      if (!cancelPromiseResolve) throw new Error('cancelPromiseResolve not set');
      cancelPromiseResolve();
    });

    // Simulate backend sending the cancellation progress event
    act(() => {
      triggerProgress({ step: 'cancelled', progress: 1, message: 'Installation cancelled' });
    });

    // Wait for the "Installation cancelled" message and "Return to Setup" button
    await waitFor(() => expect(screen.getByText('Installation cancelled')).toBeInTheDocument());
    const returnBtn = screen.getByText('Return to Setup');
    expect(returnBtn).toBeInTheDocument();

    // Click "Return to Setup" to trigger navigation
    act(() => {
      fireEvent.click(returnBtn);
    });

    // Now navigation should be called
    expect(mockNavigate).toHaveBeenCalledWith({ to: '/setup' });
  });

  test('displays "Installation cancelled" message', async () => {
    let cancelPromiseResolve: (() => void) | undefined;

    (invoke as unknown as { mockImplementation: (fn: unknown) => void }).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') {
        return new Promise(() => {});
      }
      if (cmd === 'abort_installation') {
        return new Promise<void>((resolve) => {
          cancelPromiseResolve = resolve;
        });
      }
      return Promise.resolve(undefined);
    });

    act(() => {
      render(<InstallationProgress />);
    });
    act(() => {
      triggerProgress({ step: 'downloading', progress: 0.1, message: 'Downloading Miniforge' });
    });
    await waitFor(() => expect(screen.getByText(/Downloading Miniforge/i)).toBeInTheDocument());

    act(() => {
      fireEvent.click(screen.getByText('Cancel'));
    });

    await waitFor(() => expect(screen.getByText(/Cancelling/i)).toBeInTheDocument());

    act(() => {
      if (!cancelPromiseResolve) throw new Error('cancelPromiseResolve not set');
      cancelPromiseResolve();
    });

    act(() => {
      triggerProgress({ step: 'cancelled', progress: 1, message: 'Installation cancelled' });
    });

    await waitFor(() => expect(screen.getByText(/Installation cancelled/i)).toBeInTheDocument());
  });

  test('handles "Continue Anyway" on error', async () => {
    (invoke as unknown as { mockImplementation: (fn: unknown) => void }).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.reject(new Error('Conda install failed'));
      return Promise.resolve(undefined);
    });

    render(<InstallationProgress />);
    triggerProgress({ step: 'install', progress: 0.5, message: 'Conda install failed' });

    await waitFor(() => {
      expect(screen.getAllByText(/Installation failed/i).length).toBeGreaterThan(0);
    });

    act(() => {
      fireEvent.click(screen.getByText('Continue Anyway'));
    });
    await waitFor(() => expect(window.location.href).toBe('/environments?directory=%2Fmock%2Finstall%2Fdir&userDataDir=%2Fmock%2Fuser%2Fdata%2Fdir'));
  });

  test('handles "Try Again" on error', async () => {
    (invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'install_conda') return Promise.reject(new Error('Conda install failed'));
      return Promise.resolve(undefined);
    });

    act(() => {
      render(<InstallationProgress />);
    });
    act(() => {
      triggerProgress({ step: 'install', progress: 0.5, message: 'Conda install failed' });
    });

    await waitFor(() => {
      expect(screen.getAllByText(/Installation failed/i).length).toBeGreaterThan(0);
    });

    // Wait for the "Try Again" button to be available before clicking
    await waitFor(() => {
      expect(screen.getByText('Try Again')).toBeInTheDocument();
    });

    act(() => {
      fireEvent.click(screen.getByText('Try Again'));
    });
    expect(window.location.href).toBe('/setup');
  });
});
