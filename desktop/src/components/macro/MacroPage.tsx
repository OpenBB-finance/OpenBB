import { useCallback, useEffect, useState } from "react";
import { resolveOpenBBBackend } from "../../lib/openbbBackend";
import {
  evaluateMacroExpression,
  fetchMacroAlerts,
  fetchMacroCatalog,
  fetchMacroDerived,
  fetchMacroRegime,
  fetchMacroSeries,
  invalidateMacroCache,
  registerMacroSeries,
  saveMacroDerived,
  searchMacroCatalog,
  triggerMacroUpdate,
} from "../../lib/macroApi";
import type {
  MacroAlertItem,
  MacroCatalogItem,
  MacroDataPoint,
  MacroExpressionResponse,
  MacroFill,
  MacroFreq,
  MacroRegimePoint,
  MacroSeriesResponse,
} from "../../types/macro";
import { CatalogSidebar } from "./CatalogSidebar";
import { ExpressionBar } from "./ExpressionBar";
import { MainSeriesChart } from "./MainSeriesChart";
import { RegimeAlertsPanel } from "./RegimeAlertsPanel";
import { RelationshipPanel } from "./RelationshipPanel";
import { StatsPanel } from "./StatsPanel";

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function yearsAgoIso(years: number): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - years);
  return d.toISOString().slice(0, 10);
}

function toDerivedId(expression: string): string {
  const clean = expression
    .trim()
    .toLowerCase()
    .replace(/[^a-z0-9]+/g, "_")
    .replace(/^_+|_+$/g, "");
  return `DRV:${clean || "expression"}`;
}

function isSimpleKey(expr: string): boolean {
  return /^[A-Za-z0-9:_\.]+$/.test(expr.trim());
}

function normalizePoints(input: unknown): MacroDataPoint[] {
  if (!Array.isArray(input)) {
    return [];
  }
  return input
    .map((item) => {
      const row = item as Partial<MacroDataPoint>;
      const date = typeof row.date === "string" ? row.date : "";
      const numeric = typeof row.value === "number" ? row.value : Number(row.value);
      if (!date || Number.isNaN(numeric)) {
        return null;
      }
      return { date, value: numeric };
    })
    .filter((item): item is MacroDataPoint => item !== null);
}

function normalizeAlerts(input: unknown): MacroAlertItem[] {
  if (!Array.isArray(input)) {
    return [];
  }
  return input as MacroAlertItem[];
}

function toFriendlyError(error: unknown): string {
  if (error instanceof Error) {
    const text = error.message || "Unknown error";
    if (/FRED_API_KEY/i.test(text)) {
      return "FRED_API_KEY is not configured. Set the key or use cached data.";
    }
    if (/Failed to fetch/i.test(text) || /NetworkError/i.test(text)) {
      return "Backend connection failed. Verify OpenBB API is running.";
    }
    if (/not found/i.test(text)) {
      return "Endpoint not found. Check API version and router registration.";
    }
    return text;
  }
  return "Request failed due to an unknown error.";
}

