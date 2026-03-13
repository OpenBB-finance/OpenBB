/// <reference types="vitest/globals" />
import { render, screen, waitFor, fireEvent, act } from '@testing-library/react';
import { vi } from 'vitest';
import React from 'react';

// Mock @tanstack/react-router to match the real API
vi.mock('@tanstack/react-router', () => ({
  useRouter: vi.fn(() => ({
    navigate: vi.fn(),
  })),
  createFileRoute: vi.fn(() => (opts: any) => ({
    ...opts,
    options: opts,
  })),
}));

// Mock @tauri-apps/api/core
import * as tauriCore from '@tauri-apps/api/core';
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

// Mock @tauri-apps/plugin-dialog
import * as tauriDialog from '@tauri-apps/plugin-dialog';
vi.mock('@tauri-apps/plugin-dialog', () => ({
  confirm: vi.fn(),
}));

// Mock @tauri-apps/api/event
import * as tauriEvent from '@tauri-apps/api/event';
vi.mock('@tauri-apps/api/event', () => ({
  listen: vi.fn(() => Promise.resolve(() => {})),
}));

// Import after mocks so Route uses the mocks
import { Route as UninstallRoute } from '../../routes/uninstall';

describe('UninstallPage Route', () => {
  const UninstallComponent = UninstallRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();

    (tauriCore.invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'get_installation_directory') return Promise.resolve('/mock/install/dir');
      if (cmd === 'get_userdata_directory') return Promise.resolve('/mock/user/data/dir');
      if (cmd === 'get_settings_directory') return Promise.resolve('/mock/settings/dir');
      if (cmd === 'uninstall_application') return Promise.resolve(undefined);
      if (cmd === 'app.exit') return Promise.resolve(undefined); // <-- ADD THIS LINE
      return Promise.resolve(undefined);
    });
  });

  it('renders Uninstall component and shows directory paths', async () => {
    render(<UninstallComponent />);
    expect(screen.getByText(/Uninstall Application & Data/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByText(/mock\/install\/dir/i)).toBeInTheDocument();
      expect(screen.getByText(/mock\/user\/data\/dir/i)).toBeInTheDocument();
      expect(screen.getByText(/mock\/settings\/dir/i)).toBeInTheDocument();
    });
  });

  it('allows toggling "Remove user data" checkbox', async () => {
    render(<UninstallComponent />);
    const checkbox = await screen.findByLabelText(/Remove user data/i);
    expect(checkbox).not.toBeChecked();
    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();
  });

  it('allows toggling "Remove application settings" checkbox', async () => {
    render(<UninstallComponent />);
    const checkbox = await screen.findByLabelText(/Remove application settings/i);
    expect(checkbox).not.toBeChecked();
    fireEvent.click(checkbox);
    expect(checkbox).toBeChecked();
  });

  it('starts uninstallation when "Uninstall" is clicked and user confirms', async () => {
    (tauriDialog.confirm as any).mockResolvedValueOnce(true);

    render(<UninstallComponent />);
    fireEvent.click(screen.getByText('Uninstall'));

    await waitFor(() => expect(tauriDialog.confirm).toHaveBeenCalledWith(
      'This action cannot be undone.\n\nClick OK to continue.',
      { title: 'Confirm Uninstall', kind: 'warning' }
    ));
    await waitFor(() => expect(screen.getByText(/Uninstalling\.\.\./i)).toBeInTheDocument());
    await waitFor(() => expect(tauriCore.invoke).toHaveBeenCalledWith('uninstall_application', {
      removeUserData: false,
      removeSettings: false,
    }));
    await waitFor(() => expect(screen.getByText(/Uninstallation complete! Closing application.../i)).toBeInTheDocument());
  });

  it('does not start uninstallation if user cancels confirmation', async () => {
    (tauriDialog.confirm as any).mockResolvedValueOnce(false);

    render(<UninstallComponent />);
    fireEvent.click(screen.getByText('Uninstall'));

    await waitFor(() => expect(tauriDialog.confirm).toHaveBeenCalledWith(
      'This action cannot be undone.\n\nClick OK to continue.',
      { title: 'Confirm Uninstall', kind: 'warning' }
    ));
    expect(tauriCore.invoke).not.toHaveBeenCalledWith('uninstall_application', expect.any(Object));
    expect(screen.queryByText(/Starting uninstallation.../i)).not.toBeInTheDocument();
  });

  it('displays error message on uninstallation failure', async () => {
    (tauriDialog.confirm as any).mockResolvedValueOnce(true);
    (tauriCore.invoke as any).mockImplementation((cmd: string) => {
      if (cmd === 'uninstall_application') return Promise.reject(new Error('Uninstall failed'));
      if (cmd === 'get_installation_directory') return Promise.resolve('/mock/install/dir');
      if (cmd === 'get_userdata_directory') return Promise.resolve('/mock/user/data/dir');
      if (cmd === 'get_settings_directory') return Promise.resolve('/mock/settings/dir');
      return Promise.resolve(undefined);
    });

    render(<UninstallComponent />);
    fireEvent.click(screen.getByText('Uninstall'));

    // Wait for the error dialog to be called with the correct error message
    await waitFor(() => {
      const calls = (tauriDialog.confirm as any).mock.calls;
      expect(
        calls.some(
          ([msg, opts]: [string, { title: string; kind: string }]) =>
            msg === 'An error occurred during uninstallation: Error: Uninstall failed' &&
            opts &&
            opts.title === 'Uninstallation Error' &&
            opts.kind === 'error'
        )
      ).toBe(true);
    });

    // Optionally, check that the progress dialog is closed
    expect(screen.queryByText(/Uninstalling\.\.\./i)).not.toBeInTheDocument();
  });

  it('shows progress updates during uninstallation', async () => {
    (tauriDialog.confirm as any).mockResolvedValueOnce(true);

    let handler: ((event: any) => void) | undefined;
    (tauriEvent.listen as any).mockImplementationOnce((_: any, cb: (event: any) => void) => {
      handler = cb;
      return Promise.resolve(() => {});
    });

    render(<UninstallComponent />);
    fireEvent.click(screen.getByText('Uninstall'));

    await waitFor(() => expect(screen.getByText(/Starting uninstallation.../i)).toBeInTheDocument());

    // Simulate progress events
    act(() => {
      if (handler) handler({ payload: 'Step 1: Cleaning files...' });
    });
    await waitFor(() => expect(screen.getByText(/Step 1: Cleaning files.../i)).toBeInTheDocument());

    act(() => {
      if (handler) handler({ payload: 'Step 2: Removing directories...' });
    });
    await waitFor(() => expect(screen.getByText(/Step 2: Removing directories.../i)).toBeInTheDocument());
  });
});
