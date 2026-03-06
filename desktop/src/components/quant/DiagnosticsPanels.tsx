import type {
  AlertsPayload,
  ModelICPayload,
  ModelPerformancePayload,
  ModelRegimePayload,
  ModelShapPayload,
  PortfolioExposurePayload,
  PortfolioRiskPayload,
  RegimeCurrentPayload,
} from "../../types/quant";
import { createActionTargetClickHandler } from "./actionTargetNavigation";
import { PanelCard } from "./PanelCard";

interface DiagnosticsPanelsProps {
  diagnosticsError: string | null;
  modelIcPayload: ModelICPayload | null;
  modelRegimePayload: ModelRegimePayload | null;
  modelShapPayload: ModelShapPayload | null;
  modelPerformancePayload: ModelPerformancePayload | null;
  currentAlertsPayload: AlertsPayload | null;
  portfolioExposurePayload: PortfolioExposurePayload | null;
  portfolioRiskPayload: PortfolioRiskPayload | null;
  regimeCurrentPayload: RegimeCurrentPayload | null;
}

export function DiagnosticsPanels({
  diagnosticsError,
  modelIcPayload,
  modelRegimePayload,
  modelShapPayload,
  modelPerformancePayload,
  currentAlertsPayload,
  portfolioExposurePayload,
  portfolioRiskPayload,
  regimeCurrentPayload,
}: DiagnosticsPanelsProps) {
  const icPoints = modelIcPayload?.points ?? [];
  const latestIcPoint = icPoints.length > 0 ? icPoints[icPoints.length - 1] : null;
  const regimeScenarioCount = Object.keys(modelRegimePayload?.regimes ?? {}).length;
  const shapStatusRaw = String(modelShapPayload?.status ?? "not_loaded");
  const shapStatusLabel = shapStatusRaw === "ok" ? "로드됨" : "미로드";
  const models = modelPerformancePayload?.models ?? [];
  const alerts = currentAlertsPayload?.alerts ?? [];
  const driftAlerts = alerts.filter((item) =>
    ["ic_non_positive_3m", "ic_rolling_drop_6m", "ic_trend_negative"].includes(item.rule_id),
  );
  const criticalAlerts = alerts.filter((item) => item.severity === "critical").length;
  const warningAlerts = alerts.filter((item) => item.severity === "warning").length;
  const infoAlerts = alerts.filter((item) => item.severity === "info").length;
  const factorExposure = portfolioExposurePayload?.factor_exposure ?? {};
  const riskFactorExposure = portfolioRiskPayload?.factor_exposure ?? {};
  const stressTest = portfolioRiskPayload?.stress_test ?? {};
  const topFactorRows = Object.entries(
    Object.keys(factorExposure).length > 0 ? factorExposure : riskFactorExposure,
  )
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 5);
  const topStressRows = Object.entries(stressTest)
    .sort((a, b) => Math.abs(b[1]) - Math.abs(a[1]))
    .slice(0, 4);

  const statItems = [
    {
      label: "IC 데이터 수",
      value: String(icPoints.length),
      status: icPoints.length > 0 ? "ready" : "empty",
      hint: "model/ic 엔드포인트에서 불러온 히스토리",
    },
    {
      label: "레짐 버킷 수",
      value: String(regimeScenarioCount),
      status: regimeScenarioCount > 0 ? "ready" : "empty",
      hint: "레짐 기준 모델 성과 분해",
    },
    {
      label: "SHAP 상태",
      value: shapStatusLabel,
      status: shapStatusRaw === "ok" ? "ready" : "empty",
      hint: "설명가능성(Explainability) 페이로드 준비 상태",
    },
    {
      label: "SHAP 요약 포인트",
      value: String(modelShapPayload?.summary_points?.length ?? 0),
      status: (modelShapPayload?.summary_points?.length ?? 0) > 0 ? "ready" : "empty",
      hint: "요약에 포함된 핵심 피처 수",
    },
  ] as const;

  const statusBadge = (status: "ready" | "empty") =>
    status === "ready" ? (
        <span className="rounded-sm border border-emerald-500/40 bg-emerald-500/10 px-1.5 py-0.5 body-xxs-medium text-emerald-300">
        준비됨
      </span>
    ) : (
      <span className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-1.5 py-0.5 body-xxs-medium text-amber-300">
        대기중
      </span>
    );

  const severityBadge = (severity: "info" | "warning" | "critical") => {
    if (severity === "critical") {
      return (
          <span className="rounded-sm border border-rose-500/40 bg-rose-500/10 px-1.5 py-0.5 body-xxs-medium text-rose-300">
          치명
        </span>
      );
    }
    if (severity === "warning") {
      return (
          <span className="rounded-sm border border-amber-500/40 bg-amber-500/10 px-1.5 py-0.5 body-xxs-medium text-amber-300">
          경고
        </span>
      );
    }
    return (
      <span className="rounded-sm border border-sky-500/40 bg-sky-500/10 px-1.5 py-0.5 body-xxs-medium text-sky-300">
        정보
      </span>
    );
  };

  const metricValue = (value: number | null | undefined, digits = 4) =>
    Number.isFinite(value) ? Number(value).toFixed(digits) : "-";

  const actionSteps: Array<{ href: string; title: string; description: string }> = [
    {
      href: "#quant-action-train",
      title: "1단계 학습 시작",
      description: "모델 학습 실행",
    },
    {
      href: "#quant-action-signals",
      title: "2단계 신호 생성",
      description: "예측 신호 계산",
    },
    {
      href: "#quant-action-backtest",
      title: "3단계 백테스트 실행",
      description: "성과/리스크 점검",
    },
  ];

  const renderActionSteps = () => (
    <div className="mt-2 grid grid-cols-1 gap-1.5 sm:grid-cols-3">
      {actionSteps.map((step) => (
        <a
          key={step.href}
          href={step.href}
          onClick={createActionTargetClickHandler(step.href)}
          className="group rounded-sm border border-sky-500/40 bg-gradient-to-br from-sky-500/15 to-cyan-500/5 px-2.5 py-2 transition hover:border-sky-400/60 hover:from-sky-500/20 hover:to-cyan-500/15"
        >
          <div className="flex items-center justify-between">
            <p className="body-xs-medium text-sky-100">{step.title}</p>
            <span className="body-xxs-medium text-sky-300 transition group-hover:translate-x-0.5">
              {"->"}
            </span>
          </div>
          <p className="mt-0.5 body-xxs-regular text-sky-200/80">{step.description}</p>
        </a>
      ))}
    </div>
  );

  return (
    <>
      <PanelCard title="모델 진단" description="IC / 레짐 / SHAP 상태 요약">
        {diagnosticsError ? (
          <p className="mb-2 body-xs-medium text-amber-300">{diagnosticsError}</p>
        ) : null}
        <div className="grid grid-cols-1 gap-2 sm:grid-cols-2">
          {statItems.map((item) => (
            <div key={item.label} className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <div className="mb-1 flex items-center justify-between">
                <p className="body-xs-medium text-theme-primary">{item.label}</p>
                {statusBadge(item.status)}
              </div>
              <p className="body-sm-medium text-theme-primary">{item.value}</p>
              <p className="mt-1 body-xxs-regular text-theme-muted">{item.hint}</p>
            </div>
          ))}
        </div>
        {icPoints.length === 0 && regimeScenarioCount === 0 && shapStatusRaw !== "ok" ? (
          <div className="mt-2 rounded-sm border border-theme-outline bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">
              진단 데이터가 아직 없습니다. 아래 순서대로 진행해주세요.
            </p>
            {renderActionSteps()}
          </div>
        ) : null}
      </PanelCard>

      <PanelCard title="모델 비교" description="모델별 핵심 지표와 알림 현황">
        <div className="space-y-2">
          {models.length > 0 ? (
            <div className="space-y-1.5">
              {models.map((item) => (
                <div
                  key={item.model_name}
                  className="grid grid-cols-[1.3fr_repeat(3,minmax(0,1fr))] items-center gap-2 rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5"
                >
                  <p className="body-xs-medium text-theme-primary">{item.model_name}</p>
                  <p className="body-xs-regular text-theme-muted">
                    검증 IC {metricValue(item.val_ic, 3)}
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Sharpe {metricValue(item.sharpe, 2)}
                  </p>
                  <p className="body-xs-regular text-theme-muted">
                    Turnover {metricValue(item.turnover, 2)}
                  </p>
                </div>
              ))}
            </div>
          ) : (
            <p className="body-xs-regular text-theme-muted">
              비교 가능한 모델 데이터가 아직 없습니다.
            </p>
          )}
          <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
            <p className="body-xs-medium text-theme-primary">알림 요약</p>
            <p className="mt-1 body-xs-regular text-theme-muted">
              치명 {criticalAlerts} | 경고 {warningAlerts} | 정보 {infoAlerts}
            </p>
          </div>
        </div>
      </PanelCard>

      <PanelCard title="피처 드리프트" description="IC 기반 드리프트 모니터">
        <div className="space-y-2">
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">IC 포인트</p>
              <p className="body-sm-medium text-theme-primary">{icPoints.length}</p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Latest IC</p>
              <p className="body-sm-medium text-theme-primary">{metricValue(latestIcPoint?.ic)}</p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">Rolling IC</p>
              <p className="body-sm-medium text-theme-primary">
                {metricValue(latestIcPoint?.rolling_ic)}
              </p>
            </div>
          </div>
          {driftAlerts.length > 0 ? (
            <div className="space-y-1.5">
              {driftAlerts.slice(0, 6).map((item) => (
                <div
                  key={`${item.rule_id}-${item.triggered_at}`}
                  className="flex items-center justify-between rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5"
                >
                  <div>
                    <p className="body-xs-medium text-theme-primary">{item.rule_id}</p>
                    <p className="body-xxs-regular text-theme-muted">{item.triggered_at}</p>
                  </div>
                  <div className="flex items-center gap-2">
                    <p className="body-xs-regular text-theme-muted">{metricValue(item.value, 3)}</p>
                    {severityBadge(item.severity)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <p className="body-xs-regular text-theme-muted">
              현재 활성화된 드리프트 알림이 없습니다.
            </p>
          )}
        </div>
      </PanelCard>

      <PanelCard title="리스크 스냅샷" description="팩터 익스포저, 스트레스, 레짐 상태">
        <div className="space-y-2">
          <div className="grid grid-cols-3 gap-2">
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">추세 레짐</p>
              <p className="body-sm-medium text-theme-primary">
                {regimeCurrentPayload?.trend_regime ?? "미확인"}
              </p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">변동성 레짐</p>
              <p className="body-sm-medium text-theme-primary">
                {regimeCurrentPayload?.vol_regime ?? "미확인"}
              </p>
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xxs-regular text-theme-muted">유동성 레짐</p>
              <p className="body-sm-medium text-theme-primary">
                {regimeCurrentPayload?.liquidity_regime ?? "미확인"}
              </p>
            </div>
          </div>

          <div className="grid grid-cols-1 gap-2 lg:grid-cols-2">
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xs-medium text-theme-primary">상위 팩터 익스포저</p>
              {topFactorRows.length > 0 ? (
                <div className="mt-1 space-y-1">
                  {topFactorRows.map(([name, value]) => (
                    <div key={name} className="flex items-center justify-between">
                      <span className="body-xxs-regular text-theme-muted">{name}</span>
                      <span className="body-xxs-medium text-theme-primary">{metricValue(value, 3)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-1 body-xxs-regular text-theme-muted">팩터 익스포저 데이터가 없습니다.</p>
              )}
            </div>
            <div className="rounded-sm border border-theme-outline bg-theme-secondary p-2">
              <p className="body-xs-medium text-theme-primary">스트레스 테스트</p>
              {topStressRows.length > 0 ? (
                <div className="mt-1 space-y-1">
                  {topStressRows.map(([name, value]) => (
                    <div key={name} className="flex items-center justify-between">
                      <span className="body-xxs-regular text-theme-muted">{name}</span>
                      <span className="body-xxs-medium text-theme-primary">{metricValue(value, 3)}</span>
                    </div>
                  ))}
                </div>
              ) : (
                <p className="mt-1 body-xxs-regular text-theme-muted">스트레스 시나리오 데이터가 없습니다.</p>
              )}
            </div>
          </div>
        </div>
      </PanelCard>
    </>
  );
}