export default function MacroPage() {
  const [backendBaseUrl, setBackendBaseUrl] = useState<string>("");
  const [isBackendLoading, setIsBackendLoading] = useState(false);
  const [isBusy, setIsBusy] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);

  const [expression, setExpression] = useState("FRED:UNRATE");
  const [selectedKey, setSelectedKey] = useState("FRED:UNRATE");
  const [transform, setTransform] = useState("level");
  const [freq, setFreq] = useState<MacroFreq>("W");
  const [fill, setFill] = useState<MacroFill>("ffill");
  const [startDate, setStartDate] = useState(yearsAgoIso(10));
  const [endDate, setEndDate] = useState(todayIso());

  const [catalogItems, setCatalogItems] = useState<MacroCatalogItem[]>([]);
  const [searchText, setSearchText] = useState("");
  const [searchResults, setSearchResults] = useState<MacroCatalogItem[]>([]);
  const [seriesPayload, setSeriesPayload] = useState<MacroSeriesResponse | null>(null);
  const [exprPayload, setExprPayload] = useState<MacroExpressionResponse | null>(null);

  const [ratioPoints, setRatioPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [spreadPoints, setSpreadPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [corrPoints, setCorrPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [betaPoints, setBetaPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [leftSymbol, setLeftSymbol] = useState("FRED:DGS10");
  const [rightSymbol, setRightSymbol] = useState("FRED:DGS2");

  const [latestRegime, setLatestRegime] = useState<MacroRegimePoint | null>(null);
  const [currentAlerts, setCurrentAlerts] = useState<MacroAlertItem[]>([]);
  const [historyAlerts, setHistoryAlerts] = useState<MacroAlertItem[]>([]);

  const chartPayload = exprPayload?.status === "ok" ? exprPayload : seriesPayload;
  const chartPoints = normalizePoints(chartPayload?.data);
  const chartTitle = chartPayload?.meta?.title || chartPayload?.meta?.key || expression;
  const chartSubtitle = chartPayload?.meta?.source
    ? `${chartPayload.meta.source} | ${chartPayload.meta.transform}`
    : "";

  const resolveBackend = useCallback(async () => {
    setIsBackendLoading(true);
    setErrorMessage(null);
    try {
      const backend = await resolveOpenBBBackend();
      setBackendBaseUrl(backend.baseUrl);
      if (!backend.connected) {
        setErrorMessage("OpenBB API is not connected. Check status in the Backends tab.");
      }
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    } finally {
      setIsBackendLoading(false);
    }
  }, []);

  const refreshRegimeAndAlerts = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    const [regime, alerts] = await Promise.all([
      fetchMacroRegime(backendBaseUrl, { start: startDate, end: endDate, freq: "W", fill: "ffill" }),
      fetchMacroAlerts(backendBaseUrl, { start: startDate, end: endDate, limit: 200 }),
    ]);
    const regimePoints = Array.isArray(regime.data) ? regime.data : [];
    setLatestRegime(regime.latest || (regimePoints.length > 0 ? regimePoints[regimePoints.length - 1] : null));
    setCurrentAlerts(normalizeAlerts(alerts.current));
    setHistoryAlerts(normalizeAlerts(alerts.history));
  }, [backendBaseUrl, endDate, startDate]);

  const loadCatalog = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    const catalog = await fetchMacroCatalog(backendBaseUrl);
    setCatalogItems(catalog.items || []);
  }, [backendBaseUrl]);

  const runExpression = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    setInfoMessage(null);
    try {
      if (isSimpleKey(expression)) {
        const response = await fetchMacroSeries(backendBaseUrl, {
          key: expression,
          start: startDate,
          end: endDate,
          transform,
          freq,
          fill,
        });
        setSeriesPayload(response);
        setExprPayload(null);
        setSelectedKey(expression);
        if (response.status !== "ok") {
          setInfoMessage(response.message || "Series data is not ready.");
        }
      } else {
        const response = await evaluateMacroExpression(backendBaseUrl, {
          expr: expression,
          start: startDate,
          end: endDate,
          transform,
          freq,
          fill,
        });
        setExprPayload(response);
        setSeriesPayload(null);
        if (response.status !== "ok") {
          setInfoMessage(response.message || "Expression result is empty.");
        }
      }
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    } finally {
      setIsBusy(false);
    }
  }, [backendBaseUrl, endDate, expression, fill, freq, startDate, transform]);

  const runRelationship = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const [ratio, spread, corr, beta] = await Promise.all([
        evaluateMacroExpression(backendBaseUrl, {
          expr: `${leftSymbol}/${rightSymbol}`,
          start: startDate,
          end: endDate,
          freq,
          fill,
          transform: "level",
        }),
        evaluateMacroExpression(backendBaseUrl, {
          expr: `${leftSymbol}-${rightSymbol}`,
          start: startDate,
          end: endDate,
          freq,
          fill,
          transform: "level",
        }),
        evaluateMacroExpression(backendBaseUrl, {
          expr: `rolling_corr(${leftSymbol},${rightSymbol},60)`,
          start: startDate,
          end: endDate,
          freq,
          fill,
          transform: "level",
        }),
        evaluateMacroExpression(backendBaseUrl, {
          expr: `rolling_beta(${leftSymbol},${rightSymbol},60)`,
          start: startDate,
          end: endDate,
          freq,
          fill,
          transform: "level",
        }),
      ]);
      setRatioPoints(normalizePoints(ratio.data));
      setSpreadPoints(normalizePoints(spread.data));
      setCorrPoints(normalizePoints(corr.data));
      setBetaPoints(normalizePoints(beta.data));
      const nonOkMessage = [ratio, spread, corr, beta]
        .filter((payload) => payload.status !== "ok" && payload.message)
        .map((payload) => payload.message)
        .filter((message): message is string => Boolean(message))
        .join(" | ");
      if (nonOkMessage) {
        setInfoMessage(nonOkMessage);
      }
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    } finally {
      setIsBusy(false);
    }
  }, [backendBaseUrl, endDate, fill, freq, leftSymbol, rightSymbol, startDate]);

  const handleSearch = useCallback(async () => {
    if (!backendBaseUrl || !searchText.trim()) {
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const response = await searchMacroCatalog(backendBaseUrl, searchText.trim(), undefined, 25);
      setSearchResults(Array.isArray(response.items) ? response.items : []);
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    } finally {
      setIsBusy(false);
    }
  }, [backendBaseUrl, searchText]);

  const handleRegister = useCallback(
    async (seriesId: string) => {
      if (!backendBaseUrl) {
        return;
      }
      setIsBusy(true);
      try {
        await registerMacroSeries(backendBaseUrl, { series_id: seriesId, domain: "Custom", default_transform: "level" });
        invalidateMacroCache();
        await loadCatalog();
        setExpression(`FRED:${seriesId.toUpperCase()}`);
        setSelectedKey(`FRED:${seriesId.toUpperCase()}`);
      } catch (error) {
        setErrorMessage(toFriendlyError(error));
      } finally {
        setIsBusy(false);
      }
    },
    [backendBaseUrl, loadCatalog],
  );

  const handleSaveDerived = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    try {
      const derivedId = toDerivedId(expression);
      await saveMacroDerived(backendBaseUrl, {
        derived_id: derivedId,
        expression,
        default_transform: transform,
      });
      setInfoMessage(`Saved derived series: ${derivedId}`);
      await fetchMacroDerived(backendBaseUrl);
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    }
  }, [backendBaseUrl, expression, transform]);

  const handleRefreshDefaults = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    setIsBusy(true);
    setErrorMessage(null);
    try {
      const response = await triggerMacroUpdate(backendBaseUrl, { all_default: true, start: startDate, end: endDate });
      invalidateMacroCache();
      await loadCatalog();
      await refreshRegimeAndAlerts();
      setInfoMessage(response.message || `Updated ${response.updated_series.length} series.`);
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    } finally {
      setIsBusy(false);
    }
  }, [backendBaseUrl, endDate, loadCatalog, refreshRegimeAndAlerts, startDate]);

  useEffect(() => {
    void resolveBackend();
  }, [resolveBackend]);

  useEffect(() => {
    if (!backendBaseUrl) {
      return;
    }
    void (async () => {
      try {
        await loadCatalog();
        await runExpression();
        await runRelationship();
        await refreshRegimeAndAlerts();
      } catch (error) {
        setErrorMessage(toFriendlyError(error));
      }
    })();
  }, [backendBaseUrl, loadCatalog, refreshRegimeAndAlerts, runExpression, runRelationship]);

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-3 flex items-start justify-between gap-3">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Macro</h1>
          <p className="body-sm-regular text-theme-muted">
            FRED-based macro analysis with transformations, cross-asset relations, regime scores, and alerts.
          </p>
        </div>
        <button type="button" className="button-secondary rounded-sm px-3 py-2 body-xs-medium" onClick={handleRefreshDefaults} disabled={isBusy}>
          Refresh Defaults
        </button>
      </div>

      {errorMessage ? (
        <div className="mb-2 rounded-sm border border-red-500/60 bg-red-500/10 p-2">
          <p className="body-xs-medium text-red-300">{errorMessage}</p>
        </div>
      ) : null}
      {infoMessage ? (
        <div className="mb-2 rounded-sm border border-sky-500/60 bg-sky-500/10 p-2">
          <p className="body-xs-medium text-sky-300">{infoMessage}</p>
        </div>
      ) : null}

      <ExpressionBar
        expression={expression}
        onExpressionChange={setExpression}
        transform={transform}
        onTransformChange={setTransform}
        freq={freq}
        onFreqChange={setFreq}
        fill={fill}
        onFillChange={setFill}
        startDate={startDate}
        endDate={endDate}
        onStartDateChange={setStartDate}
        onEndDateChange={setEndDate}
        onRun={() => {
          void runExpression();
          void runRelationship();
          void refreshRegimeAndAlerts();
        }}
        onSave={() => {
          void handleSaveDerived();
        }}
        isBusy={isBusy || isBackendLoading}
      />

      <div className="mt-3 grid grid-cols-1 gap-3 xl:grid-cols-[300px_minmax(0,1fr)_320px]">
        <CatalogSidebar
          items={catalogItems}
          selectedKey={selectedKey}
          searchText={searchText}
          onSearchTextChange={setSearchText}
          onSearch={() => void handleSearch()}
          onSelectKey={(key) => {
            setSelectedKey(key);
            setExpression(key);
            const next = catalogItems.find((item) => item.id === key || `FRED:${item.series_id}` === key);
            setTransform(next?.default_transform || "level");
            setInfoMessage(null);
          }}
          onRegister={(seriesId) => void handleRegister(seriesId)}
          searchResults={searchResults}
          isBusy={isBusy}
        />

        <div className="space-y-3">
          <MainSeriesChart points={chartPoints} title={chartTitle} subtitle={chartSubtitle} />
          <RelationshipPanel
            leftSymbol={leftSymbol}
            rightSymbol={rightSymbol}
            onLeftChange={setLeftSymbol}
            onRightChange={setRightSymbol}
            onRun={() => void runRelationship()}
            ratioPoints={ratioPoints}
            spreadPoints={spreadPoints}
            corrPoints={corrPoints}
            betaPoints={betaPoints}
          />
        </div>

        <div className="space-y-3">
          <StatsPanel meta={chartPayload?.meta ?? null} stats={chartPayload?.stats ?? null} />
          <RegimeAlertsPanel latestRegime={latestRegime} currentAlerts={currentAlerts} historyAlerts={historyAlerts} />
        </div>
      </div>
    </div>
  );
}


