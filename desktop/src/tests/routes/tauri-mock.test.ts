import { beforeAll, afterEach, expect, test } from 'vitest';
import { randomFillSync } from 'crypto';
import { mockIPC, clearMocks } from '@tauri-apps/api/mocks';
import { invoke } from '@tauri-apps/api/core';

beforeAll(() => {
  Object.defineProperty(window, 'crypto', {
    value: {
      getRandomValues: (buffer: Uint8Array | Uint16Array | Uint32Array) => {
        return randomFillSync(buffer);
      },
    },
  });
});

// Clear mocks after each test to ensure test isolation
afterEach(() => {
  clearMocks();
});

test('mockIPC intercepts invoke calls', async () => {
  // Mock the 'greet' command to return a specific string
  mockIPC((cmd, args) => {
    if (cmd === 'greet') {
      // Ensure args is an object and has a 'name' property
      if (typeof args === 'object' && args !== null && 'name' in args) {
        return `Hello, ${(args as Record<string, unknown>).name}!`;
      }
      throw new Error('Invalid arguments for greet command');
    }
    // If other commands are invoked, let them pass through or throw an error
    throw new Error(`Unknown command: ${cmd}`);
  });

  // Invoke the mocked command
  const result = await invoke('greet', { name: 'Tauri' });

  // Assert that the mocked response is returned
  expect(result).toBe('Hello, Tauri!');
});

test('mockIPC can simulate errors', async () => {
  // Mock the 'fail_command' to throw an error
  mockIPC((cmd) => {
    if (cmd === 'fail_command') {
      throw new Error('This command failed!');
    }
  });

  // Expect the invoke call to reject with the mocked error
  await expect(invoke('fail_command')).rejects.toThrow('This command failed!');
});
