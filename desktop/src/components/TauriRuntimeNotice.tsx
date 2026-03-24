interface TauriRuntimeNoticeProps {
  title: string;
  description?: string;
}

export function TauriRuntimeNotice({
  title,
  description = "Open this tab in the desktop app to access local services, filesystem features, and Tauri commands.",
}: TauriRuntimeNoticeProps) {
  return (
    <div className="flex h-full w-full items-center justify-center px-6 py-10">
      <div className="w-full max-w-2xl rounded-lg border border-theme-outline bg-theme-secondary p-6 shadow-sm">
        <p className="body-xs-medium uppercase tracking-[0.12em] text-theme-muted">Desktop runtime required</p>
        <h1 className="mt-2 body-lg-bold text-theme-primary">{title}</h1>
        <p className="mt-3 body-sm text-theme-secondary">{description}</p>
      </div>
    </div>
  );
}
