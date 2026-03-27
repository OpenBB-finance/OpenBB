import { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { PanelCard } from "../quant/PanelCard";
import { MacroRegimeSummary } from "./MacroRegimeSummary";
import { MacroStudyChart } from "./MacroStudyChart";
import { resolveOpenBBBackend } from "../../lib/openbbBackend";
import { openPathSafely } from "../../lib/pathOpener";
import {
  exportMacroFeatures,
  exportMacroReport,
  fetchMacroCatalog,
  fetchMacroCompare,
  fetchMacroHealthWithActivation,
  fetchMacroLeadLag,
  fetchMacroRegime,
  fetchMacroRegimeState,
  fetchMacroReleaseCalendar,
  fetchMacroScatter,
  fetchMacroStudies,
  fetchMacroVintages,
  saveMacroStudy,
} from "../../lib/macroApi";
import { writeMacroStudyHandoff } from "../../lib/macroStudyHandoff";
import { buildSymbolLabHref } from "../../lib/symbolLabNavigation";
import type {
  MacroCatalogItem,
  MacroCompareResponse,
  MacroFeatureExportResponse,
  MacroLeadLagResponse,
  MacroNormalizeMode,
  MacroRegimePoint,
  MacroRegimeStateResponse,
  MacroReleaseCalendarItem,
  MacroScatterResponse,
  MacroStudyPayload,
  MacroStudySeriesSpec,
  MacroVintageResponse,
  MacroViewMode,
} from "../../types/macro";

const DEFAULT_LINKED_ASSETS = ["SPY", "TLT", "GLD"];
const MACRO_VIEW_MODES: MacroViewMode[] = ["explorer", "compare", "relationship", "release", "report"];

function todayIso(): string {
  return new Date().toISOString().slice(0, 10);
}

function yearsAgoIso(years: number): string {
  const d = new Date();
  d.setFullYear(d.getFullYear() - years);
  return d.toISOString().slice(0, 10);
}

function emptyStudy(): MacroStudyPayload {
  return {
    name: "New Macro Study",
    objective: "",
    series_specs: [],
    view_specs: [
      { view_id: "explorer", mode: "explorer", title: "Explorer", layout: {} },
      { view_id: "compare", mode: "compare", title: "Compare", layout: {} },
      { view_id: "relationship", mode: "relationship", title: "Relationship", layout: {} },
      { view_id: "release", mode: "release", title: "Release", layout: {} },
      { view_id: "report", mode: "report", title: "Report", layout: {} },
    ],
    notes: "",
    conclusion: {
      summary: "",
      thesis: "",
      risk_cases: [],
      action_bias: "neutral",
      confidence: null,
      next_checks: [],
    },
    linked_assets: [...DEFAULT_LINKED_ASSETS],
    linked_feature_set_id: null,
  };
}

function studySignature(study: MacroStudyPayload | null): string {
  if (!study) {
    return "";
  }
  return JSON.stringify({
    name: study.name,
    objective: study.objective,
    series_specs: study.series_specs,
    view_specs: study.view_specs,
    notes: study.notes,
    conclusion: study.conclusion,
    linked_assets: study.linked_assets,
    linked_feature_set_id: study.linked_feature_set_id,
  });
}

function parseLines(value: string): string[] {
  return value
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean);
}

function formatLines(value: string[] | undefined | null): string {
  return (value ?? []).join("\n");
}

function safeScore(value: number | null | undefined, digits = 2): string {
  if (value === null || value === undefined || Number.isNaN(value)) {
    return "-";
  }
  return value.toFixed(digits);
}

function isValidAsOfDate(value: string | null): value is string {
  return Boolean(value && /^\d{4}-\d{2}-\d{2}$/.test(value));
}

function isMacroViewMode(value: string | null): value is MacroViewMode {
  return Boolean(value && MACRO_VIEW_MODES.includes(value as MacroViewMode));
}

function buildLineOption(
  payload: MacroCompareResponse | null,
  seriesSpecs: MacroStudySeriesSpec[],
): Record<string, unknown> {
  const keys = Object.keys(payload?.series ?? {});
  const categories = Array.from(
    new Set(keys.flatMap((key) => payload?.series[key]?.data.map((point) => point.date) ?? [])),
  ).sort();
  const specMap = new Map(seriesSpecs.map((spec) => [spec.key, spec]));
  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0, textStyle: { color: "#94a3b8" } },
    grid: { top: 48, right: 48, bottom: 36, left: 48 },
    xAxis: {
      type: "category",
      data: categories,
      axisLabel: { color: "#94a3b8" },
      axisLine: { lineStyle: { color: "#334155" } },
    },
    yAxis: [
      {
        type: "value",
        axisLabel: { color: "#94a3b8" },
        splitLine: { lineStyle: { color: "rgba(148, 163, 184, 0.15)" } },
      },
      {
        type: "value",
        axisLabel: { color: "#94a3b8" },
        splitLine: { show: false },
      },
    ],
    series: keys.map((key) => {
      const spec = specMap.get(key);
      const valueMap = new Map((payload?.series[key]?.data ?? []).map((point) => [point.date, point.value]));
      return {
        name: payload?.series[key]?.meta.title ?? spec?.alias ?? key,
        type: spec?.display_style === "bar" ? "bar" : "line",
        smooth: true,
        yAxisIndex: spec?.axis === "right" ? 1 : 0,
        areaStyle: spec?.display_style === "area" ? { opacity: 0.18 } : undefined,
        showSymbol: false,
        data: categories.map((date) => valueMap.get(date) ?? null),
      };
    }),
  };
}

