import { useCallback, useEffect, useState } from "react";
import { resolveOpenBBBackend } from "../../lib/openbbBackend";
import {
  evaluateMacroExpression,
  fetchCopperGoldPreset,
  fetchMacroHealth,
  fetchMacroHealthWithActivation,
  fetchMarketRatio,
  fetchMarketRollingCorr,
  fetchMacroAlerts,
  fetchMacroCatalog,
  fetchMacroDerived,
  fetchMacroRegime,
  fetchMacroRegimeState,
  fetchMacroSeries,
  fetchMacroSeriesMulti,
  invalidateMacroCache,
  registerMacroSeries,
  saveMacroDerived,
  searchMacroCatalog,
  triggerMacroUpdate,
} from "../../lib/macroApi";
import type { FeatureActivation } from "../../types/feature-activation";
import type {
  MacroAlertItem,
  MacroCatalogItem,
  MacroDataPoint,
  MacroExpressionResponse,
  MacroHealthResponse,
  MacroPresetResponse,
  MacroFill,
  MacroFreq,
  MacroRegimePoint,
  MacroRegimeStateResponse,
  MacroSeriesResponse,
  MacroSeriesMultiResponse,
} from "../../types/macro";
import { CatalogSidebar } from "./CatalogSidebar";
import { ExpressionBar } from "./ExpressionBar";
import { MainSeriesChart } from "./MainSeriesChart";
import { MultiSeriesComparePanel } from "./MultiSeriesComparePanel";
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

