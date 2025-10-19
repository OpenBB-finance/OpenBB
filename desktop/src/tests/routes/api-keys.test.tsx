import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import { invoke } from '@tauri-apps/api/core';
import { vi } from 'vitest';
import ApiKeysPage from '../../routes/api-keys';
import React from 'react';
import { message } from '@tauri-apps/plugin-dialog';

// --- Mocks ---
vi.mock('@tanstack/react-router', () => ({
  createFileRoute: vi.fn(() => vi.fn((options) => ({
    options: { component: options.component || ((props: any) => React.createElement('div', null, props.children)) },
  }))),
  useRouter: vi.fn(() => ({
    invalidate: vi.fn(),
  })),
  useBlocker: vi.fn(() => ({
    state: 'unblocked',
    proceed: vi.fn(),
    reset: vi.fn(),
  })),
}));
vi.mock('@tauri-apps/api/core', () => ({ invoke: vi.fn() }));
vi.mock('@tauri-apps/plugin-dialog', () => ({
    message: vi.fn(),
}));

const mockLocalStorage = { getItem: vi.fn(), setItem: vi.fn(), removeItem: vi.fn(), clear: vi.fn(), length: 0, key: vi.fn() };
Object.defineProperty(window, 'localStorage', { writable: true, value: mockLocalStorage });

const mockClipboard = { writeText: vi.fn() };
Object.defineProperty(navigator, 'clipboard', { writable: true, value: mockClipboard });

let mockCredentials: Record<string, string | null> = {};

beforeEach(() => {
  mockCredentials = {};
  vi.clearAllMocks();
  mockLocalStorage.getItem.mockReturnValue(null);
  mockClipboard.writeText.mockResolvedValue(undefined);

  vi.mocked(invoke).mockImplementation(async (cmd, args) => {
    if (cmd === 'get_user_credentials') {
      return Promise.resolve({ credentials: { ...mockCredentials } });
    }
    if (cmd === 'update_user_credentials') {
      const { credentials } = args as { credentials: Record<string, string> };
      mockCredentials = { ...credentials };
      return Promise.resolve(undefined);
    }
    if (cmd === 'open_credentials_file' || cmd === 'open_url_in_window') {
      return Promise.resolve(undefined);
    }
    return Promise.resolve({});
  });
});

