---
title: Toolkit VS Provider
sidebar_position: 11
description: This section provides an explanation of the OpenBB Platform toolkits, which are a generalized category of functionality for performing operations beyond the scope of any provider fetcher.
keywords:
- OpenBB Platform
- toolkit
- provider
- extension
---

This page will summarize some of the differences between toolkit and provider extensions, and then walk through adding a new toolkit extension and router path to the OpenBB Platform using a supplied template.

## What Is A Toolkit?

Toolkits are a generalized category of functionality for performing operations beyond the scope of any provider fetcher.
The possibilities are virtually unlimited, and each component (`equity`, `etf`, `index`, etc.) can be installed or removed independently.
A toolkit might even be extending another extension, which itself is an extension of an extension.

An easy example to understand is, `openbb-technical`.
It has its own router where all functions are configured as a `POST` request, with data being sent by the user as a serialized JSON in the body.
Calculations are performed using the supplied data and parameters, returning a new instance of the OBBject class.

The `pyproject.toml` defining the extension is nearly nearly identical to a Provider.
Instead of registering the plugin as a provider extension, it is an `openbb_core` extension.

> `openbb-devtools` is an extension with no router entry points or added functionality. Its only purpose is to install a collection of Python packages.

### Provider

```toml
[tool.poetry.plugins."openbb_provider_extension"]
```

### Core

```toml
[tool.poetry.plugins."openbb_core_extension"]
```

Below is the contents of the `pyproject.toml` file that defines the `openbb-technincal` extension.

```toml
[tool.poetry]
name = "openbb-technical"
version = "1.1.3"
description = "Technical Analysis extension for OpenBB"
authors = ["OpenBB Team <hello@openbb.co>"]
readme = "README.md"
packages = [{ include = "openbb_technical" }]

[tool.poetry.dependencies]
python = ">=3.8,<3.12"  # scipy forces python <4.0 explicitly
scipy = "^1.10.1"
statsmodels = "^0.14.0"
scikit-learn = "^1.3.1"
pandas-ta = "^0.3.14b"
openbb-core = "^1.1.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.plugins."openbb_core_extension"]
technical = "openbb_technical.technical_router:router"
```

On [this page](add_data_provider_extension), we created a data provider extension using a template ZIP file.
The structure is familiar, but let's take a look at some subtle differences.

For convenience, a template router extension ZIP file can be downloaded [here](https://github.com/OpenBB-finance/OpenBBTerminal/files/14542427/dashboards.zip) to follow along with.

## Folder Structure

A couple of notable differences between a provider and toolkit extension are:

- In the OpenBB GitHub repo, extensions are all located under:

    ```console
    ~/OpenBBTerminal/openbb_platform/extensions
    ```

- An additional folder housing integration tests, with the `tests` folder staying empty.
- There is a `router` file, and there can be sub-folders with additional routers.
- Utility functions don't need their own sub-folder.
- `__init__.py` files are all empty.
