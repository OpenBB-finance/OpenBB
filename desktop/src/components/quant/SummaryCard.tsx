import type { ReactNode } from "react";

export type SummaryStatus = "ok" | "warning" | "critical";

interface SummaryCardProps {
  label: string;
  value: string | number | ReactNode;
  status?: SummaryStatus;
  actionLabel?: string;
  actionHref?: string;
}

export function SummaryCard({
  label,
  value,
  status = "ok",
  actionLabel,
  actionHref,
}: SummaryCardProps) {
  const statusStyles =
    status === "warning"
      ? "border-amber-500/50 bg-amber-500/5"
      : status === "critical"
        ? "border-red-500/50 bg-red-500/5"
        : "border-theme-outline bg-theme-primary";

  return (
    <div className={`rounded-sm border p-3 ${statusStyles}`}>
      <p className="body-xxs-regular text-theme-muted">{label}</p>
      <div className="mt-1 body-xs-medium text-theme-primary">{value}</div>
      {actionLabel && actionHref ? (
        <a
          href={actionHref}
          className="mt-2 inline-block body-xxs-medium text-sky-400 hover:text-sky-300"
        >
          {actionLabel}
        </a>
      ) : null}
    </div>
  );
}
