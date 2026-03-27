import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import {
  buildTradingViewSymbolUrl,
  buildTradingViewWidgetConfig,
} from "../../lib/tradingView";
import type {
  TradingViewFinanceWidgetType,
  TradingViewThemeMode,
} from "../../types/finance";

interface TradingViewWidgetEmbedProps {
  widgetType: TradingViewFinanceWidgetType;
  symbol: string;
  theme: TradingViewThemeMode;
  minHeight?: number;
  frameHeight?: number;
  title: string;
  description?: string;
  lazy?: boolean;
}

const TRADINGVIEW_CONSOLE_NOISE = [
  "Deprecation warning: use moment.updateLocale",
  "Cannot listen to the event from the provider",
  "Cannot listen to the event from the provided iframe",
  "Fetch:POST https://scanner.tradingview.com",
  "Fetch:GET https://scanner.tradingview.com",
];

const TRADING_VIEW_WIDGET_MAX_ATTEMPTS = 2;

function buildTradingViewHostDocument(
  widgetType: TradingViewFinanceWidgetType,
  symbol: string,
  theme: TradingViewThemeMode,
  frameHeight?: number,
) {
  const config = buildTradingViewWidgetConfig(widgetType, symbol, theme, frameHeight);
  const payload = JSON.stringify(config.payload).replace(/<\/script/gi, "<\\/script");
  const scriptSrc = config.scriptSrc;
  const consoleNoise = JSON.stringify(TRADINGVIEW_CONSOLE_NOISE);

  return `<!doctype html>
<html lang="en">
  <head>
    <meta charset="utf-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1" />
    <style>
      html, body {
        margin: 0;
        width: 100%;
        min-height: 100%;
        background: transparent;
        overflow: hidden;
      }

      .tv-host {
        width: 100%;
        min-height: 100%;
      }

      .tradingview-widget-container,
      .tradingview-widget-container__widget {
        width: 100%;
        height: 100%;
        min-height: 100%;
      }

      .tradingview-widget-copyright {
        margin-top: 8px;
        color: rgba(148, 163, 184, 0.95);
        font: 500 11px/1.4 Inter, system-ui, sans-serif;
      }

      .tradingview-widget-copyright a {
        color: inherit;
        text-decoration: none;
      }
    </style>
  </head>
  <body>
    <div class="tv-host">
      <div class="tradingview-widget-container">
        <div class="tradingview-widget-container__widget"></div>
        <div class="tradingview-widget-copyright">
          <a href="https://www.tradingview.com/" rel="noopener nofollow" target="_blank">Track all markets on TradingView</a>
        </div>
      </div>
    </div>
    <script>
      (() => {
        const NOISE = ${consoleNoise};
        const shouldSuppress = (args) =>
          args.some((arg) => typeof arg === "string" && NOISE.some((item) => arg.includes(item)));
        const patch = (method) => (...args) => {
          if (shouldSuppress(args)) return;
          method.apply(console, args);
        };
        console.warn = patch(console.warn.bind(console));
        console.error = patch(console.error.bind(console));
      })();
    </script>
    <script type="text/javascript" src="${scriptSrc}" async>${payload}</script>
  </body>
</html>`;
}

