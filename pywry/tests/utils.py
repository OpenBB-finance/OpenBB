import time
from functools import wraps
from typing import Any, Callable, TypeVar

from pywry import runtime

F = TypeVar("F", bound=Callable[..., Any])


def retry_on_subprocess_failure(max_attempts: int = 3, delay: float = 1.0) -> Callable[[F], F]:
    """Retry decorator for tests that may fail due to transient subprocess issues.

    On Windows, WebView2 sometimes fails to start due to resource contention
    ("Failed to unregister class Chrome_WidgetWin_0"). This decorator retries
    the test after a delay to allow resources to be released.
    """

    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            last_error: Exception | None = None
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except TimeoutError as e:
                    last_error = e
                    if attempt < max_attempts - 1:
                        # Clean up and wait before retry
                        runtime.stop()
                        time.sleep(delay)
            raise last_error  # type: ignore[misc]

        return wrapper  # type: ignore[return-value]

    return decorator
