"""Detect Flask applications without importing Flask."""

from __future__ import annotations

import importlib.util


def flask_available() -> bool:
    """Return ``True`` when Flask can be imported in this environment."""
    return importlib.util.find_spec("flask") is not None


def is_flask_app(obj: object) -> bool:
    """Return ``True`` when ``obj`` is a Flask application or a subclass of one."""
    for klass in type(obj).__mro__:
        if f"{klass.__module__}.{klass.__qualname__}" == "flask.app.Flask":
            return True
    return False
