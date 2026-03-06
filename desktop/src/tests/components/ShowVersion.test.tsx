/// <reference types="vitest/globals" />
import { cleanup, render, screen } from '@testing-library/react';
import { afterEach, beforeEach, expect, test, vi } from 'vitest';

const tauriInternalsDescriptor = () =>
  Object.getOwnPropertyDescriptor(window, '__TAURI_INTERNALS__');

const restoreTauriInternals = (descriptor?: PropertyDescriptor) => {
  if (descriptor) {
    Object.defineProperty(window, '__TAURI_INTERNALS__', descriptor);
    return;
  }
  delete (window as Window & { __TAURI_INTERNALS__?: unknown }).__TAURI_INTERNALS__;
};

beforeEach(() => {
  vi.resetModules();
});

afterEach(() => {
  cleanup();
  vi.restoreAllMocks();
  vi.resetModules();
});

test('does not call getVersion outside Tauri runtime', async () => {
  const getVersion = vi.fn().mockResolvedValue('9.9.9');
  const originalDescriptor = tauriInternalsDescriptor();
  restoreTauriInternals();

  vi.doMock('@tauri-apps/api/app', () => ({
    getVersion,
  }));

  const { default: ShowVersion } = await import('../../components/ShowVersion');
  render(<ShowVersion />);

  expect(getVersion).not.toHaveBeenCalled();
  expect(screen.queryByText(/^v/)).not.toBeInTheDocument();

  restoreTauriInternals(originalDescriptor);
});

test('renders the version inside Tauri runtime', async () => {
  const getVersion = vi.fn().mockResolvedValue('1.2.3');
  const originalDescriptor = tauriInternalsDescriptor();

  Object.defineProperty(window, '__TAURI_INTERNALS__', {
    configurable: true,
    value: {},
  });

  vi.doMock('@tauri-apps/api/app', () => ({
    getVersion,
  }));

  const { default: ShowVersion } = await import('../../components/ShowVersion');
  render(<ShowVersion />);

  expect(await screen.findByText('v1.2.3')).toBeInTheDocument();
  expect(getVersion).toHaveBeenCalledTimes(1);

  restoreTauriInternals(originalDescriptor);
});
