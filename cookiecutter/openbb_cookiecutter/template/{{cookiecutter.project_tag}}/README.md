{%- set types = cookiecutter.extension_types.split(',') | map('trim') | list -%}
{%- set is_all = 'all' in types -%}
{%- set has_router = is_all or 'router' in types -%}
{%- set has_provider = is_all or 'provider' in types -%}
{%- set has_charting = is_all or 'charting' in types -%}
{%- set has_obbject = is_all or 'obbject' in types -%}
{%- set has_on_command_output = is_all or 'on_command_output' in types -%}
# {{ cookiecutter.project_name }}

An extension for the OpenBB Platform, generated with `openbb-cookiecutter`.

## Contents
{% if has_router %}
- `{{ cookiecutter.package_name }}/routers/{{ cookiecutter.router_name }}.py`: commands under `obb.{{ cookiecutter.router_name }}`.
{%- endif %}
{%- if has_provider %}
- `{{ cookiecutter.package_name }}/providers/{{ cookiecutter.provider_name }}/`: the `{{ cookiecutter.provider_name }}` provider, with an `Example` model and an `EquityHistorical` standard-model implementation.
{%- endif %}
{%- if has_charting %}
- `{{ cookiecutter.package_name }}/routers/{{ cookiecutter.router_name }}_views.py`: charts for `{{ cookiecutter.router_name }}` commands, used when `openbb-charting` is installed.
{%- endif %}
{%- if has_obbject %}
- `{{ cookiecutter.package_name }}/obbject/{{ cookiecutter.obbject_name }}/__init__.py`: the `to_string` and `{{ cookiecutter.obbject_name }}` accessors on every command result.
{%- endif %}
{%- if has_on_command_output %}
- `{{ cookiecutter.package_name }}/obbject/{{ cookiecutter.obbject_name }}/on_command_output.py`: a plugin that runs after `/{{ cookiecutter.router_name }}/candles`.
{%- endif %}
{%- if has_charting and not has_router %}

The views are named after `{{ cookiecutter.router_name }}` routes, so pair them with a router extension that uses that name.
{%- endif %}

## Development

Create an environment with [uv](https://docs.astral.sh/uv/) and install the package in editable mode with its development dependencies:

```bash
uv sync
```

Build the `openbb` package so the new commands appear under `obb`:

```bash
uv run openbb-build
```
{%- if has_on_command_output %}

On-command-output plugins run on every matching result, so OpenBB loads them only when explicitly allowed:

```bash
export OPENBB_ALLOW_ON_COMMAND_OUTPUT=true
```
{%- endif %}

Lint, type check, and test:

```bash
uv run ruff format --check .
uv run ruff check .
uv run ty check {{ cookiecutter.package_name }}
uv run pytest
```

Serve the commands over the REST API with `uv run openbb-api`.
