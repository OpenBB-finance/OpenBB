import { createFileRoute } from "@tanstack/react-router";
import { PanelCard } from "../components/quant/PanelCard";

const SETTINGS_CARDS = [
  {
    title: "Backends",
    description: "Manage the OpenBB API target and backend process detection.",
    to: "/backends" as const,
  },
  {
    title: "Environments",
    description: "Choose the working directory and local environment layout.",
    to: "/environments" as const,
  },
  {
    title: "API Keys",
    description: "Set credentials for FRED and other integrations without mixing them into research workflows.",
    to: "/api-keys" as const,
  },
];

function SettingsPage() {
  return (
    <div className="h-full min-h-0 overflow-auto py-4">
      <div className="mb-4">
        <h1 className="body-lg-medium text-theme-primary">Settings</h1>
        <p className="body-sm-regular text-theme-muted">
          Settings and integrations live here so the top navigation stays focused on research, strategy, execution, and ops.
        </p>
      </div>

      <div className="grid grid-cols-1 gap-4 xl:grid-cols-3">
        {SETTINGS_CARDS.map((card) => (
          <PanelCard key={card.title} title={card.title} description={card.description}>
            <a href={card.to} className="body-sm-medium text-theme-accent">
              Open {card.title}
            </a>
          </PanelCard>
        ))}
      </div>
    </div>
  );
}

export const Route = createFileRoute("/settings")({
  component: SettingsPage,
});
