import { buildOpenBBRequestInit, getOpenBBAuthorization } from "./openbbBackend";

export interface OpenBBSseEvent {
  type: string;
  data: string;
}

export interface OpenBBSseStreamOptions {
  eventTypes?: string[];
  onOpen?: () => void;
  onEvent?: (event: OpenBBSseEvent) => void;
  onConnectionError?: (error: unknown) => void;
}

export interface OpenBBSseConnection {
  close: () => void;
}

function parseEventBlock(block: string): OpenBBSseEvent | null {
  let type = "message";
  const dataLines: string[] = [];

  for (const rawLine of block.split(/\r?\n/)) {
    if (!rawLine || rawLine.startsWith(":")) {
      continue;
    }

    const separatorIndex = rawLine.indexOf(":");
    const field = separatorIndex >= 0 ? rawLine.slice(0, separatorIndex) : rawLine;
    let value = separatorIndex >= 0 ? rawLine.slice(separatorIndex + 1) : "";
    if (value.startsWith(" ")) {
      value = value.slice(1);
    }

    if (field === "event" && value) {
      type = value;
    } else if (field === "data") {
      dataLines.push(value);
    }
  }

  if (dataLines.length === 0) {
    return null;
  }

  return {
    type,
    data: dataLines.join("\n"),
  };
}

function dispatchBufferedEvents(
  buffer: string,
  isClosed: () => boolean,
  onEvent?: (event: OpenBBSseEvent) => void,
): string {
  let remaining = buffer;

  while (!isClosed()) {
    const separatorIndex = remaining.search(/\r?\n\r?\n/);
    if (separatorIndex < 0) {
      break;
    }

    const block = remaining.slice(0, separatorIndex);
    const separatorMatch = remaining.slice(separatorIndex).match(/^\r?\n\r?\n/);
    const separatorLength = separatorMatch?.[0].length ?? 2;
    remaining = remaining.slice(separatorIndex + separatorLength);

    const event = parseEventBlock(block);
    if (event) {
      onEvent?.(event);
    }
  }

  return remaining;
}

async function readErrorDetail(response: Response): Promise<string> {
  try {
    const payload = await response.json() as { detail?: unknown; message?: unknown };
    if (typeof payload?.detail === "string" && payload.detail.trim()) {
      return payload.detail;
    }
    if (typeof payload?.message === "string" && payload.message.trim()) {
      return payload.message;
    }
  } catch {
    try {
      const text = await response.text();
      if (text.trim()) {
        return text.trim();
      }
    } catch {
      return "";
    }
  }

  return "";
}

function openEventSourceStream(url: string, options: OpenBBSseStreamOptions): OpenBBSseConnection {
  let closed = false;
  const stream = new EventSource(url);

  stream.onopen = () => {
    if (!closed) {
      options.onOpen?.();
    }
  };

  stream.onmessage = (event) => {
    if (!closed) {
      options.onEvent?.({ type: "message", data: event.data });
    }
  };

  for (const type of options.eventTypes ?? []) {
    if (type === "message") {
      continue;
    }

    stream.addEventListener(type, (event) => {
      if (closed || !("data" in event)) {
        return;
      }

      const messageEvent = event as MessageEvent<string>;
      options.onEvent?.({ type, data: messageEvent.data ?? "" });
    });
  }

  stream.onerror = (event) => {
    if (!closed) {
      options.onConnectionError?.(event);
    }
  };

  return {
    close: () => {
      if (closed) {
        return;
      }
      closed = true;
      stream.close();
    },
  };
}

function openFetchStream(url: string, options: OpenBBSseStreamOptions): OpenBBSseConnection {
  let closed = false;
  const controller = new AbortController();

  const run = async () => {
    try {
      const response = await fetch(
        url,
        buildOpenBBRequestInit({
          method: "GET",
          headers: { Accept: "text/event-stream" },
          cache: "no-store",
          signal: controller.signal,
        }),
      );

      if (!response.ok) {
        const detail = await readErrorDetail(response);
        throw new Error(detail || `SSE request failed (${response.status})`);
      }

      if (!response.body) {
        throw new Error("SSE response body is unavailable.");
      }

      if (closed) {
        return;
      }

      options.onOpen?.();

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = "";

      while (!closed) {
        const { done, value } = await reader.read();
        if (done) {
          break;
        }

        buffer += decoder.decode(value, { stream: true });
        buffer = dispatchBufferedEvents(buffer, () => closed, options.onEvent);
      }

      if (closed) {
        return;
      }

      buffer += decoder.decode();
      const remaining = dispatchBufferedEvents(buffer, () => closed, options.onEvent).trim();
      if (!closed && remaining) {
        const trailingEvent = parseEventBlock(remaining);
        if (trailingEvent) {
          options.onEvent?.(trailingEvent);
        }
      }

      if (!closed) {
        throw new Error("SSE stream closed unexpectedly.");
      }
    } catch (error) {
      if (!closed && !controller.signal.aborted) {
        options.onConnectionError?.(error);
      }
    }
  };

  void run();

  return {
    close: () => {
      if (closed) {
        return;
      }
      closed = true;
      controller.abort();
    },
  };
}

export function openOpenBBSseStream(url: string, options: OpenBBSseStreamOptions = {}): OpenBBSseConnection {
  const authorization = getOpenBBAuthorization();
  if (!authorization && typeof EventSource !== "undefined") {
    return openEventSourceStream(url, options);
  }

  return openFetchStream(url, options);
}