function buildLeadLagOption(payload: MacroLeadLagResponse | null): Record<string, unknown> {
  return {
    tooltip: { trigger: "axis" },
    grid: { top: 24, right: 16, bottom: 36, left: 48 },
    xAxis: {
      type: "category",
      data: payload?.table.map((item) => String(item.lag)) ?? [],
      axisLabel: { color: "#94a3b8" },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148, 163, 184, 0.15)" } },
    },
    series: [{ type: "bar", data: payload?.table.map((item) => item.correlation) ?? [], itemStyle: { color: "#38bdf8" } }],
  };
}

function buildScatterOption(payload: MacroScatterResponse | null): Record<string, unknown> {
  return {
    tooltip: { trigger: "item" },
    grid: { top: 24, right: 16, bottom: 36, left: 48 },
    xAxis: {
      type: "value",
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148, 163, 184, 0.15)" } },
    },
    yAxis: {
      type: "value",
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148, 163, 184, 0.15)" } },
    },
    series: [{ type: "scatter", symbolSize: 10, data: payload?.points.map((point) => [point.x, point.y, point.date]) ?? [] }],
  };
}

function buildVintageOption(payload: MacroVintageResponse | null): Record<string, unknown> {
  const categories = Array.from(
    new Set([
      ...(payload?.latest?.map((point) => point.date) ?? []),
      ...(payload?.as_of?.map((point) => point.date) ?? []),
    ]),
  ).sort();
  const latestMap = new Map((payload?.latest ?? []).map((point) => [point.date, point.value]));
  const asOfMap = new Map((payload?.as_of ?? []).map((point) => [point.date, point.value]));
  return {
    tooltip: { trigger: "axis" },
    legend: { top: 0, textStyle: { color: "#94a3b8" } },
    grid: { top: 48, right: 16, bottom: 36, left: 48 },
    xAxis: { type: "category", data: categories, axisLabel: { color: "#94a3b8" } },
    yAxis: {
      type: "value",
      axisLabel: { color: "#94a3b8" },
      splitLine: { lineStyle: { color: "rgba(148, 163, 184, 0.15)" } },
    },
    series: [
      { name: "Latest", type: "line", smooth: true, showSymbol: false, data: categories.map((date) => latestMap.get(date) ?? null) },
      { name: "As Of", type: "line", smooth: true, showSymbol: false, data: categories.map((date) => asOfMap.get(date) ?? null) },
    ],
  };
}

async function copyText(value: string): Promise<void> {
  if (typeof navigator !== "undefined" && navigator.clipboard?.writeText) {
    await navigator.clipboard.writeText(value);
    return;
  }
  if (typeof document === "undefined") {
    throw new Error("Clipboard is unavailable in this runtime.");
  }
  const textArea = document.createElement("textarea");
  textArea.value = value;
  textArea.style.position = "fixed";
  textArea.style.opacity = "0";
  document.body.appendChild(textArea);
  textArea.select();
  document.execCommand("copy");
  document.body.removeChild(textArea);
}

async function openLocalPath(path: string | null | undefined) {
  if (!path) {
    return;
  }
  await openPathSafely(path);
}

