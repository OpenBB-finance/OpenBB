"""Codegen pipeline that turns a ``.spec`` document into a full extension package.

The pipeline is staged so each layer is independently testable:

* ``pydantic_gen`` — convert one OpenAPI JSON-schema fragment into a Pydantic
  class definition (``QueryParams`` or ``Data``). Cycles, optionals, arrays,
  and nested objects all resolve to source text.
* (later) ``fetcher_gen`` — emit the three-class ``QueryParams`` / ``Data`` /
  ``Fetcher`` module for one spec command.
* (later) ``router_gen`` — emit the router file binding model names to
  ``@router.command`` registrations.
* (later) ``provider_gen`` — emit ``providers/<name>/__init__.py`` with the
  ``Provider(...)`` instance + ``fetcher_dict``.
* (later) ``project_gen`` — emit ``pyproject.toml`` with deps and entry points.
"""