export function TradingViewWidgetEmbed({
  widgetType,
  symbol,
  theme,
  minHeight = 220,
  frameHeight,
  title,
  description,
  lazy = false,
}: TradingViewWidgetEmbedProps) {
  const hostRef = useRef<HTMLDivElement | null>(null);
  const frameRef = useRef<HTMLIFrameElement | null>(null);
  const [shouldMount, setShouldMount] = useState(!lazy);
  const [hasTimedOut, setHasTimedOut] = useState(false);
  const [attempt, setAttempt] = useState(1);
  const [reloadToken, setReloadToken] = useState(0);
  const tradingViewHref = useMemo(() => buildTradingViewSymbolUrl(symbol), [symbol]);

  const handleRetry = useCallback(() => {
    setHasTimedOut(false);
    setAttempt(1);
    setReloadToken((value) => value + 1);
  }, []);

  useEffect(() => {
    if (!lazy || shouldMount) {
      return undefined;
    }

    const host = hostRef.current;
    if (!host || typeof IntersectionObserver === "undefined") {
      setShouldMount(true);
      return undefined;
    }

    const observer = new IntersectionObserver((entries) => {
      if (entries.some((entry) => entry.isIntersecting)) {
        setShouldMount(true);
        observer.disconnect();
      }
    });

    observer.observe(host);
    return () => observer.disconnect();
  }, [lazy, shouldMount]);

  useEffect(() => {
    setHasTimedOut(false);
    setAttempt(1);
  }, [widgetType, symbol, theme, frameHeight]);

  useEffect(() => {
    if (!shouldMount) {
      return undefined;
    }

    const frameNode = frameRef.current;
    if (!frameNode) {
      return undefined;
    }

    setHasTimedOut(false);
    frameNode.srcdoc = buildTradingViewHostDocument(widgetType, symbol, theme, frameHeight);

    let timeoutId = 0;
    let pollId = 0;

    const cleanup = () => {
      window.clearTimeout(timeoutId);
      window.clearInterval(pollId);
    };

      const clearLoadedState = () => {
        const documentRef = frameNode.contentDocument;
        const hasWidgetContent = Boolean(
          documentRef?.querySelector(".tradingview-widget-container__widget")?.children.length,
        );

        if (hasWidgetContent) {
        cleanup();
        setHasTimedOut(false);
        return true;
      }
      return false;
    };

    timeoutId = window.setTimeout(() => {
      if (clearLoadedState()) {
        return;
      }
      cleanup();
      // Increase tolerance rather than aggressively hiding: if it hasn't loaded in 30s, then we retry.
      if (attempt < TRADING_VIEW_WIDGET_MAX_ATTEMPTS) {
        setAttempt((value) => value + 1);
        setReloadToken((value) => value + 1);
        return;
      }
      // setHasTimedOut(true); <-- disabled to prevent hiding working charts
    }, 30_000);

    pollId = window.setInterval(() => {
      clearLoadedState();
    }, 250);

    const handleLoad = () => {
      clearLoadedState();
    };
    frameNode.addEventListener("load", handleLoad);

    return () => {
      frameNode.removeEventListener("load", handleLoad);
      cleanup();
      frameNode.srcdoc = "";
    };
  }, [attempt, frameHeight, reloadToken, shouldMount, symbol, theme, widgetType]);

  return (
    <div ref={hostRef} className="relative" style={{ minHeight }}>
      <iframe
        ref={frameRef}
        className={`h-full w-full rounded-sm border border-theme-outline bg-theme-secondary ${
          hasTimedOut ? "hidden" : "block"
        }`}
        style={{ minHeight }}
        aria-label={title}
        title={title}
        loading={lazy ? "lazy" : "eager"}
      />
      {!shouldMount ? (
        <div
          className="absolute inset-0 flex items-center justify-center rounded-sm border border-dashed border-theme-outline bg-theme-secondary/50"
          style={{ minHeight }}
        >
          <p className="body-xs-regular text-theme-muted">Loading {title.toLowerCase()} when visible...</p>
        </div>
      ) : null}
      {hasTimedOut ? (
        <div
          className="absolute inset-0 flex flex-col items-center justify-center rounded-sm border border-amber-500/40 bg-amber-500/10 px-6 text-center"
          style={{ minHeight }}
        >
          <p className="body-xs-medium text-theme-primary">{title}</p>
          <p className="mt-2 body-xs-regular text-theme-muted">
            TradingView widget failed to load. Try another symbol or reload.
          </p>
          {description ? <p className="mt-1 body-xxs-regular text-theme-muted">{description}</p> : null}
          <div className="mt-4 flex flex-wrap items-center justify-center gap-2">
            <button
              type="button"
              onClick={handleRetry}
              className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-1.5 body-xxs-medium text-theme-primary hover:bg-theme-secondary/80"
            >
              Retry widget
            </button>
            <a
              href={tradingViewHref}
              target="_blank"
              rel="noopener noreferrer"
              className="rounded-sm border border-blue-500/30 bg-blue-500/10 px-3 py-1.5 body-xxs-medium text-blue-300 hover:bg-blue-500/20"
            >
              Open in TradingView
            </a>
          </div>
        </div>
      ) : null}
    </div>
  );
}
