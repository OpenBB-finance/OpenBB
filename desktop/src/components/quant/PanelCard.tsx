import type { ReactNode } from "react";

interface PanelCardProps {
  title: string;
  description?: string;
  children: ReactNode;
}

export function PanelCard({ title, description, children }: PanelCardProps) {
  return (
    <section className="rounded-md border border-theme-outline bg-theme-primary p-4">
      <header className="mb-3">
        <h2 className="body-md-medium text-theme-primary">{title}</h2>
        {description ? (
          <p className="mt-1 body-xs-regular text-theme-muted">{description}</p>
        ) : null}
      </header>
      {children}
    </section>
  );
}
