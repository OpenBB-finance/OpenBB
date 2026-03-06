import type { ComponentProps } from "react";
import { PanelCard } from "./PanelCard";
import { PortfolioPolicyControlsCard } from "./PortfolioPolicyControlsCard";
import { TrainingConfigSection } from "./TrainingConfigSection";
import { UniverseConfigSection } from "./UniverseConfigSection";

type UniverseSectionProps = ComponentProps<typeof UniverseConfigSection>;
type TrainingSectionProps = ComponentProps<typeof TrainingConfigSection>;
type PolicySectionProps = ComponentProps<typeof PortfolioPolicyControlsCard>;

interface QuantControlsColumnProps {
  universeSection: UniverseSectionProps;
  trainingSection: TrainingSectionProps;
  policySection: PolicySectionProps;
}

export function QuantControlsColumn({
  universeSection,
  trainingSection,
  policySection,
}: QuantControlsColumnProps) {
  return (
    <div className="space-y-4">
      <PanelCard title="Controls" description="Universe, period, model, and run actions">
        <div className="space-y-3">
          <UniverseConfigSection {...universeSection} />
          <TrainingConfigSection {...trainingSection} />
          <PortfolioPolicyControlsCard {...policySection} />
        </div>
      </PanelCard>
    </div>
  );
}
