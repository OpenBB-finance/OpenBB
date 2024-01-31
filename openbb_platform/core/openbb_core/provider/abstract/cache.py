import asyncio
import time
import hashlib
import json
from abc import ABC, abstractmethod
from datetime import date, datetime

try:
    import redis

    REDIS_AVAILABLE = True
except ImportError:
    REDIS_AVAILABLE = False


def jsonify_date(obj):
    """JSON serializer for objects not serializable by default json code"""

    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError(f"Type {type(obj)} not serializable")


def generate_cache_key(*args, **kwargs):
    """Generate a unique key for a request."""
    key = json.dumps((args, kwargs), sort_keys=True, default=jsonify_date)
    return hashlib.sha256(key.encode("utf-8")).hexdigest()


class OpenBBAsyncCache(ABC):
    @abstractmethod
    async def get(self, key):
        pass

    @abstractmethod
    async def set(self, key, value):
        pass

    @abstractmethod
    async def clear(self):
        pass


class AsyncLRUCache(OpenBBAsyncCache):
    """Simple class to implement an LRU cache with our async fetcher.fetch_data"""

    def __init__(self, maxsize=100, expiration=600):
        self.cache = {}
        self.maxsize = maxsize
        self.history = []
        self.expiration = expiration  # Seconds
        self.lock = asyncio.Lock()

    async def get(self, key):
        async with self.lock:
            if key in self.cache:
                item, timestamp = self.cache[key]
                if time.time() - timestamp < self.expiration:
                    self.history.remove(key)
                    self.history.append(key)
                    return item
                else:
                    del self.cache[key]
                self.history.remove(key)
        return None

    async def set(self, key, value):
        async with self.lock:
            if key not in self.cache and len(self.cache) >= self.maxsize:
                oldest_key = self.history.pop(0)
                del self.cache[oldest_key]
            self.cache[key] = (value, time.time())
            self.history.append(key)

    async def clear(self):
        async with self.lock:
            self.cache = {}
            self.history = []

    async def cleanup(self):
        """Remove expired entries from the cache."""
        async with self.lock:
            current_time = time.time()
            keys_to_delete = [
                key
                for key, (value, timestamp) in self.cache.items()
                if current_time - timestamp >= self.expiration
            ]
            for key in keys_to_delete:
                del self.cache[key]
                self.history.remove(key)


class AsyncRedisCache(OpenBBAsyncCache):
    def __init__(self, host="localhost", port=6379, db=0, expiration=600):
        if not REDIS_AVAILABLE:
            raise RuntimeError(
                "Redis library is not installed. Please install it to use AsyncRedisCache."
            )
        self.client = redis.Redis(host=host, port=port, db=db)
        try:
            self.client.ping()
        except redis.exceptions.ConnectionError:
            raise RuntimeError(
                "Could not connect to Redis. Please make sure it is running."
            )
        self.expiration = expiration

    async def get(self, key):
        value = self.client.get(key)
        return json.loads(value) if value else None

    async def set(self, key, value):
        self.client.setex(key, self.expiration, json.dumps(value))

    async def clear(self):
        self.client.flushdb()
