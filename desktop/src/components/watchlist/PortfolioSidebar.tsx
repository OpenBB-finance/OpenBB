import { useCallback, useState } from "react";
import { WatchlistTickerRow } from "./WatchlistTickerRow";
import type { QuoteRecord, WatchlistGroup } from "../../lib/watchlistApi";

interface PortfolioSidebarProps {
  groups: WatchlistGroup[];
  quotes: Map<string, QuoteRecord>;
  activeSymbol: string;
  onSelectSymbol: (symbol: string) => void;
  onAddTicker: (groupName: string, symbol: string) => void;
  onRemoveTicker: (groupName: string, symbol: string) => void;
  onAddGroup: (name: string) => void;
}

export function PortfolioSidebar({
  groups,
  quotes,
  activeSymbol,
  onSelectSymbol,
  onAddTicker,
  onRemoveTicker,
  onAddGroup,
}: PortfolioSidebarProps) {
  const [collapsedGroups, setCollapsedGroups] = useState<Set<string>>(new Set());
  const [addingTickerGroup, setAddingTickerGroup] = useState<string | null>(null);
  const [tickerInput, setTickerInput] = useState("");
  const [addGroupInput, setAddGroupInput] = useState("");
  const [showAddGroup, setShowAddGroup] = useState(false);

  const toggleGroup = useCallback((name: string) => {
    setCollapsedGroups((prev) => {
      const next = new Set(prev);
      if (next.has(name)) {
        next.delete(name);
      } else {
        next.add(name);
      }
      return next;
    });
  }, []);

  const handleAddTicker = useCallback(
    (groupName: string) => {
      const symbol = tickerInput.trim().toUpperCase();
      if (!symbol) {
        return;
      }
      onAddTicker(groupName, symbol);
      setTickerInput("");
      setAddingTickerGroup(null);
    },
    [onAddTicker, tickerInput],
  );

  const handleAddGroup = useCallback(() => {
    const name = addGroupInput.trim();
    if (!name) {
      return;
    }
    onAddGroup(name);
    setAddGroupInput("");
    setShowAddGroup(false);
  }, [addGroupInput, onAddGroup]);

  return (
    <div className="flex h-full flex-col rounded-sm border border-theme-outline bg-theme-primary">
      <div className="flex items-center justify-between border-b border-theme-outline px-3 py-3">
        <h2 className="body-sm-medium text-theme-primary tracking-wider uppercase">My Portfolio</h2>
        <button
          type="button"
          className="body-xxs-medium text-theme-muted hover:text-theme-primary"
          onClick={() => setShowAddGroup((value) => !value)}
        >
          + Add Group
        </button>
      </div>

      {showAddGroup ? (
        <div className="flex items-center gap-2 border-b border-theme-outline px-3 py-2">
          <input
            type="text"
            value={addGroupInput}
            onChange={(event) => setAddGroupInput(event.target.value)}
            onKeyDown={(event) => {
              if (event.key === "Enter") {
                handleAddGroup();
              }
            }}
            placeholder="Group name"
            className="flex-1 rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1.5 body-xxs-regular text-theme-primary"
          />
          <button
            type="button"
            onClick={handleAddGroup}
            className="rounded-sm bg-blue-500/20 px-2 py-1.5 body-xxs-medium text-blue-300"
          >
            Add
          </button>
        </div>
      ) : null}

      <div className="flex-1 overflow-auto">
        {groups.map((group) => {
          const isCollapsed = collapsedGroups.has(group.name);
          return (
            <div key={group.name} className="border-b border-theme-outline last:border-b-0">
              <button
                type="button"
                onClick={() => toggleGroup(group.name)}
                className="flex w-full items-center justify-between px-3 py-2 hover:bg-theme-secondary/40"
              >
                <span className="body-xxs-medium text-theme-muted uppercase tracking-wide">
                  {isCollapsed ? ">" : "v"} {group.name}
                </span>
                <span className="body-xxs-regular text-theme-muted">{group.tickers.length}</span>
              </button>

              {!isCollapsed ? (
                <div className="pb-1">
                  {group.tickers.map((symbol) => {
                    const quote = quotes.get(symbol);
                    return (
                      <div key={symbol} className="group relative">
                        <WatchlistTickerRow
                          symbol={symbol}
                          name={quote?.name ?? ""}
                          changePercent={quote?.change_percent ?? null}
                          changeDollar={quote?.change ?? null}
                          isSelected={activeSymbol === symbol}
                          onClick={() => onSelectSymbol(symbol)}
                        />
                        <button
                          type="button"
                          onClick={(event) => {
                            event.stopPropagation();
                            onRemoveTicker(group.name, symbol);
                          }}
                          className="absolute right-1 top-1 hidden rounded-sm px-1 py-0.5 body-xxs-regular text-red-400 hover:bg-red-500/10 group-hover:block"
                          aria-label={`Remove ${symbol}`}
                        >
                          x
                        </button>
                      </div>
                    );
                  })}

                  {addingTickerGroup === group.name ? (
                    <div className="flex items-center gap-2 px-3 py-2">
                      <input
                        type="text"
                        value={tickerInput}
                        onChange={(event) => setTickerInput(event.target.value.toUpperCase())}
                        onKeyDown={(event) => {
                          if (event.key === "Enter") {
                            handleAddTicker(group.name);
                          }
                        }}
                        placeholder="AAPL"
                        autoFocus
                        className="w-24 rounded-sm border border-theme-outline bg-theme-secondary px-2 py-1 body-xxs-regular text-theme-primary"
                      />
                      <button
                        type="button"
                        onClick={() => handleAddTicker(group.name)}
                        className="rounded-sm bg-blue-500/20 px-2 py-1 body-xxs-medium text-blue-300"
                      >
                        Add
                      </button>
                      <button
                        type="button"
                        onClick={() => {
                          setAddingTickerGroup(null);
                          setTickerInput("");
                        }}
                        className="body-xxs-regular text-theme-muted"
                      >
                        Cancel
                      </button>
                    </div>
                  ) : (
                    <button
                      type="button"
                      onClick={() => setAddingTickerGroup(group.name)}
                      className="w-full px-3 py-2 text-left body-xxs-medium text-theme-muted hover:text-theme-primary"
                    >
                      + Add Ticker
                    </button>
                  )}
                </div>
              ) : null}
            </div>
          );
        })}
      </div>
    </div>
  );
}