describe('ApiKeysPage', () => {

  test('shows error on fetch failure', async () => {
    const error = new Error('fail');
    vi.mocked(invoke).mockImplementation(async (cmd) => {
        if (cmd === 'get_user_credentials') {
            throw error;
        }
        return {};
    });

    render(<ApiKeysPage />);

    await waitFor(() => {
        expect(message).toHaveBeenCalledWith('Failed to load API keys: Error: fail', expect.any(Object));
    });
  });

  test('shows empty state', async () => {
    mockCredentials = {};
    render(<ApiKeysPage />);
    await waitFor(() => expect(screen.getByText(/No API keys added/i)).toBeInTheDocument());
  });

  test('add and save new API key', async () => {
    mockCredentials = {};
    render(<ApiKeysPage />);
    await waitFor(() => expect(screen.getByText(/No API keys added/i)).toBeInTheDocument());

    fireEvent.click(screen.getByRole('button', { name: /Add New Key/i }));

    await screen.findByText('Add API Key');

    fireEvent.change(screen.getByPlaceholderText('api_key_name'), { target: { value: 'NEW_KEY' } });
    fireEvent.change(screen.getByPlaceholderText('Enter your API key'), { target: { value: 'new_value' } });

    fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    await waitFor(() => {
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('update_user_credentials', { credentials: { NEW_KEY: 'new_value' } });
    });

    await waitFor(() => {
        expect(screen.getByText('NEW_KEY')).toBeInTheDocument();
    });
  });

  test('add button is disabled if API key name is empty', async () => {
    render(<ApiKeysPage />);
    await screen.findByText(/No API keys added/i);

    fireEvent.click(screen.getByRole('button', { name: /Add New Key/i }));

    await screen.findByText('Add API Key');

    const addButton = screen.getByRole('button', { name: 'Add' });
    expect(addButton).toBeDisabled();

    fireEvent.change(screen.getByPlaceholderText('api_key_name'), { target: { value: 'some-key' } });
    expect(addButton).not.toBeDisabled();
  });

  test('shows error if duplicate API key names', async () => {
    mockCredentials = { 'DUPLICATE_KEY': 'value1' };
    render(<ApiKeysPage />);
    await screen.findByText('DUPLICATE_KEY');

    fireEvent.click(screen.getByRole('button', { name: /Add New Key/i }));

    await screen.findByText('Add API Key');

    fireEvent.change(screen.getByPlaceholderText('api_key_name'), { target: { value: 'DUPLICATE_KEY' } });
    fireEvent.change(screen.getByPlaceholderText('Enter your API key'), { target: { value: 'value2' } });

    fireEvent.click(screen.getByRole('button', { name: 'Add' }));

    await waitFor(() => {
      expect(message).toHaveBeenCalledWith('An API key with this name already exists.', expect.any(Object));
    });
  });

  test('removes an API key', async () => {
    mockCredentials = { 'KEY_TO_REMOVE': 'value' };
    render(<ApiKeysPage />);

    await waitFor(() => expect(screen.getByText('KEY_TO_REMOVE')).toBeInTheDocument());

    const row = screen.getByText('KEY_TO_REMOVE').closest('.group');
    expect(row).not.toBeNull();

    const editButton = row!.querySelector('button'); // The first button should be edit
    expect(editButton).not.toBeNull();
    fireEvent.click(editButton!);

    await screen.findByText('Edit API Key');

    const deleteButton = screen.getByRole('button', { name: 'Delete' });
    fireEvent.click(deleteButton);

    await waitFor(() => {
      expect(vi.mocked(invoke)).toHaveBeenCalledWith('update_user_credentials', { credentials: {} });
    });

    await waitFor(() => {
      expect(screen.queryByText('KEY_TO_REMOVE')).not.toBeInTheDocument();
    });
  });

  test('copies API key value to clipboard', async () => {
    mockCredentials = { 'TEST_KEY': 'secret_value' };
    render(<ApiKeysPage />);

    await waitFor(() => expect(screen.getByText('TEST_KEY')).toBeInTheDocument());

    const row = screen.getByText('TEST_KEY').closest('.group');
    expect(row).not.toBeNull();

    const copyButton = row!.querySelectorAll('button')[2]; // Third button is copy
    expect(copyButton).not.toBeNull();
    fireEvent.click(copyButton!);

    await waitFor(() => {
      expect(mockClipboard.writeText).toHaveBeenCalledWith('secret_value');
    });
  });

  test('filters API keys', async () => {
    mockCredentials = { 'KEY1': 'value1', 'KEY2': 'value2' };
    render(<ApiKeysPage />);

    await waitFor(() => {
      expect(screen.getByText('KEY1')).toBeInTheDocument();
      expect(screen.getByText('KEY2')).toBeInTheDocument();
    });

    const searchInput = screen.getByPlaceholderText('Search API Keys...');
    fireEvent.change(searchInput, { target: { value: 'KEY1' } });

    await waitFor(() => {
      expect(screen.getByText('KEY1')).toBeInTheDocument();
      expect(screen.queryByText('KEY2')).not.toBeInTheDocument();
    });
  });

  test('opens Settings modal and opens files', async () => {
    render(<ApiKeysPage />);
    await waitFor(() => expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument());

    fireEvent.click(screen.getByTestId('settings-button'));

    await screen.findByText(/Configuration Files/i);
    expect(screen.getByLabelText('user_settings.json')).toBeChecked();

    fireEvent.click(screen.getByRole('button', { name: /Open File/i }));
    expect(vi.mocked(invoke)).toHaveBeenLastCalledWith('open_credentials_file', { fileName: 'user_settings.json' });

    await waitFor(() => expect(screen.queryByText(/Configuration Files/i)).not.toBeInTheDocument());

    fireEvent.click(screen.getByTestId('settings-button'));
    await screen.findByText(/Configuration Files/i);

    fireEvent.click(screen.getByLabelText('system_settings.json'));
    fireEvent.click(screen.getByRole('button', { name: /Open File/i }));
    expect(vi.mocked(invoke)).toHaveBeenLastCalledWith('open_credentials_file', { fileName: 'system_settings.json' });
  });

  test('opens documentation via documentation icon', async () => {
    render(<ApiKeysPage />);
    await waitFor(() => expect(screen.queryByText(/Loading/i)).not.toBeInTheDocument());

    fireEvent.click(screen.getByTestId('documentation-button'));

    expect(vi.mocked(invoke)).toHaveBeenCalledWith('open_url_in_window', {
      url: 'https://docs.openbb.co/desktop/api_keys',
      title: 'Open Data Platform Documentation',
    });
  });

  test('toggles API key visibility', async () => {
    mockCredentials = { 'TEST_KEY': 'secret_value' };
    render(<ApiKeysPage />);

    await waitFor(() => expect(screen.getByText('TEST_KEY')).toBeInTheDocument());

    expect(screen.getByText('********************')).toBeInTheDocument();

    const row = screen.getByText('TEST_KEY').closest('.group');
    expect(row).not.toBeNull();

    const visibilityButton = row!.querySelectorAll('button')[1]; // Second button is visibility
    fireEvent.click(visibilityButton!);

    await waitFor(() => {
      expect(screen.getByText('secret_value')).toBeInTheDocument();
    });

    fireEvent.click(visibilityButton!);

    await waitFor(() => {
      expect(screen.getByText('********************')).toBeInTheDocument();
    });
  });
});
