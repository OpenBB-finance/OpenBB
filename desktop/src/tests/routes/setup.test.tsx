/// <reference types="vitest/globals" />
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { vi } from 'vitest';
import React from 'react';

// Properly mock @tanstack/react-router
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => (opts: any) => ({
    ...opts,
    options: opts,
  })),
  useNavigate: vi.fn(),
}));

import { invoke } from '@tauri-apps/api/core';
import { useNavigate } from '@tanstack/react-router';
import { confirm } from '@tauri-apps/plugin-dialog';

// Mock @tauri-apps/api/core
vi.mock('@tauri-apps/api/core', () => ({
  invoke: vi.fn(),
}));

// Mock @tauri-apps/plugin-dialog
vi.mock('@tauri-apps/plugin-dialog', () => ({
  confirm: vi.fn(),
}));

// Import after mocks so Route uses the mocks
import { Route as SetupRoute } from '../../routes/setup';

describe('SetupPage Route', () => {
  const mockNavigate = vi.fn();
  const SetupComponent = SetupRoute.options.component as React.ComponentType;

  beforeEach(() => {
    vi.clearAllMocks();
    vi.mocked(useNavigate).mockReturnValue(mockNavigate);
    vi.mocked(invoke).mockClear();
    vi.mocked(confirm).mockClear();

    vi.mocked(invoke).mockImplementation((cmd) => {
      if (cmd === 'get_home_directory') return Promise.resolve('/mock/home');
      if (cmd === 'check_directory_exists') return Promise.resolve(false);
      if (cmd === 'install_to_directory') return Promise.resolve(undefined);
      if (cmd === 'select_directory') return Promise.resolve('/mock/selected/dir');
      if (cmd === 'quit_application') return Promise.resolve(undefined);
      return Promise.resolve(undefined);
    });
  });

  it('renders Setup component and shows default directories', async () => {
    render(<SetupComponent />);
    expect(screen.getByText(/Installation & Setup/i)).toBeInTheDocument();
    await waitFor(() => {
      expect(screen.getByDisplayValue('/mock/home/OpenBB')).toBeInTheDocument();
      expect(screen.getByDisplayValue('/mock/home/OpenBBUserData')).toBeInTheDocument();
    });
  });

  it('allows changing installation directory via input', async () => {
    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    const installDirInput = screen.getByRole('textbox', { name: /Installation Directory/i });
    fireEvent.change(installDirInput, { target: { value: '/custom/install' } });
    expect(installDirInput).toHaveValue('/custom/install');
  });

  it('allows changing user data directory via input', async () => {
    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBBUserData'));
    const userDataDirInput = screen.getByRole('textbox', { name: /User Data Directory/i });
    fireEvent.change(userDataDirInput, { target: { value: '/custom/user/data' } });
    expect(userDataDirInput).toHaveValue('/custom/user/data');
  });

  it('browses for installation directory', async () => {
    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    const installDirButton = screen.getByRole('button', { name: /browse for installation directory/i });
    fireEvent.click(installDirButton);
    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('select_directory', { prompt: 'Select Installation Directory' })
    );
    await waitFor(() => expect(screen.getByDisplayValue('/mock/selected/dir')).toBeInTheDocument());
  });

  it('browses for user data directory', async () => {
    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBBUserData'));
    const userDataDirButton = screen.getByRole('button', { name: /browse for user data directory/i });
    fireEvent.click(userDataDirButton);
    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('select_directory', { prompt: 'Select User Data Directory' })
    );
    await waitFor(() => expect(screen.getByDisplayValue('/mock/selected/dir')).toBeInTheDocument());
  });

  it('starts installation when "Begin Installation" is clicked and directories do not exist', async () => {
    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    fireEvent.click(screen.getByText(/Begin Installation/i));
    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('check_directory_exists', { path: '/mock/home/OpenBB' })
    );
    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('install_to_directory', {
        directory: '/mock/home/OpenBB',
        userDataDirectory: '/mock/home/OpenBBUserData',
      })
    );
    expect(mockNavigate).toHaveBeenCalledWith({
      to: '/installation-progress',
      search: { directory: '/mock/home/OpenBB', userDataDir: '/mock/home/OpenBBUserData' },
    });
  });

  it('prompts for overwrite if installation directory exists and user confirms', async () => {
    vi.mocked(invoke).mockImplementation((cmd) => {
      if (cmd === 'check_directory_exists') return Promise.resolve(true);
      if (cmd === 'get_home_directory') return Promise.resolve('/mock/home');
      return Promise.resolve(undefined);
    });
    vi.mocked(confirm).mockResolvedValueOnce(true);

    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    fireEvent.click(screen.getByText(/Begin Installation/i));
    await waitFor(() =>
      expect(confirm).toHaveBeenCalledWith(
        "Target destination already exists.\n\nDo you want to overwrite?\n\n",
        { title: "Overwrite Installation Directory?", kind: "warning" }
      )
    );
    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('install_to_directory', expect.any(Object))
    );
  });

  it('does not install if installation directory exists and user cancels overwrite', async () => {
    vi.mocked(invoke).mockImplementation((cmd) => {
      if (cmd === 'check_directory_exists') return Promise.resolve(true);
      if (cmd === 'get_home_directory') return Promise.resolve('/mock/home');
      return Promise.resolve(undefined);
    });
    vi.mocked(confirm).mockResolvedValueOnce(false);

    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    fireEvent.click(screen.getByText(/Begin Installation/i));
    await waitFor(() =>
      expect(confirm).toHaveBeenCalledWith(
        "Target destination already exists.\n\nDo you want to overwrite?\n\n",
        { title: "Overwrite Installation Directory?", kind: "warning" }
      )
    );
    expect(vi.mocked(invoke)).not.toHaveBeenCalledWith('install_to_directory', expect.any(Object));
    expect(mockNavigate).not.toHaveBeenCalled();
  });

  it('displays error message on installation failure', async () => {
    vi.mocked(invoke).mockImplementation((cmd) => {
      if (cmd === 'install_to_directory') return Promise.reject(new Error('Installation failed'));
      if (cmd === 'get_home_directory') return Promise.resolve('/mock/home');
      return Promise.resolve(undefined);
    });

    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    fireEvent.click(screen.getByText(/Begin Installation/i));
    await waitFor(() =>
      expect(screen.getByText(/Installation setup failed: Error: Installation failed/i)).toBeInTheDocument()
    );
  });

  it('quits application when "Cancel" is clicked and user confirms', async () => {
    vi.mocked(confirm).mockResolvedValueOnce(true);

    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    fireEvent.click(screen.getByText('Cancel'));
    await waitFor(() =>
      expect(confirm).toHaveBeenCalledWith(
        "Are you sure you want to quit the installation?",
        { title: "Quit Installation", kind: "warning" }
      )
    );
    await waitFor(() =>
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('quit_application')
    );
  });

  it('does not quit application when "Cancel" is clicked and user cancels confirmation', async () => {
    vi.mocked(confirm).mockResolvedValueOnce(false);

    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));
    fireEvent.click(screen.getByText('Cancel'));
    await waitFor(() =>
      expect(confirm).toHaveBeenCalledWith(
        "Are you sure you want to quit the installation?",
        { title: "Quit Installation", kind: "warning" }
      )
    );
    expect(vi.mocked(invoke)).not.toHaveBeenCalledWith('quit_application');
  });

  it('shows validation error for paths with spaces', async () => {
    render(<SetupComponent />);
    await waitFor(() => screen.getByDisplayValue('/mock/home/OpenBB'));

    const installDirInput = screen.getByRole('textbox', { name: /Installation Directory/i });
    fireEvent.change(installDirInput, { target: { value: '/with spaces/install' } });

    const userDataDirInput = screen.getByRole('textbox', { name: /User Data Directory/i });
    fireEvent.change(userDataDirInput, { target: { value: '/with spaces/user' } });

    fireEvent.click(screen.getByText(/Begin Installation/i));

    await waitFor(() => {
      expect(screen.getAllByText(/Path cannot contain spaces/i)).toHaveLength(2);
    });
  });
});
