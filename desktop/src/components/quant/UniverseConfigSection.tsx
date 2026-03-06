import type { UniverseResponse } from "../../types/quant";

interface UniverseSetOptionView {
  id: string;
  label: string;
  countHint?: number;
  hasFile?: boolean;
  minimumRequired?: number;
}

interface UniverseResolveStateView {
  status: "idle" | "loading" | "ok" | "error";
  message: string | null;
  count: number | null;
  minimumRequired: number;
  meetsMinimum: boolean;
}

interface UniverseProfileOptionView {
  id: string;
  label: string;
  description: string;
}

interface UniverseConfigSectionProps {
  universeSetOptions: UniverseSetOptionView[];
  selectedUniverseSet: string;
  onUniverseSetChange: (value: string) => void;
  isUniverseSetMode: boolean;
  universeResolveState: UniverseResolveStateView;
  profiles: UniverseProfileOptionView[];
  selectedProfile: string;
  profileLabel: string;
  onProfileSelect: (profileId: string) => void;
  universe: UniverseResponse | null;
  symbolsInput: string;
  onSymbolsInputChange: (value: string) => void;
  onFormatSymbols: () => void;
  onClearSymbols: () => void;
  parsedSymbolsCount: number;
  dateStart: string;
  dateEnd: string;
  onDateStartChange: (value: string) => void;
  onDateEndChange: (value: string) => void;
}

export function UniverseConfigSection({
  universeSetOptions,
  selectedUniverseSet,
  onUniverseSetChange,
  isUniverseSetMode,
  universeResolveState,
  profiles,
  selectedProfile,
  profileLabel,
  onProfileSelect,
  universe,
  symbolsInput,
  onSymbolsInputChange,
  onFormatSymbols,
  onClearSymbols,
  parsedSymbolsCount,
  dateStart,
  dateEnd,
  onDateStartChange,
  onDateEndChange,
}: UniverseConfigSectionProps) {
  return (
    <>
      <div>
        <label htmlFor="quant-universe-set" className="body-xs-medium text-theme-muted">
          Universe Set
        </label>
        <select
          id="quant-universe-set"
          className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
          value={selectedUniverseSet}
          onChange={(event) => onUniverseSetChange(event.target.value)}
        >
          {universeSetOptions.map((option) => {
            const suffix =
              option.countHint !== undefined
                ? ` (${option.countHint}${
                    option.minimumRequired ? ` / min ${option.minimumRequired}` : ""
                  })`
                : option.minimumRequired
                  ? ` (min ${option.minimumRequired})`
                  : "";
            const missing =
              option.id !== "default" && option.hasFile === false ? " [missing]" : "";
            return (
              <option key={option.id} value={option.id}>
                {option.label}
                {suffix}
                {missing}
              </option>
            );
          })}
        </select>
        <p className="mt-1 body-xs-regular text-theme-muted">
          {isUniverseSetMode
            ? "Universe set mode is active. Train request will send universe_id only."
            : "Default mode is active. Train request will use symbols from textarea."}
        </p>
        {isUniverseSetMode && universeResolveState.status === "loading" ? (
          <p className="mt-1 body-xs-regular text-theme-muted">
            Resolving universe set symbols...
          </p>
        ) : null}
        {isUniverseSetMode && universeResolveState.status === "ok" ? (
          <p className="mt-1 body-xs-regular text-emerald-300">
            Resolved {universeResolveState.count ?? 0} symbols
            {universeResolveState.minimumRequired > 0
              ? ` (minimum ${universeResolveState.minimumRequired})`
              : ""}
            .
          </p>
        ) : null}
        {isUniverseSetMode && universeResolveState.status === "error" ? (
          <p className="mt-1 body-xs-medium text-amber-300">
            {universeResolveState.message ??
              "Selected universe set is invalid or undersized. Run refresh_universes --all --no-validate."}
          </p>
        ) : null}
      </div>

      <div>
        <p className="body-xs-medium text-theme-muted">Universe Profile</p>
        <div className="mt-1 flex flex-wrap gap-2">
          {profiles.map((profile) => (
            <button
              key={profile.id}
              type="button"
              className={`rounded-sm px-2 py-1 body-xs-medium ${
                selectedProfile === profile.id ? "button-neutral" : "button-secondary"
              }`}
              onClick={() => onProfileSelect(profile.id)}
              disabled={!universe || isUniverseSetMode}
              title={profile.description}
            >
              {profile.id === "all" && universe ? `All (${universe.assets.length})` : profile.label}
            </button>
          ))}
          <span className="rounded-sm bg-theme-secondary px-2 py-1 body-xs-regular text-theme-muted">
            Current: {profileLabel}
          </span>
        </div>
      </div>

      <div>
        <label htmlFor="quant-symbols" className="body-xs-medium text-theme-muted">
          Symbols (comma/newline separated)
        </label>
        <textarea
          id="quant-symbols"
          className="mt-1 h-28 w-full resize-y rounded-sm border border-theme-outline bg-theme-secondary p-2 font-mono text-[13px] !leading-6 tracking-normal text-theme-primary"
          value={symbolsInput}
          spellCheck={false}
          placeholder="SPY, QQQ, TLT ..."
          onChange={(event) => onSymbolsInputChange(event.target.value)}
          disabled={isUniverseSetMode}
        />
        <div className="mt-2 flex gap-2">
          <button
            type="button"
            className="button-secondary rounded-sm px-2 py-1 body-xs-medium"
            onClick={onFormatSymbols}
            disabled={isUniverseSetMode}
          >
            Format
          </button>
          <button
            type="button"
            className="button-secondary rounded-sm px-2 py-1 body-xs-medium"
            onClick={onClearSymbols}
            disabled={isUniverseSetMode}
          >
            Clear
          </button>
        </div>
        <p className="mt-1 body-xs-regular text-theme-muted">
          Parsed symbols: {parsedSymbolsCount}
          {universe ? ` / Universe version: ${universe.version}` : ""}
        </p>
      </div>

      <div className="grid grid-cols-2 gap-2">
        <label className="body-xs-medium text-theme-muted">
          Start
          <input
            type="date"
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={dateStart}
            onChange={(event) => onDateStartChange(event.target.value)}
          />
        </label>
        <label className="body-xs-medium text-theme-muted">
          End
          <input
            type="date"
            className="mt-1 w-full rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
            value={dateEnd}
            onChange={(event) => onDateEndChange(event.target.value)}
          />
        </label>
      </div>
    </>
  );
}
