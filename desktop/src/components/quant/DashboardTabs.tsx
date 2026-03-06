import type { ReactNode } from "react";

export type DashboardTabId = "summary" | "performance" | "risk" | "portfolio" | "model" | "regime";

const TAB_CONFIG: Array<{ id: DashboardTabId; label: string }> = [
  { id: "summary", label: "Summary" },
  { id: "performance", label: "Performance" },
  { id: "risk", label: "Risk" },
  { id: "portfolio", label: "Portfolio" },
  { id: "model", label: "Model" },
  { id: "regime", label: "Regime" },
];

interface DashboardTabsProps {
  activeTab: DashboardTabId;
  onTabChange: (tab: DashboardTabId) => void;
  children: Record<DashboardTabId, ReactNode>;
}

export function DashboardTabs({ activeTab, onTabChange, children }: DashboardTabsProps) {
  return (
    <div className="space-y-4">
      <div
        className="flex flex-wrap gap-1 border-b border-theme-outline pb-2"
        role="tablist"
        aria-label="Dashboard sections"
      >
        {TAB_CONFIG.map((tab) => (
          <button
            key={tab.id}
            type="button"
            role="tab"
            aria-selected={activeTab === tab.id}
            aria-controls={`panel-${tab.id}`}
            id={`tab-${tab.id}`}
            className={`rounded-sm px-3 py-2 body-xs-medium transition-colors ${
              activeTab === tab.id
                ? "bg-sky-500/20 text-sky-300 border border-sky-500/50"
                : "bg-theme-secondary text-theme-muted hover:bg-theme-outline/30 hover:text-theme-primary"
            }`}
            onClick={() => onTabChange(tab.id)}
          >
            {tab.label}
          </button>
        ))}
      </div>
      <div
        id={`panel-${activeTab}`}
        role="tabpanel"
        aria-labelledby={`tab-${activeTab}`}
        className="min-h-0"
      >
        {children[activeTab]}
      </div>
    </div>
  );
}
