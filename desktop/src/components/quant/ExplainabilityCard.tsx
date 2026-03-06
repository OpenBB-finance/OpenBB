import type { ArtifactSummaryPayload } from "../../types/quant";
import { createActionTargetClickHandler } from "./actionTargetNavigation";
import { PanelCard } from "./PanelCard";

interface ExplainabilityCardProps {
  summary: ArtifactSummaryPayload | null;
}

export function ExplainabilityCard({ summary }: ExplainabilityCardProps) {
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
    <PanelCard
      title="설명가능성 (Explainability)"
      description="피처 중요도, 검증 오차, 아티팩트 준비 상태"
    >
      {!summary ? (
        <div className="rounded-sm border border-theme-outline bg-theme-secondary p-3">
          <p className="body-sm-medium text-theme-primary">설명가능성 데이터가 아직 없습니다</p>
          <p className="mt-1 body-xs-regular text-theme-muted">
            학습 완료 후 Completed Run을 불러오면 피처 중요도와 검증 진단을 확인할 수 있습니다.
          </p>
          {renderActionSteps()}
        </div>
      ) : (
        <div className="space-y-3">
          <div className="rounded-sm bg-theme-secondary p-2">
            <p className="body-xs-regular text-theme-muted">최근 검증 오차</p>
            <p className="body-sm-medium text-theme-primary">{summary.latest_validation_error ?? "-"}</p>
          </div>

          <div>
            <p className="body-xs-medium text-theme-muted">상위 중요 피처</p>
            <ul className="mt-1 space-y-1">
              {summary.feature_importance.slice(0, 8).map((item) => (
                <li
                  key={item.feature}
                  className="flex items-center justify-between rounded-sm bg-theme-secondary px-2 py-1"
                >
                  <span className="body-xs-regular text-theme-primary">{item.feature}</span>
                  <span className="body-xs-regular text-theme-muted">{item.importance.toFixed(4)}</span>
                </li>
              ))}
            </ul>
          </div>

          <div>
            <p className="body-xs-medium text-theme-muted">아티팩트</p>
            <p className="body-xs-regular text-theme-primary">
              {summary.available_artifacts.length > 0
                ? summary.available_artifacts.join(", ")
                : "아티팩트가 없습니다."}
            </p>
          </div>
        </div>
      )}
    </PanelCard>
  );
}
