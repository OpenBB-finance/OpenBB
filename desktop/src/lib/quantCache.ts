const TTL_CACHE = new Map<string, { expiresAt: number; value: unknown }>();

export async function getCachedOrFetch<T>(
  key: string,
  ttlMs: number,
  fetcher: () => Promise<T>,
): Promise<T> {
  const now = Date.now();
  const cached = TTL_CACHE.get(key);
  if (cached && cached.expiresAt > now) {
    return cached.value as T;
  }

  const value = await fetcher();
  TTL_CACHE.set(key, { expiresAt: now + ttlMs, value });
  return value;
}

export function clearCachePrefix(prefix: string): void {
  for (const key of TTL_CACHE.keys()) {
    if (key.startsWith(prefix)) {
      TTL_CACHE.delete(key);
    }
  }
}