export default function MacroPage() {
  const [backendBaseUrl, setBackendBaseUrl] = useState("");
  const [isLoading, setIsLoading] = useState(true);
  const [isSaving, setIsSaving] = useState(false);
  const [isExporting, setIsExporting] = useState(false);
  const [errorMessage, setErrorMessage] = useState<string | null>(null);
  const [infoMessage, setInfoMessage] = useState<string | null>(null);
  const [macroReady, setMacroReady] = useState(false);
  const [macroWarnings, setMacroWarnings] = useState<string[]>([]);

  const [catalogItems, setCatalogItems] = useState<MacroCatalogItem[]>([]);
  const [releaseCalendar, setReleaseCalendar] = useState<MacroReleaseCalendarItem[]>([]);
  const [studies, setStudies] = useState<MacroStudyPayload[]>([]);
  const [selectedStudyId, setSelectedStudyId] = useState<string | null>(null);
  const [studyDraft, setStudyDraft] = useState<MacroStudyPayload | null>(null);

  const [searchText, setSearchText] = useState("");
  const [domainFilter, setDomainFilter] = useState("all");
  const [startDate, setStartDate] = useState(yearsAgoIso(12));
  const [endDate, setEndDate] = useState(todayIso());
  const [asOfDate, setAsOfDate] = useState("");
  const [viewMode, setViewMode] = useState<MacroViewMode>("explorer");
  const [normalization, setNormalization] = useState<MacroNormalizeMode>("raw");
  const [comparePayload, setComparePayload] = useState<MacroCompareResponse | null>(null);
  const [leadLagPayload, setLeadLagPayload] = useState<MacroLeadLagResponse | null>(null);
  const [scatterPayload, setScatterPayload] = useState<MacroScatterResponse | null>(null);
  const [vintagePayload, setVintagePayload] = useState<MacroVintageResponse | null>(null);
  const [regimeSeries, setRegimeSeries] = useState<MacroRegimePoint[]>([]);
  const [latestRegime, setLatestRegime] = useState<MacroRegimePoint | null>(null);
  const [regimeState, setRegimeState] = useState<MacroRegimeStateResponse | null>(null);
  const [reportExport, setReportExport] = useState<{ report_path?: string | null } | null>(null);
  const [featureExport, setFeatureExport] = useState<MacroFeatureExportResponse | null>(null);
  const [pathActionError, setPathActionError] = useState<string | null>(null);

  const lastSavedSignatureRef = useRef("");
  const hasHydratedSearchRef = useRef(false);
  const initialSearchRef = useRef({
    studyId: new URLSearchParams(window.location.search).get("studyId"),
    view: new URLSearchParams(window.location.search).get("view"),
    seriesKey: new URLSearchParams(window.location.search).get("seriesKey"),
    query: new URLSearchParams(window.location.search).get("query"),
    domain: new URLSearchParams(window.location.search).get("domain"),
    asOfDate: new URLSearchParams(window.location.search).get("asOfDate"),
  });

  const currentStudy = studyDraft;
  const currentSeriesKeys = currentStudy?.series_specs.map((spec) => spec.key) ?? [];
  const activeRelationPair = useMemo(
    () => currentStudy?.series_specs.slice(0, 2).map((spec) => spec.key) ?? [],
    [currentStudy],
  );

  const filteredCatalog = useMemo(() => {
    const query = searchText.trim().toLowerCase();
    return catalogItems.filter((item) => {
      const domainOk = domainFilter === "all" || (item.domain ?? "unknown") === domainFilter;
      if (!domainOk) {
        return false;
      }
      if (!query) {
        return true;
      }
      return [item.id, item.title ?? "", item.domain ?? "", ...(item.tags ?? [])]
        .join(" ")
        .toLowerCase()
        .includes(query);
    });
  }, [catalogItems, domainFilter, searchText]);

  const domainOptions = useMemo(
    () => ["all", ...Array.from(new Set(catalogItems.map((item) => item.domain).filter(Boolean) as string[])).sort()],
    [catalogItems],
  );

  const studyReleaseItems = useMemo(() => {
    const keySet = new Set(currentSeriesKeys);
    return releaseCalendar.filter((item) => keySet.has(item.key));
  }, [currentSeriesKeys, releaseCalendar]);

  const hydrateStudies = useCallback((items: MacroStudyPayload[]) => {
    const initialSearch = initialSearchRef.current;
    setStudies(items);
    const fallbackStudy = items[0] ?? null;
    const nextStudy =
      items.find((item) => item.id === selectedStudyId) ??
      items.find((item) => item.id === initialSearch.studyId) ??
      fallbackStudy;
    if (nextStudy) {
      setSelectedStudyId(nextStudy.id ?? null);
      setStudyDraft(nextStudy);
      lastSavedSignatureRef.current = studySignature(nextStudy);
      if (initialSearch.studyId && nextStudy.id !== initialSearch.studyId) {
        setInfoMessage(`Study ${initialSearch.studyId} was not found. Loaded the latest available study instead.`);
      }
    } else {
      setSelectedStudyId(null);
      setStudyDraft(emptyStudy());
      lastSavedSignatureRef.current = "";
    }
  }, [selectedStudyId]);

  const loadBootstrap = useCallback(async () => {
    setIsLoading(true);
    setErrorMessage(null);
    try {
      const backend = await resolveOpenBBBackend();
      setBackendBaseUrl(backend.baseUrl);
      if (!backend.connected) {
        setErrorMessage("OpenBB backend is not connected.");
        return;
      }

      const [activationResult, catalog, studyResponse, releaseResponse, regimeResponse, regimeStateResponse] = await Promise.all([
        fetchMacroHealthWithActivation(backend.baseUrl),
        fetchMacroCatalog(backend.baseUrl),
        fetchMacroStudies(backend.baseUrl),
        fetchMacroReleaseCalendar(backend.baseUrl),
        fetchMacroRegime(backend.baseUrl, { start: yearsAgoIso(3), end: todayIso(), freq: "W", fill: "ffill" }).catch(() => null),
        fetchMacroRegimeState(backend.baseUrl).catch(() => null),
      ]);
      setMacroReady(activationResult.activation.available);
      setMacroWarnings(activationResult.data?.warnings ?? []);
      setCatalogItems(catalog.items);
      setReleaseCalendar(releaseResponse.items);
      setRegimeSeries(regimeResponse?.data ?? []);
      setLatestRegime(regimeResponse?.latest ?? regimeResponse?.data?.at(-1) ?? null);
      setRegimeState(regimeStateResponse);
      hydrateStudies(studyResponse.items);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to load Macro Lab.");
    } finally {
      setIsLoading(false);
    }
  }, [hydrateStudies]);

  useEffect(() => {
    void loadBootstrap();
  }, [loadBootstrap]);

  useEffect(() => {
    if (hasHydratedSearchRef.current || studies.length === 0) {
      return;
    }
    hasHydratedSearchRef.current = true;
    const initialSearch = initialSearchRef.current;
    if (initialSearch.query) {
      setSearchText(initialSearch.query);
    }
    if (initialSearch.domain) {
      setDomainFilter(initialSearch.domain);
    }
    if (isValidAsOfDate(initialSearch.asOfDate)) {
      setAsOfDate(initialSearch.asOfDate);
    }
    if (isMacroViewMode(initialSearch.view)) {
      setViewMode(initialSearch.view);
    }
    if (initialSearch.seriesKey) {
      const currentKeys = new Set((studyDraft?.series_specs ?? []).map((spec) => spec.key));
      if (!currentKeys.has(initialSearch.seriesKey)) {
        setInfoMessage(`Series ${initialSearch.seriesKey} is not in the active study basket.`);
      }
    }
  }, [studies.length, studyDraft?.series_specs]);

  const persistStudy = useCallback(
    async (payload: MacroStudyPayload, showInfo = false) => {
      if (!backendBaseUrl) {
        return;
      }
      const signature = studySignature(payload);
      setIsSaving(true);
      try {
        const response = await saveMacroStudy(backendBaseUrl, payload);
        const saved = response.items[0];
        if (!saved) {
          return;
        }
        lastSavedSignatureRef.current = signature;
        setSelectedStudyId(saved.id ?? null);
        setStudyDraft(saved);
        setStudies((previous) => {
          const rest = previous.filter((item) => item.id !== saved.id);
          return [saved, ...rest];
        });
        if (showInfo) {
          setInfoMessage(`Saved study: ${saved.name}`);
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to save study.");
      } finally {
        setIsSaving(false);
      }
    },
    [backendBaseUrl],
  );

  useEffect(() => {
    if (!currentStudy || !backendBaseUrl) {
      return;
    }
    const signature = studySignature(currentStudy);
    if (!signature || signature === lastSavedSignatureRef.current) {
      return;
    }
    const timeoutId = window.setTimeout(() => {
      void persistStudy(currentStudy, false);
    }, 900);
    return () => window.clearTimeout(timeoutId);
  }, [backendBaseUrl, currentStudy, persistStudy]);

  useEffect(() => {
    if (!backendBaseUrl || !currentStudy?.id || !macroReady) {
      return;
    }

    const loadAnalysis = async () => {
      try {
        const [compare, vintageMaybe] = await Promise.all([
          fetchMacroCompare(backendBaseUrl, {
            study_id: currentStudy.id!,
            normalization,
            start: startDate,
            end: endDate,
            as_of_date: asOfDate || undefined,
          }),
          asOfDate && currentStudy.series_specs[0]
            ? fetchMacroVintages(backendBaseUrl, {
                key: currentStudy.series_specs[0].key,
                as_of_date: asOfDate,
                start: startDate,
                end: endDate,
              })
            : Promise.resolve(null),
        ]);
        setComparePayload(compare);
        setVintagePayload(vintageMaybe);

        if (activeRelationPair.length >= 2) {
          const [lhs, rhs] = activeRelationPair;
          const [leadLag, scatter] = await Promise.all([
            fetchMacroLeadLag(backendBaseUrl, {
              lhs,
              rhs,
              start: startDate,
              end: endDate,
              freq: "W",
              fill: "ffill",
              max_lag: 16,
            }),
            fetchMacroScatter(backendBaseUrl, {
              lhs,
              rhs,
              start: startDate,
              end: endDate,
              freq: "W",
              fill: "ffill",
            }),
          ]);
          setLeadLagPayload(leadLag);
          setScatterPayload(scatter);
        } else {
          setLeadLagPayload(null);
          setScatterPayload(null);
        }
      } catch (error) {
        setErrorMessage(error instanceof Error ? error.message : "Failed to load analysis.");
      }
    };

    void loadAnalysis();
  }, [activeRelationPair, asOfDate, backendBaseUrl, currentStudy?.id, currentStudy?.series_specs, endDate, macroReady, normalization, startDate]);

  useEffect(() => {
    if (!backendBaseUrl || !macroReady) {
      return;
    }

    const loadRegimeSummary = async () => {
      try {
        const [regimeResponse, regimeStateResponse] = await Promise.all([
          fetchMacroRegime(backendBaseUrl, {
            start: startDate,
            end: endDate,
            freq: "W",
            fill: "ffill",
          }).catch(() => null),
          fetchMacroRegimeState(backendBaseUrl).catch(() => null),
        ]);
        setRegimeSeries(regimeResponse?.data ?? []);
        setLatestRegime(regimeResponse?.latest ?? regimeResponse?.data?.at(-1) ?? null);
        setRegimeState(regimeStateResponse);
      } catch {
        setRegimeSeries([]);
        setLatestRegime(null);
        setRegimeState(null);
      }
    };

    void loadRegimeSummary();
  }, [backendBaseUrl, endDate, macroReady, startDate]);

  useEffect(() => {
    if (typeof window === "undefined") {
      return;
    }
    const params = new URLSearchParams(window.location.search);
    if (selectedStudyId) {
      params.set("studyId", selectedStudyId);
    } else {
      params.delete("studyId");
    }
    params.set("view", viewMode);
    if (searchText.trim()) {
      params.set("query", searchText.trim());
    } else {
      params.delete("query");
    }
    if (domainFilter && domainFilter !== "all") {
      params.set("domain", domainFilter);
    } else {
      params.delete("domain");
    }
    if (isValidAsOfDate(asOfDate)) {
      params.set("asOfDate", asOfDate);
    } else {
      params.delete("asOfDate");
    }
    const nextSearch = params.toString();
    const nextUrl = `${window.location.pathname}${nextSearch ? `?${nextSearch}` : ""}`;
    window.history.replaceState(window.history.state, "", nextUrl);
  }, [asOfDate, domainFilter, searchText, selectedStudyId, viewMode]);

  const updateStudy = useCallback((updater: (study: MacroStudyPayload) => MacroStudyPayload) => {
    setStudyDraft((previous) => (previous ? updater(previous) : previous));
  }, []);

  const addSeriesToStudy = useCallback((item: MacroCatalogItem) => {
    updateStudy((study) => {
      if (study.series_specs.some((spec) => spec.key === item.id)) {
        return study;
      }
      return {
        ...study,
        series_specs: [
          ...study.series_specs,
          {
            key: item.id,
            alias: item.title ?? item.id,
            transform_chain: [],
            freq: "M",
            fill: "ffill",
            axis: study.series_specs.length % 2 === 0 ? "left" : "right",
            normalize_mode: "raw",
            lag_mode: null,
            display_style: "line",
          },
        ],
      };
    });
  }, [updateStudy]);

  const removeSeriesFromStudy = useCallback((key: string) => {
    updateStudy((study) => ({
      ...study,
      series_specs: study.series_specs.filter((spec) => spec.key !== key),
    }));
  }, [updateStudy]);

  const updateSeriesSpec = useCallback((key: string, patch: Partial<MacroStudySeriesSpec>) => {
    updateStudy((study) => ({
      ...study,
      series_specs: study.series_specs.map((spec) => (spec.key === key ? { ...spec, ...patch } : spec)),
    }));
  }, [updateStudy]);

  const handleCreateStudy = useCallback(() => {
    setSelectedStudyId(null);
    setStudyDraft(emptyStudy());
    lastSavedSignatureRef.current = "";
    setInfoMessage("Created a new study draft.");
  }, []);

  const handleExportReport = useCallback(async () => {
    if (!backendBaseUrl || !currentStudy?.id) {
      return;
    }
    setIsExporting(true);
    try {
      const response = await exportMacroReport(backendBaseUrl, { study_id: currentStudy.id });
      setReportExport(response);
      setInfoMessage(`Report exported to ${response.report_path ?? "reports folder"}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to export report.");
    } finally {
      setIsExporting(false);
    }
  }, [backendBaseUrl, currentStudy?.id]);

  const handleExportFeatures = useCallback(async () => {
    if (!backendBaseUrl || !currentStudy?.id) {
      return;
    }
    setIsExporting(true);
    try {
      const response = await exportMacroFeatures(backendBaseUrl, {
        study_id: currentStudy.id,
        as_of_policy: asOfDate ? `as_of:${asOfDate}` : "latest",
      });
      setFeatureExport(response);
      writeMacroStudyHandoff({
        studyId: currentStudy.id ?? null,
        name: currentStudy.name,
        objective: currentStudy.objective,
        conclusionSummary: currentStudy.conclusion.summary,
        actionBias: currentStudy.conclusion.action_bias,
        linkedAssets: currentStudy.linked_assets ?? [],
        featureArtifactPath: response.artifact_path ?? null,
        asOfPolicy: asOfDate ? `as_of:${asOfDate}` : "latest",
        exportedAt: response.exported_at ?? new Date().toISOString(),
      });
      updateStudy((study) => ({
        ...study,
        linked_feature_set_id: response.artifact_path ?? study.linked_feature_set_id,
      }));
      setInfoMessage(`Feature lineage exported to ${response.artifact_path ?? "artifact store"}.`);
    } catch (error) {
      setErrorMessage(error instanceof Error ? error.message : "Failed to export features.");
    } finally {
      setIsExporting(false);
    }
  }, [asOfDate, backendBaseUrl, currentStudy?.id, updateStudy]);

  const handleOpenPath = useCallback(async (path: string | null | undefined) => {
    try {
      setPathActionError(null);
      await openLocalPath(path);
    } catch (error) {
      setPathActionError(error instanceof Error ? error.message : "Failed to open local path.");
    }
  }, []);

  const handleCopyPath = useCallback(async (path: string | null | undefined) => {
    if (!path) {
      return;
    }
    try {
      await copyText(path);
      setPathActionError(null);
      setInfoMessage(`Copied path: ${path}`);
    } catch (error) {
      setPathActionError(error instanceof Error ? error.message : "Failed to copy local path.");
    }
  }, []);

  const headerTitle = currentStudy?.name ?? "Macro Lab";

  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4 flex flex-wrap items-start justify-between gap-4">
        <div>
          <h1 className="body-lg-medium text-theme-primary">Macro Lab</h1>
          <p className="body-sm-regular text-theme-muted">
            FRED-first research workspace for study building, vintage analysis, release monitoring, and conclusion capture.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <button
            type="button"
            onClick={handleCreateStudy}
            className="rounded-sm border border-theme-outline px-3 py-2 body-sm-medium text-theme-primary"
          >
            New Study
          </button>
          <button
            type="button"
            onClick={() => currentStudy && void persistStudy(currentStudy, true)}
            className="rounded-sm bg-theme-accent px-3 py-2 body-sm-medium text-white disabled:opacity-50"
            disabled={!currentStudy || isSaving}
          >
            {isSaving ? "Saving..." : "Save Study"}
          </button>
        </div>
      </div>

      {errorMessage ? (
        <div className="mb-4 rounded-md border border-red-500/40 bg-red-500/10 px-4 py-3 body-sm-regular text-red-200">
          {errorMessage}
        </div>
      ) : null}
      {infoMessage ? (
        <div className="mb-4 rounded-md border border-emerald-500/40 bg-emerald-500/10 px-4 py-3 body-sm-regular text-emerald-200">
          {infoMessage}
        </div>
      ) : null}

      <div className="mb-4 grid grid-cols-1 gap-4 xl:grid-cols-[340px_minmax(0,1fr)_360px]">
        <PanelCard title="Series Builder" description="Search the local catalog, build the study basket, and tune per-series transforms.">
          <div className="space-y-4">
            <div>
              <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-study-selector">
                Active Study
              </label>
              <select
                id="macro-study-selector"
                className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                value={selectedStudyId ?? ""}
                onChange={(event) => {
                  const next = studies.find((item) => item.id === event.target.value) ?? null;
                  setSelectedStudyId(next?.id ?? null);
                  setStudyDraft(next ?? emptyStudy());
                  lastSavedSignatureRef.current = next ? studySignature(next) : "";
                }}
              >
                {studies.map((study) => (
                  <option key={study.id ?? study.name} value={study.id ?? ""}>
                    {study.name}
                  </option>
                ))}
              </select>
            </div>

            <div className="grid grid-cols-1 gap-3 sm:grid-cols-2">
              <div>
                <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-search">
                  Search Catalog
                </label>
                <input
                  id="macro-search"
                  value={searchText}
                  onChange={(event) => setSearchText(event.target.value)}
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                  placeholder="Search FRED series"
                />
              </div>
              <div>
                <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-domain">
                  Domain
                </label>
                <select
                  id="macro-domain"
                  value={domainFilter}
                  onChange={(event) => setDomainFilter(event.target.value)}
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                >
                  {domainOptions.map((option) => (
                    <option key={option} value={option}>
                      {option}
                    </option>
                  ))}
                </select>
              </div>
            </div>

            <div className="max-h-72 space-y-2 overflow-auto rounded-md border border-theme-outline p-2" data-testid="macro-catalog-results">
              {filteredCatalog.slice(0, 24).map((item) => (
                <button
                  key={item.id}
                  type="button"
                  onClick={() => addSeriesToStudy(item)}
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 text-left transition hover:border-theme-accent"
                >
                  <div className="body-sm-medium text-theme-primary">{item.title ?? item.id}</div>
                  <div className="body-xxs-regular text-theme-muted">
                    {item.id} | {item.domain ?? "unknown"} | last obs {item.last_obs ?? "n/a"}
                  </div>
                </button>
              ))}
            </div>

            <div className="space-y-3" data-testid="macro-study-series">
              <div className="body-sm-medium text-theme-primary">Study Basket</div>
              {(currentStudy?.series_specs ?? []).map((spec) => (
                <div key={spec.key} className="rounded-md border border-theme-outline bg-theme-secondary p-3">
                  <div className="mb-2 flex items-start justify-between gap-2">
                    <div>
                      <div className="body-sm-medium text-theme-primary">{spec.alias ?? spec.key}</div>
                      <div className="body-xxs-regular text-theme-muted">{spec.key}</div>
                    </div>
                    <button
                      type="button"
                      onClick={() => removeSeriesFromStudy(spec.key)}
                      className="body-xxs-medium text-red-300"
                    >
                      Remove
                    </button>
                  </div>
                  <div className="grid grid-cols-1 gap-2">
                    <input
                      value={spec.alias ?? ""}
                      onChange={(event) => updateSeriesSpec(spec.key, { alias: event.target.value })}
                      className="rounded-sm border border-theme-outline bg-theme-primary px-2 py-2 body-xs-regular text-theme-primary"
                      placeholder="Alias"
                    />
                    <div className="grid grid-cols-2 gap-2">
                      <select
                        value={spec.normalize_mode}
                        onChange={(event) => updateSeriesSpec(spec.key, { normalize_mode: event.target.value as MacroNormalizeMode })}
                        className="rounded-sm border border-theme-outline bg-theme-primary px-2 py-2 body-xs-regular text-theme-primary"
                      >
                        <option value="raw">Raw</option>
                        <option value="index100">Index 100</option>
                        <option value="zscore">Z-Score</option>
                        <option value="yoy">YoY</option>
                        <option value="percentile_5y">Percentile 5Y</option>
                      </select>
                      <select
                        value={spec.axis}
                        onChange={(event) => updateSeriesSpec(spec.key, { axis: event.target.value as "left" | "right" })}
                        className="rounded-sm border border-theme-outline bg-theme-primary px-2 py-2 body-xs-regular text-theme-primary"
                      >
                        <option value="left">Left Axis</option>
                        <option value="right">Right Axis</option>
                      </select>
                    </div>
                    <input
                      value={spec.transform_chain.join(", ")}
                      onChange={(event) => updateSeriesSpec(spec.key, {
                        transform_chain: event.target.value.split(",").map((item) => item.trim()).filter(Boolean),
                      })}
                      className="rounded-sm border border-theme-outline bg-theme-primary px-2 py-2 body-xs-regular text-theme-primary"
                      placeholder="Transforms, e.g. yoy, ema:6"
                    />
                  </div>
                </div>
              ))}
              {!currentStudy?.series_specs.length ? (
                <div className="rounded-sm border border-dashed border-theme-outline px-3 py-4 body-sm-regular text-theme-muted">
                  Add at least one series from the catalog to start a study.
                </div>
              ) : null}
            </div>
          </div>
        </PanelCard>

        <div className="space-y-4">
          <PanelCard
            title="Regime Summary"
            description="Levelized macro scores bring the old cycle view back into the active Macro Lab workflow."
          >
            <MacroRegimeSummary
              latestRegime={latestRegime}
              regimeState={regimeState}
              regimeSeries={regimeSeries}
            />
          </PanelCard>

          <PanelCard title={headerTitle} description="Analysis canvas with synchronized views for compare, relationship, release, and report work.">
            <div className="mb-4 flex flex-wrap items-center gap-2">
              {(["explorer", "compare", "relationship", "release", "report"] as MacroViewMode[]).map((mode) => (
                <button
                  key={mode}
                  type="button"
                  onClick={() => setViewMode(mode)}
                  className={`rounded-full px-3 py-1.5 body-xs-medium ${viewMode === mode ? "bg-theme-accent text-white" : "border border-theme-outline text-theme-muted"}`}
                >
                  {mode}
                </button>
              ))}
              <div className="ml-auto flex flex-wrap gap-2">
                <input type="date" value={startDate} onChange={(event) => setStartDate(event.target.value)} className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5 body-xs-regular text-theme-primary" />
                <input type="date" value={endDate} onChange={(event) => setEndDate(event.target.value)} className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5 body-xs-regular text-theme-primary" />
                <input type="date" value={asOfDate} onChange={(event) => setAsOfDate(event.target.value)} className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5 body-xs-regular text-theme-primary" aria-label="As Of Date" />
                <select value={normalization} onChange={(event) => setNormalization(event.target.value as MacroNormalizeMode)} className="rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5 body-xs-regular text-theme-primary">
                  <option value="raw">Raw</option>
                  <option value="index100">Index 100</option>
                  <option value="zscore">Z-Score</option>
                  <option value="yoy">YoY</option>
                  <option value="percentile_5y">Percentile 5Y</option>
                </select>
              </div>
            </div>

            <MacroStudyChart
              title={viewMode === "release" ? "Latest vs As-Of Vintage" : "Study Compare"}
              option={viewMode === "release" ? buildVintageOption(vintagePayload) : buildLineOption(comparePayload, currentStudy?.series_specs ?? [])}
              height={viewMode === "release" ? 360 : 420}
            />

            <div className="mt-4 grid grid-cols-1 gap-4 xl:grid-cols-2">
              <PanelCard
                title={viewMode === "relationship" ? "Lead-Lag Table" : "Relationship Lens"}
                description={viewMode === "release" ? "Vintage metadata and revision diagnostics." : "Scatter and lead-lag views help translate macro relationships into conviction."}
              >
                {viewMode === "relationship" ? (
                  <MacroStudyChart option={buildLeadLagOption(leadLagPayload)} height={240} />
                ) : viewMode === "release" ? (
                  <div className="space-y-2">
                    <div className="body-sm-medium text-theme-primary">Revision Delta</div>
                    <div className="body-lg-medium text-theme-primary">{safeScore(vintagePayload?.revision_delta, 4)}</div>
                    <div className="body-xs-regular text-theme-muted">
                      As-of view only applies to stored FRED vintages. Market series stay on latest mode.
                    </div>
                  </div>
                ) : (
                  <MacroStudyChart option={buildScatterOption(scatterPayload)} height={240} />
                )}
              </PanelCard>

              <PanelCard
                title={viewMode === "relationship" ? "Scatter" : "Release Monitor"}
                description={viewMode === "report" ? "Saved conclusions and linked assets make the report reusable." : "Use freshness, release cadence, and stale markers to decide when the thesis needs refresh."}
              >
                {viewMode === "relationship" ? (
                  <MacroStudyChart option={buildScatterOption(scatterPayload)} height={240} />
                ) : (
                  <div className="space-y-2">
                    {studyReleaseItems.slice(0, 5).map((item) => (
                      <div key={item.key} className="rounded-sm border border-theme-outline px-3 py-2">
                        <div className="body-sm-medium text-theme-primary">{item.title ?? item.key}</div>
                        <div className="body-xxs-regular text-theme-muted">
                          next release {item.estimated_next_release ?? "n/a"} | stale {item.stale_days ?? "n/a"}d | vintage {item.vintage_available ? "yes" : "no"}
                        </div>
                      </div>
                    ))}
                    {!studyReleaseItems.length ? (
                      <div className="body-sm-regular text-theme-muted">No study release metadata yet.</div>
                    ) : null}
                  </div>
                )}
              </PanelCard>
            </div>
          </PanelCard>
        </div>

        <div className="space-y-4">
          <PanelCard title="Insight Drawer" description="Capture the thesis, action mapping, release context, and export actions in one place.">
            <div className="space-y-4">
              <div className="rounded-md border border-theme-outline bg-theme-secondary px-3 py-3">
                <div className="body-sm-medium text-theme-primary">System Status</div>
                <div className="mt-1 body-xs-regular text-theme-muted">
                  backend {backendBaseUrl || "unresolved"} | macro {macroReady ? "ready" : "unavailable"}
                </div>
                {macroWarnings.length ? (
                  <div className="mt-2 body-xxs-regular text-amber-300">{macroWarnings.join(", ")}</div>
                ) : null}
              </div>

              <div>
                <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-study-name">
                  Study Name
                </label>
                <input
                  id="macro-study-name"
                  value={currentStudy?.name ?? ""}
                  onChange={(event) => updateStudy((study) => ({ ...study, name: event.target.value }))}
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                />
              </div>

              <div>
                <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-study-objective">
                  Objective
                </label>
                <textarea
                  id="macro-study-objective"
                  value={currentStudy?.objective ?? ""}
                  onChange={(event) => updateStudy((study) => ({ ...study, objective: event.target.value }))}
                  rows={3}
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                />
              </div>

              <div className="grid grid-cols-1 gap-3">
                <div>
                  <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-summary">
                    Conclusion Summary
                  </label>
                  <textarea
                    id="macro-summary"
                    value={currentStudy?.conclusion.summary ?? ""}
                    onChange={(event) => updateStudy((study) => ({ ...study, conclusion: { ...study.conclusion, summary: event.target.value } }))}
                    rows={2}
                    className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                  />
                </div>
                <div>
                  <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-thesis">
                    Thesis
                  </label>
                  <textarea
                    id="macro-thesis"
                    value={currentStudy?.conclusion.thesis ?? ""}
                    onChange={(event) => updateStudy((study) => ({ ...study, conclusion: { ...study.conclusion, thesis: event.target.value } }))}
                    rows={3}
                    className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                  />
                </div>
                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-action-bias">
                      Action Bias
                    </label>
                    <select
                      id="macro-action-bias"
                      value={currentStudy?.conclusion.action_bias ?? "neutral"}
                      onChange={(event) => updateStudy((study) => ({ ...study, conclusion: { ...study.conclusion, action_bias: event.target.value } }))}
                      className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                    >
                      <option value="bullish">Bullish</option>
                      <option value="neutral">Neutral</option>
                      <option value="defensive">Defensive</option>
                      <option value="risk_on">Risk On</option>
                      <option value="risk_off">Risk Off</option>
                    </select>
                  </div>
                  <div>
                    <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-confidence">
                      Confidence
                    </label>
                    <input
                      id="macro-confidence"
                      type="number"
                      min={0}
                      max={1}
                      step={0.05}
                      value={currentStudy?.conclusion.confidence ?? ""}
                      onChange={(event) => updateStudy((study) => ({
                        ...study,
                        conclusion: { ...study.conclusion, confidence: event.target.value === "" ? null : Number(event.target.value) },
                      }))}
                      className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                    />
                  </div>
                </div>
                <div>
                  <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-risk-cases">
                    Risk Cases
                  </label>
                  <textarea
                    id="macro-risk-cases"
                    value={formatLines(currentStudy?.conclusion.risk_cases)}
                    onChange={(event) => updateStudy((study) => ({ ...study, conclusion: { ...study.conclusion, risk_cases: parseLines(event.target.value) } }))}
                    rows={3}
                    className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                    placeholder="One per line"
                  />
                </div>
                <div>
                  <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-next-checks">
                    Next Checks
                  </label>
                  <textarea
                    id="macro-next-checks"
                    value={formatLines(currentStudy?.conclusion.next_checks)}
                    onChange={(event) => updateStudy((study) => ({ ...study, conclusion: { ...study.conclusion, next_checks: parseLines(event.target.value) } }))}
                    rows={3}
                    className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                    placeholder="One per line"
                  />
                </div>
              </div>

              <div>
                <label className="mb-1 block body-xs-medium text-theme-muted" htmlFor="macro-notes">
                  Draft Notes
                </label>
                <textarea
                  id="macro-notes"
                  value={currentStudy?.notes ?? ""}
                  onChange={(event) => updateStudy((study) => ({ ...study, notes: event.target.value }))}
                  rows={6}
                  className="w-full rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2 body-sm-regular text-theme-primary"
                />
              </div>

              <div className="space-y-2">
                <div className="body-xs-medium text-theme-muted">Linked Assets</div>
                <div className="flex flex-wrap gap-2">
                  {(currentStudy?.linked_assets ?? []).map((asset) => (
                    <a
                      key={asset}
                      href={buildSymbolLabHref({
                        symbol: asset,
                        source: "macro",
                        studyId: currentStudy?.id ?? undefined,
                      })}
                      className="rounded-full border border-theme-outline px-3 py-1 body-xs-medium text-theme-primary"
                    >
                      {asset}
                    </a>
                  ))}
                </div>
              </div>

              <div className="grid grid-cols-1 gap-2">
                <button type="button" onClick={() => void handleExportReport()} disabled={!currentStudy?.id || isExporting} className="rounded-sm border border-theme-outline px-3 py-2 body-sm-medium text-theme-primary disabled:opacity-50">
                  Open Report Export
                </button>
                <button type="button" onClick={() => void handleExportFeatures()} disabled={!currentStudy?.id || isExporting} className="rounded-sm border border-theme-outline px-3 py-2 body-sm-medium text-theme-primary disabled:opacity-50">
                  Export Feature Lineage
                </button>
                {pathActionError ? (
                  <div className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-3 py-2">
                    <p className="body-xxs-regular text-amber-200">{pathActionError}</p>
                  </div>
                ) : null}
                {reportExport?.report_path ? (
                  <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                    <div className="body-xxs-regular text-theme-muted">{reportExport.report_path}</div>
                    <div className="mt-2 flex gap-2">
                      <button type="button" onClick={() => void handleOpenPath(reportExport.report_path)} className="body-xs-medium text-theme-accent">Open Report</button>
                      <button type="button" onClick={() => void handleOpenPath(reportExport.report_path?.split(/[/\\]/).slice(0, -1).join("/"))} className="body-xs-medium text-theme-accent">Open Folder</button>
                      <button type="button" onClick={() => void handleCopyPath(reportExport.report_path)} className="body-xs-medium text-theme-accent">Copy Path</button>
                    </div>
                  </div>
                ) : null}
                {featureExport?.artifact_path ? (
                  <div className="rounded-sm border border-theme-outline bg-theme-secondary px-3 py-2">
                    <div className="body-xxs-regular text-theme-muted">{featureExport.artifact_path}</div>
                    <div className="mt-2 flex gap-2">
                      <button type="button" onClick={() => void handleOpenPath(featureExport.artifact_path)} className="body-xs-medium text-theme-accent">Open Export</button>
                      <button type="button" onClick={() => void handleCopyPath(featureExport.artifact_path)} className="body-xs-medium text-theme-accent">Copy Path</button>
                      <button type="button" onClick={() => updateStudy((study) => ({ ...study, linked_feature_set_id: featureExport.artifact_path ?? study.linked_feature_set_id }))} className="body-xs-medium text-theme-accent">Attach To Study</button>
                    </div>
                  </div>
                ) : null}
              </div>
            </div>
          </PanelCard>
        </div>
      </div>

      {isLoading ? (
        <div className="rounded-md border border-theme-outline px-4 py-6 body-sm-regular text-theme-muted">
          Loading Macro Lab...
        </div>
      ) : null}
    </div>
  );
}
