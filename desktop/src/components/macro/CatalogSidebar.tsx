import type { MacroCatalogItem } from "../../types/macro";

interface CatalogSidebarProps {
  items: MacroCatalogItem[];
  selectedKey: string;
  searchText: string;
  onSearchTextChange: (next: string) => void;
  onSearch: () => void;
  onSelectKey: (key: string) => void;
  onRegister: (seriesId: string) => void;
  searchResults: MacroCatalogItem[];
  isBusy: boolean;
}

function domainName(item: MacroCatalogItem): string {
  return item.domain || "Custom";
}

export function CatalogSidebar({
  items,
  selectedKey,
  searchText,
  onSearchTextChange,
  onSearch,
  onSelectKey,
  onRegister,
  searchResults,
  isBusy,
}: CatalogSidebarProps) {
  const grouped = items.reduce<Record<string, MacroCatalogItem[]>>((acc, item) => {
    const group = domainName(item);
    if (!acc[group]) {
      acc[group] = [];
    }
    acc[group].push(item);
    return acc;
  }, {});

  return (
    <div className="rounded-sm border border-theme-outline bg-theme-primary p-3">
      <h3 className="body-sm-medium text-theme-primary">Catalog</h3>
      <div className="mt-2 grid grid-cols-[minmax(0,1fr)_auto] gap-2">
        <input
          type="text"
          value={searchText}
          onChange={(event) => onSearchTextChange(event.target.value)}
          placeholder="Search FRED (e.g. unemployment)"
          className="rounded-sm border border-theme-outline bg-theme-secondary p-2 body-xs-regular text-theme-primary"
        />
        <button type="button" className="button-secondary rounded-sm px-2 py-1 body-xs-medium" onClick={onSearch} disabled={isBusy}>
          Search
        </button>
      </div>

      {searchResults.length > 0 ? (
        <div className="mt-2 rounded-sm border border-theme-outline bg-theme-secondary p-2">
          <p className="body-xxs-regular text-theme-muted">Search Results</p>
          <ul className="mt-1 max-h-28 overflow-auto space-y-1">
            {searchResults.slice(0, 15).map((item) => (
              <li key={`result-${item.id}`} className="flex items-center justify-between gap-2">
                <button
                  type="button"
                  className="body-xs-regular text-theme-primary text-left underline-offset-2 hover:underline"
                  onClick={() => onSelectKey(item.id)}
                >
                  {item.series_id}
                </button>
                <button
                  type="button"
                  className="button-secondary rounded-sm px-2 py-0.5 body-xxs-medium"
                  onClick={() => onRegister(item.series_id)}
                >
                  Add
                </button>
              </li>
            ))}
          </ul>
        </div>
      ) : null}

      <div className="mt-3 max-h-[420px] overflow-auto pr-1">
        {Object.entries(grouped).map(([group, rows]) => (
          <div key={group} className="mb-3">
            <p className="body-xs-medium text-theme-muted">{group}</p>
            <ul className="mt-1 space-y-1">
              {rows.map((item) => {
                const key = item.id || `FRED:${item.series_id}`;
                const active = selectedKey === key;
                return (
                  <li key={key}>
                    <button
                      type="button"
                      onClick={() => onSelectKey(key)}
                      className={`w-full rounded-sm px-2 py-1 text-left ${
                        active ? "bg-sky-500/20 text-sky-300" : "bg-theme-secondary text-theme-primary"
                      }`}
                    >
                      <p className="body-xs-medium">{item.series_id}</p>
                      <p className="body-xxs-regular text-theme-muted line-clamp-2">{item.title || item.id}</p>
                    </button>
                  </li>
                );
              })}
            </ul>
          </div>
        ))}
      </div>
    </div>
  );
}
