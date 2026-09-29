# OpenBB Extensions Cookiecutter

A [Cookiecutter](https://cookiecutter.readthedocs.io/) template that generates a new OpenBB Platform extension as an installable Python project.

## Extension types

Choose one or more types, or `all`:

| Type | Generates |
|------|-----------|
| `router` | Commands under `obb.<router_name>` |
| `provider` | A data provider with an example model and an `EquityHistorical` standard-model implementation |
| `charting` | Chart views for the router's commands, used with `openbb-charting` |
| `obbject` | Accessors added to every command result |
| `on_command_output` | A plugin that runs after a command returns |

The generated project follows the same conventions as the extensions in this repository: hatchling packaging, entry points in `[project.entry-points]`, a `dev` dependency group, ruff and ty configuration in `pyproject.toml`, and tests for every generated module.

## Usage

Run it with [uv](https://docs.astral.sh/uv/) without installing:

```bash
uvx openbb-cookiecutter
```

Or install it and run the command:

```bash
pip install openbb-cookiecutter
openbb-cookiecutter
```

Enter a value at each prompt or press enter to accept the default. Pass the types directly to skip that prompt:

```bash
openbb-cookiecutter -e router provider
```

Generate without prompts, into another directory:

```bash
openbb-cookiecutter --no-input -o ./extensions -e all
```

Override any template value with `--extra-context KEY=VALUE`, for example `--extra-context provider_name=my_source`.

The provider and the OBBject extension each register a credentials namespace under their name, so they need different names.

## Working on the generated project

The generated `README.md` covers setup. In short, from the project directory:

```bash
uv sync
uv run openbb-build
uv run pytest
```

## Developing the template

From this directory:

```bash
uv sync
uv run pytest
```

The tests generate a project for each extension type and check its files, its entry points, and that it passes ruff and ty.

## Contacts

Questions about the template or OpenBB: `support@openbb.co`. Partnerships: `hello@openbb.co`. Social links: [openbb.co/links](https://openbb.co/links).
