import type { SymbolLabSearch } from "../types/quant";

function compactSearch(search: SymbolLabSearch): SymbolLabSearch {
  return Object.fromEntries(
    Object.entries(search).filter(([, value]) => typeof value === "string" && value.trim().length > 0),
  ) as SymbolLabSearch;
}

export function toSymbolLabSearch(search: SymbolLabSearch): SymbolLabSearch {
  return compactSearch(search);
}

export function buildSymbolLabHref(search: SymbolLabSearch): string {
  const params = new URLSearchParams();
  Object.entries(toSymbolLabSearch(search)).forEach(([key, value]) => {
    if (value) {
      params.set(key, value);
    }
  });
  const query = params.toString();
  return `/finance${query ? `?${query}` : ""}`;
}
