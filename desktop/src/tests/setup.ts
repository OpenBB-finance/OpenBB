import '@testing-library/jest-dom';
import React from 'react';

// Mock @openbb/ui-pro to avoid forwardRef warnings in tests
vi.mock('@openbb/ui-pro', () => ({
  Tooltip: ({ children, content }: { children: React.ReactNode; content: string }) =>
    React.createElement('div', { 'data-tooltip-content': content }, children),
  Button: ({ children, ...props }: { children: React.ReactNode; [key: string]: unknown }) =>
    React.createElement('button', props, children),
}));

// Mock ResizeObserver
const ResizeObserverMock = vi.fn(() => ({
  observe: vi.fn(),
  unobserve: vi.fn(),
  disconnect: vi.fn(),
}));

vi.stubGlobal('ResizeObserver', ResizeObserverMock);

const IntersectionObserverMock = vi.fn(function (
  this: {
    callback: IntersectionObserverCallback;
    observe: ReturnType<typeof vi.fn>;
    unobserve: ReturnType<typeof vi.fn>;
    disconnect: ReturnType<typeof vi.fn>;
    takeRecords: ReturnType<typeof vi.fn>;
  },
  callback: IntersectionObserverCallback,
) {
  this.callback = callback;
  this.observe = vi.fn();
  this.unobserve = vi.fn();
  this.disconnect = vi.fn();
  this.takeRecords = vi.fn(() => []);
});

vi.stubGlobal('IntersectionObserver', IntersectionObserverMock);

// Mock LocalStorage and SessionStorage
class LocalStorageMock {
  store: Record<string, string>;

  constructor() {
    this.store = {};
  }

  clear() {
    this.store = {};
  }

  getItem(key: string) {
    return this.store[key] || null;
  }

  setItem(key: string, value: string) {
    this.store[key] = String(value);
  }

  removeItem(key: string) {
    delete this.store[key];
  }

  key(index: number) {
    return Object.keys(this.store)[index] || null;
  }

  get length() {
    return Object.keys(this.store).length;
  }
}

vi.stubGlobal('localStorage', new LocalStorageMock());
vi.stubGlobal('sessionStorage', new LocalStorageMock());
