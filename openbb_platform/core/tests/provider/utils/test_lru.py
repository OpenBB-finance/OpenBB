"""Tests for the LRU cache utilities."""

import time

from openbb_core.provider.utils.lru import _ttl_hash_gen, ttl_cache


class TestTtlHashGen:
    """Tests for _ttl_hash_gen."""

    def test_yields_same_value_within_ttl_window(self):
        """Test that the generator yields the same value within a TTL window."""
        gen = _ttl_hash_gen(seconds=10)
        first = next(gen)
        second = next(gen)
        assert first == second

    def test_yields_different_value_after_ttl_expires(self):
        """Test that the generator yields a different value after TTL expires."""
        gen = _ttl_hash_gen(seconds=1)
        first = next(gen)
        time.sleep(1.1)
        second = next(gen)
        assert second > first

    def test_increments_by_one_per_ttl_period(self):
        """Test that the hash increments by 1 for each TTL period elapsed."""
        gen = _ttl_hash_gen(seconds=1)
        first = next(gen)
        time.sleep(2.1)
        second = next(gen)
        assert second >= first + 2


class TestTtlCache:
    """Tests for ttl_cache decorator."""

    def test_caches_return_value(self):
        """Test that the decorated function's return value is cached."""
        call_count = 0

        @ttl_cache(ttl=60)
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return "result"

        result1 = expensive_function()
        result2 = expensive_function()

        assert result1 == "result"
        assert result2 == "result"
        assert call_count == 1

    def test_cache_expires_after_ttl(self):
        """Test that the cache expires after TTL seconds."""
        call_count = 0

        @ttl_cache(ttl=1)
        def expensive_function():
            nonlocal call_count
            call_count += 1
            return f"result_{call_count}"

        result1 = expensive_function()
        assert call_count == 1

        time.sleep(1.1)

        result2 = expensive_function()
        assert call_count == 2
        assert result1 == "result_1"
        assert result2 == "result_2"

    def test_caches_with_arguments(self):
        """Test that caching works correctly with function arguments."""
        call_count = 0

        @ttl_cache(ttl=60)
        def func_with_args(x, y):
            nonlocal call_count
            call_count += 1
            return x + y

        result1 = func_with_args(1, 2)
        result2 = func_with_args(1, 2)
        result3 = func_with_args(3, 4)

        assert result1 == 3
        assert result2 == 3
        assert result3 == 7
        assert call_count == 2  # Called once for (1,2) and once for (3,4)

    def test_caches_with_kwargs(self):
        """Test that caching works correctly with keyword arguments."""
        call_count = 0

        @ttl_cache(ttl=60)
        def func_with_kwargs(a, b=10):
            nonlocal call_count
            call_count += 1
            return a * b

        result1 = func_with_kwargs(5, b=2)
        result2 = func_with_kwargs(5, b=2)
        result3 = func_with_kwargs(5, b=3)

        assert result1 == 10
        assert result2 == 10
        assert result3 == 15
        assert call_count == 2

    def test_default_ttl_is_large(self):
        """Test that default TTL (when <= 0) is set to a large value."""
        call_count = 0

        @ttl_cache(ttl=0)
        def func():
            nonlocal call_count
            call_count += 1
            return "cached"

        func()
        func()
        func()

        assert call_count == 1

    def test_negative_ttl_uses_default(self):
        """Test that negative TTL uses the default large value."""
        call_count = 0

        @ttl_cache(ttl=-1)
        def func():
            nonlocal call_count
            call_count += 1
            return "cached"

        func()
        func()

        assert call_count == 1

    def test_maxsize_limits_cache(self):
        """Test that maxsize parameter limits the cache size."""
        call_count = 0

        @ttl_cache(maxsize=2, ttl=60)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x * 2

        # Fill cache
        func(1)  # call 1
        func(2)  # call 2

        # These should be cached
        func(1)
        func(2)
        assert call_count == 2

        # This evicts the oldest (1)
        func(3)  # call 3
        assert call_count == 3

        # 1 was evicted, so this is a new call
        func(1)  # call 4
        assert call_count == 4

    def test_typed_parameter(self):
        """Test that typed=True distinguishes between types."""
        call_count = 0

        @ttl_cache(maxsize=128, typed=True, ttl=60)
        def func(x):
            nonlocal call_count
            call_count += 1
            return x

        func(1)
        func(1.0)  # Different type, should be cached separately

        assert call_count == 2

    def test_preserves_function_metadata(self):
        """Test that the decorator preserves function name and docstring."""

        @ttl_cache(ttl=60)
        def my_function():
            """My docstring."""
            return "result"

        assert my_function.__name__ == "my_function"
        assert my_function.__doc__ == "My docstring."

    def test_works_with_none_return_value(self):
        """Test that None return values are cached correctly."""
        call_count = 0

        @ttl_cache(ttl=60)
        def func_returning_none():
            nonlocal call_count
            call_count += 1

        result1 = func_returning_none()
        result2 = func_returning_none()

        assert result1 is None
        assert result2 is None
        assert call_count == 1

    def test_works_with_mutable_return_value(self):
        """Test caching with mutable return values (returns same object)."""
        call_count = 0

        @ttl_cache(ttl=60)
        def func_returning_list():
            nonlocal call_count
            call_count += 1
            return [1, 2, 3]

        result1 = func_returning_list()
        result2 = func_returning_list()

        assert result1 == [1, 2, 3]
        assert result1 is result2  # Same cached object
        assert call_count == 1

    def test_concurrent_calls_within_ttl(self):
        """Test that concurrent-like calls within TTL share cache."""
        call_count = 0

        @ttl_cache(ttl=60)
        def func():
            nonlocal call_count
            call_count += 1
            return "result"

        # Simulate multiple rapid calls
        results = [func() for _ in range(100)]

        assert all(r == "result" for r in results)
        assert call_count == 1
