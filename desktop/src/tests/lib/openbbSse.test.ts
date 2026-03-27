/// <reference types="vitest/globals" />
import { waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, test, vi } from "vitest";
import type { OpenBBSseConnection, OpenBBSseEvent } from "../../lib/openbbSse";
import { openOpenBBSseStream } from "../../lib/openbbSse";
import { setOpenBBBasicCredentials, setOpenBBBearerToken } from "../../lib/openbbBackend";

class MockEventSource {
  static instances: MockEventSource[] = [];

  url: string;

  onopen: ((this: EventSource, ev: Event) => unknown) | null = null;

  onmessage: ((this: EventSource, ev: MessageEvent<string>) => unknown) | null = null;

  onerror: ((this: EventSource, ev: Event) => unknown) | null = null;

  private listeners = new Map<string, Array<(event: MessageEvent<string>) => void>>();

  close = vi.fn();

  constructor(url: string) {
    this.url = url;
    MockEventSource.instances.push(this);
  }

  addEventListener(type: string, listener: EventListenerOrEventListenerObject): void {
    if (typeof listener !== "function") {
      return;
    }
    const list = this.listeners.get(type) ?? [];
    list.push(listener as (event: MessageEvent<string>) => void);
    this.listeners.set(type, list);
  }

  emit(type: string, payload: unknown): void {
    const event = { data: JSON.stringify(payload) } as MessageEvent<string>;
    for (const listener of this.listeners.get(type) ?? []) {
      listener(event);
    }
  }

  emitMessage(payload: unknown): void {
    this.onmessage?.call(this as unknown as EventSource, {
      data: JSON.stringify(payload),
    } as MessageEvent<string>);
  }

  triggerOpen(): void {
    this.onopen?.call(this as unknown as EventSource, new Event("open"));
  }
}

describe("openbbSse", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    localStorage.clear();
    MockEventSource.instances = [];
    vi.stubGlobal("EventSource", MockEventSource as unknown as typeof EventSource);
  });

  test("uses EventSource when no bearer token is configured", () => {
    global.fetch = vi.fn() as unknown as typeof fetch;

    const onOpen = vi.fn();
    const onEvent = vi.fn();
    const connection = openOpenBBSseStream("http://127.0.0.1:6900/sse", {
      eventTypes: ["scores_update"],
      onOpen,
      onEvent,
    });

    expect(MockEventSource.instances).toHaveLength(1);
    expect(MockEventSource.instances[0]?.url).toBe("http://127.0.0.1:6900/sse");
    expect(global.fetch).not.toHaveBeenCalled();

    const stream = MockEventSource.instances[0]!;
    stream.triggerOpen();
    stream.emit("scores_update", { label: "Risk-On / Bull" });
    stream.emitMessage({ line: "training started" });

    expect(onOpen).toHaveBeenCalledTimes(1);
    expect(onEvent).toHaveBeenCalledWith({
      type: "scores_update",
      data: JSON.stringify({ label: "Risk-On / Bull" }),
    });
    expect(onEvent).toHaveBeenCalledWith({
      type: "message",
      data: JSON.stringify({ line: "training started" }),
    });

    connection.close();
    expect(stream.close).toHaveBeenCalledTimes(1);
  });

  test("uses fetch-based SSE with bearer authorization when a token is configured", async () => {
    setOpenBBBearerToken("secret-token");

    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('event: status\ndata: {"status":"running"}\n\n'));
        controller.enqueue(encoder.encode('event: done\ndata: {"status":"completed"}\n\n'));
        controller.close();
      },
    });

    global.fetch = vi.fn(async () => new Response(body, {
      status: 200,
      headers: { "Content-Type": "text/event-stream" },
    })) as unknown as typeof fetch;

    const onOpen = vi.fn();
    const onConnectionError = vi.fn();
    const events: OpenBBSseEvent[] = [];
    let connection: OpenBBSseConnection | null = null;

    connection = openOpenBBSseStream("http://127.0.0.1:6900/sse", {
      eventTypes: ["status", "done"],
      onOpen,
      onEvent: (event) => {
        events.push(event);
        if (event.type === "done") {
          connection?.close();
        }
      },
      onConnectionError,
    });

    await waitFor(() => {
      expect(events.map((event) => event.type)).toEqual(["status", "done"]);
    });

    const init = vi.mocked(global.fetch).mock.calls[0]?.[1] as RequestInit;
    const headers = new Headers(init?.headers);

    expect(MockEventSource.instances).toHaveLength(0);
    expect(onOpen).toHaveBeenCalledTimes(1);
    expect(onConnectionError).not.toHaveBeenCalled();
    expect(headers.get("Authorization")).toBe("Bearer secret-token");
    expect(headers.get("Accept")).toBe("text/event-stream");
  });

  test("uses fetch-based SSE with basic authorization when credentials are configured", async () => {
    setOpenBBBasicCredentials("openbb", "secret-password");

    const encoder = new TextEncoder();
    const body = new ReadableStream<Uint8Array>({
      start(controller) {
        controller.enqueue(encoder.encode('event: done\ndata: {"status":"completed"}\n\n'));
        controller.close();
      },
    });

    global.fetch = vi.fn(async () => new Response(body, {
      status: 200,
      headers: { "Content-Type": "text/event-stream" },
    })) as unknown as typeof fetch;

    const events: OpenBBSseEvent[] = [];
    let connection: OpenBBSseConnection | null = null;
    connection = openOpenBBSseStream("http://127.0.0.1:6900/sse", {
      eventTypes: ["done"],
      onEvent: (event) => {
        events.push(event);
        connection?.close();
      },
    });

    await waitFor(() => {
      expect(events.map((event) => event.type)).toEqual(["done"]);
    });

    const init = vi.mocked(global.fetch).mock.calls[0]?.[1] as RequestInit;
    const headers = new Headers(init?.headers);

    expect(MockEventSource.instances).toHaveLength(0);
    expect(headers.get("Authorization")).toBe("Basic b3BlbmJiOnNlY3JldC1wYXNzd29yZA==");
    expect(headers.get("Accept")).toBe("text/event-stream");
  });
});
