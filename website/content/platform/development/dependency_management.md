---
title: Dependency Management
sidebar_position: 3
description: Dealing with dependencies when developing with the OpenBB Platform. Learn
  how to add new dependencies to the OpenBB Platform and how to add new dependencies
  to your custom extension.
keywords:
- OpenBB Platform
- Open source
- Python interface
- Dependency Management
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Dependency Management - Development | OpenBB Platform Docs" />

## High-Level Overview

- **Core**: Serves as the main infrastructural package.
- **Extensions**: Utility packages that leverage Core's infrastructure. Each extension is its own package.
- **Providers**: Utility packages extending functionality to different providers, where each provider is its own package.

## Core Dependency Management

### Installation

- **pip**: `pip install -e OpenBBTerminal/openbb_platform/platform/core`
- **poetry**: `poetry install OpenBBTerminal/openbb_platform/platform/core`

### Using Poetry

Ensure you're in a fresh conda environment before adjusting dependencies.

- **Add a Dependency**: `poetry add <my-dependency>`
- **Update Dependencies**:
  - All: `poetry update`
  - Specific: `poetry update <my-dependency>`
- **Remove a Dependency**: `poetry remove <my-dependency>`

## Core and Extensions

### Dev Installation

For development setup, use the provided script to install all extensions and their dependencies:

- `python dev_install.py [-e|--extras]`

> **Note**: If developing an extension, avoid installing all extensions to prevent unnecessary overhead.

### Dependency Management with Poetry

- **Add Platform Extension**: `poetry add openbb-extension-name [--dev]`
- **Resolve Conflicts**: Adjust versions in `pyproject.toml` if notified by Poetry.
- **Lock Dependencies**: `poetry lock`
- **Update Platform**: `poetry update openbb-platform`
- **Documentation**: Maintain `pyproject.toml` and `poetry.lock` for a clear record of dependencies.