function parseCompareKeys(raw: string): string[] {
  const seen = new Set<string>();
  const out: string[] = [];
  for (const token of raw.split(",")) {
    const key = token.trim();
    if (!key) {
      continue;
    }
    if (!seen.has(key)) {
      seen.add(key);
      out.push(key);
    }
  }
  return out;
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
  const [macroActivation, setMacroActivation] = useState<FeatureActivation | null>(null);
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
  const [compareKeys, setCompareKeys] = useState("FRED:UNRATE,FRED:CPIAUCSL,FRED:FEDFUNDS");
  const [seriesMultiPayload, setSeriesMultiPayload] = useState<MacroSeriesMultiResponse | null>(null);
  const [seriesMultiError, setSeriesMultiError] = useState<string | null>(null);

  const [ratioPoints, setRatioPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [spreadPoints, setSpreadPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [corrPoints, setCorrPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [betaPoints, setBetaPoints] = useState<Array<{ date: string; value: number }>>([]);
  const [leftSymbol, setLeftSymbol] = useState("FRED:DGS10");
  const [rightSymbol, setRightSymbol] = useState("FRED:DGS2");
  const [ratioTicker, setRatioTicker] = useState("GLD/SPY");
  const [corrWindow, setCorrWindow] = useState(60);

  const [latestRegime, setLatestRegime] = useState<MacroRegimePoint | null>(null);
  const [regimeState, setRegimeState] = useState<MacroRegimeStateResponse | null>(null);
  const [currentAlerts, setCurrentAlerts] = useState<MacroAlertItem[]>([]);
  const [historyAlerts, setHistoryAlerts] = useState<MacroAlertItem[]>([]);
  const [macroHealth, setMacroHealth] = useState<MacroHealthResponse | null>(null);
  const [copperGoldPreset, setCopperGoldPreset] = useState<MacroPresetResponse | null>(null);

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

  const checkMacroActivation = useCallback(async () => {
    if (!backendBaseUrl) {
      return false;
    }
    const activationResult = await fetchMacroHealthWithActivation(backendBaseUrl);
    setMacroActivation(activationResult.activation);
    if (!activationResult.activation.available) {
      setErrorMessage(
        activationResult.activation.detail ||
          "macro extension unavailable. Install/enable openbb-quant-ml.",
      );
      return false;
    }
    if (activationResult.data) {
      setMacroHealth(activationResult.data);
    }
    return true;
  }, [backendBaseUrl]);

  const runSeriesMultiCompare = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    const ids = parseCompareKeys(compareKeys);
    if (ids.length < 2) {
      setSeriesMultiPayload(null);
      setSeriesMultiError("Provide at least two keys for multi-series comparison.");
      return;
    }
    try {
      const response = await fetchMacroSeriesMulti(backendBaseUrl, {
        ids,
        start: startDate,
        end: endDate,
        transform: "level",
        freq,
        fill,
      });
      setSeriesMultiPayload(response);
      if (response.status !== "ok") {
        setSeriesMultiError(response.message || "Multi-series comparison returned no data.");
      } else {
        setSeriesMultiError(null);
      }
    } catch (error) {
      setSeriesMultiPayload(null);
      setSeriesMultiError(toFriendlyError(error));
    }
  }, [backendBaseUrl, compareKeys, endDate, fill, freq, startDate]);

  const refreshRegimeAndAlerts = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    const [regime, alerts] = await Promise.all([
      fetchMacroRegime(backendBaseUrl, { start: startDate, end: endDate, freq: "W", fill: "ffill" }),
      fetchMacroAlerts(backendBaseUrl, { start: startDate, end: endDate, limit: 200 }),
    ]);
    try {
      const state = await fetchMacroRegimeState(backendBaseUrl, endDate);
      setRegimeState(state);
    } catch {
      setRegimeState(null);
    }
    const regimePoints = Array.isArray(regime.data) ? regime.data : [];
    setLatestRegime(regime.latest || (regimePoints.length > 0 ? regimePoints[regimePoints.length - 1] : null));
    setCurrentAlerts(normalizeAlerts(alerts.current));
    setHistoryAlerts(normalizeAlerts(alerts.history));
  }, [backendBaseUrl, endDate, startDate]);

  const refreshDiagnostics = useCallback(async () => {
    if (!backendBaseUrl) {
      return;
    }
    const [health, preset] = await Promise.all([
      fetchMacroHealth(backendBaseUrl),
      fetchCopperGoldPreset(backendBaseUrl, {
        start: startDate,
        end: endDate,
        freq: "W",
        fill: "ffill",
        adjust_units: true,
        include_corr: true,
      }),
    ]);
    setMacroHealth(health);
    setCopperGoldPreset(preset);
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
        fetchMarketRatio(backendBaseUrl, {
          lhs: (ratioTicker.split("/")[0] || leftSymbol).trim(),
          rhs: (ratioTicker.split("/")[1] || rightSymbol).trim(),
          start: startDate,
          end: endDate,
          freq,
          fill,
        }),
        evaluateMacroExpression(backendBaseUrl, {
          expr: `${leftSymbol}-${rightSymbol}`,
          start: startDate,
          end: endDate,
          freq,
          fill,
          transform: "level",
        }),
        fetchMarketRollingCorr(backendBaseUrl, {
          x: leftSymbol,
          y: rightSymbol,
          window: corrWindow,
          start: startDate,
          end: endDate,
          freq,
          fill,
        }),
        evaluateMacroExpression(backendBaseUrl, {
          expr: `rolling_beta(${leftSymbol},${rightSymbol},${corrWindow})`,
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
  }, [backendBaseUrl, corrWindow, endDate, fill, freq, leftSymbol, ratioTicker, rightSymbol, startDate]);

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
      const response = await triggerMacroUpdate(backendBaseUrl, {
        all_default: true,
        start: startDate,
        end: endDate,
        compute_features: true,
        features_lookback_days: 365,
      });
      invalidateMacroCache();
      await loadCatalog();
      await refreshRegimeAndAlerts();
      await refreshDiagnostics();
      await runSeriesMultiCompare();
      setInfoMessage(response.message || `Updated ${response.updated_series.length} series.`);
    } catch (error) {
      setErrorMessage(toFriendlyError(error));
    } finally {
      setIsBusy(false);
    }
  }, [
    backendBaseUrl,
    endDate,
    loadCatalog,
    refreshDiagnostics,
    refreshRegimeAndAlerts,
    runSeriesMultiCompare,
    startDate,
  ]);

  useEffect(() => {
    void resolveBackend();
  }, [resolveBackend]);

  useEffect(() => {
    if (!backendBaseUrl) {
      return;
    }
    void (async () => {
      try {
        const active = await checkMacroActivation();
        if (!active) {
          return;
        }
        await loadCatalog();
        await runExpression();
        await runRelationship();
        await runSeriesMultiCompare();
        await refreshRegimeAndAlerts();
        await refreshDiagnostics();
      } catch (error) {
        setErrorMessage(toFriendlyError(error));
      }
    })();
  }, [
    backendBaseUrl,
    checkMacroActivation,
    loadCatalog,
    refreshDiagnostics,
    refreshRegimeAndAlerts,
    runExpression,
    runRelationship,
    runSeriesMultiCompare,
  ]);

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
      {macroActivation && !macroActivation.available ? (
        <div className="mb-2 rounded-sm border border-amber-500/60 bg-amber-500/10 p-2">
          <p className="body-xs-medium text-amber-300">
            macro extension unavailable: {macroActivation.detail || "Install/enable openbb-quant-ml."}
          </p>
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
          void runSeriesMultiCompare();
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
          <MultiSeriesComparePanel
            compareKeys={compareKeys}
            onCompareKeysChange={setCompareKeys}
            onRefresh={() => void runSeriesMultiCompare()}
            isBusy={isBusy}
            payload={seriesMultiPayload}
            errorMessage={seriesMultiError}
          />
          <RelationshipPanel
            leftSymbol={leftSymbol}
            rightSymbol={rightSymbol}
            ratioTicker={ratioTicker}
            onRatioTickerChange={setRatioTicker}
            onLeftChange={setLeftSymbol}
            onRightChange={setRightSymbol}
            corrWindow={corrWindow}
            onCorrWindowChange={setCorrWindow}
            onRun={() => void runRelationship()}
            ratioPoints={ratioPoints}
            spreadPoints={spreadPoints}
            corrPoints={corrPoints}
            betaPoints={betaPoints}
          />
        </div>

        <div className="space-y-3">
          <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
            <p className="body-xs-medium text-theme-primary">Macro Health</p>
            <p className="body-xxs-regular text-theme-muted mt-1">
              status: {macroHealth?.status ?? "unknown"} | obs: {macroHealth?.obs_stats?.last_obs_date_global ?? "-"} | feat:{" "}
              {macroHealth?.feature_stats?.last_feature_date ?? "-"}
            </p>
            {Array.isArray(macroHealth?.warnings) && macroHealth!.warnings.length > 0 ? (
              <p className="body-xxs-regular text-amber-400 mt-1">{macroHealth?.warnings.join(" | ")}</p>
            ) : null}
          </div>
          <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
            <p className="body-xs-medium text-theme-primary">Copper/Gold Preset</p>
            <p className="body-xxs-regular text-theme-muted mt-1">
              status: {copperGoldPreset?.status ?? "unknown"} | series: {copperGoldPreset?.series?.length ?? 0} | events:{" "}
              {copperGoldPreset?.events?.length ?? 0}
            </p>
            {copperGoldPreset?.message ? <p className="body-xxs-regular text-theme-muted mt-1">{copperGoldPreset.message}</p> : null}
            {Array.isArray(copperGoldPreset?.events) && copperGoldPreset!.events.length > 0 ? (
              <div className="mt-2 space-y-1">
                {copperGoldPreset!.events.slice(0, 3).map((event) => (
                  <p key={`${event.date}-${event.event_type}`} className="body-xxs-regular text-theme-primary">
                    {event.date} | {event.event_type}
                  </p>
                ))}
              </div>
            ) : null}
          </div>
          <StatsPanel meta={chartPayload?.meta ?? null} stats={chartPayload?.stats ?? null} />
          <RegimeAlertsPanel
            latestRegime={latestRegime}
            regimeState={regimeState}
            currentAlerts={currentAlerts}
            historyAlerts={historyAlerts}
          />
        </div>
      </div>
    </div>
  );
}


