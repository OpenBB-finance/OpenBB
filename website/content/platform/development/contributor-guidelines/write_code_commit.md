---
title: Write Code and Commit
sidebar_position: 5
description: This guide provides detailed instructions on how to write code and commit changes for the OpenBB Platform. It covers the process of creating a PR, branch naming conventions, and important guidelines to follow when committing changes.
keywords:
- OpenBB code writing
- Commit changes
- PR creation
- Branch naming conventions
- Commit guidelines
- GitHub
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Write Code and Commit - Contributor Guidelines - Development | OpenBB Platform Docs" />

## Folder Structure Overview

<details>
<summary>OpenBB Platform file tree</summary>

```bash
├── extensions
│   ├── charting
│   │   ├── __init__.py
│   │   ├── integration
│   │   ├── openbb_charting
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests
│   ├── crypto
│   │   ├── integration
│   │   ├── openbb_crypto
│   │   ├── poetry.lock
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests
│   ├── currency
│   │   ├── integration
│   │   ├── openbb_currency
│   │   ├── poetry.lock
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests

 ...

├── providers
│   ├── alpha_vantage
│   │   ├── __init__.py
│   │   ├── openbb_alpha_vantage
│   │   ├── poetry.lock
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests
│   ├── benzinga
│   │   ├── dist
│   │   ├── __init__.py
│   │   ├── openbb_benzinga
│   │   ├── poetry.lock
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests

 ...

├── openbb
│   ├── __init__.py
│   ├── package

├── platform
│   ├── core
│   │   ├── integration
│   │   ├── openbb_core
│   │   │   ├── api
│   │   │   ├── app
│   │   ├── poetry.lock
│   │   ├── pyproject.toml
│   │   ├── README.md
│   │   └── tests
│   │  
│   └── provider
│       ├── openbb_provider
│       ├── poetry.lock
│       ├── pyproject.toml
│       ├── README.md
│       └── tests

├── EXTENSIONS.md
├── integration
├── PROVIDERS.md
├── pyproject.toml
├── README.md
└── tests

```

</details>

The OpenBB Platform is organized into several key directories, each serving a specific purpose in the architecture of the system. Below is an overview of the main directories and their roles:

### `extensions`

This directory houses the various extensions available in the OpenBB Platform. Each extension has its own folder, containing the necessary files for its operation.

Each extension typically includes:

- `integration`: Integration tests.
- `openbb_[extension_name]`: Main codebase for the extension.
- `poetry.lock` and `pyproject.toml`: Dependency management files.
- `README.md`: Documentation specific to the extension.
- `tests`: Unit tests for the extension.

### `providers`

This directory contains the data providers integrated with the OpenBB Platform. Each provider has its own subdirectory.

Common files in each provider include:

- `openbb_[provider_name]`: Core code for the provider's integration.
- `poetry.lock` and `pyproject.toml`: Files for managing dependencies.
- `README.md`: Documentation for the provider.
- `tests`: Unit tests for the provider.

### `openbb`

This is the main directory for the OpenBB package, containing the core functionalities and modules of the OpenBB Platform.

- `package`: Contains the main package files and modules, i.e., the static auto generated files that serve the Python interface.

### `platform`

This directory hosts the core platform functionalities (`core`) which is the central part of the OpenBB Platform application.

### Root Directory Files

In the root directory, several important files are present:

- `EXTENSIONS.md`: List of available OpenBB extensions and its maintainers.
- `PROVIDERS.md`: List of available OpenBB providers and its maintainers
- `pyproject.toml`: The main file for managing the platform dependencies.
- `README.md`: The primary entry point for the OpenBB Platform documentation.
- `tests`: Contains tests that are relevant to the overall platform.

This structure allows for modular development and easy integration of new features, extensions, and providers, making the OpenBB Platform highly scalable and adaptable.

## How to create a PR?

To create a PR to the OpenBB Platform, you'll need to fork the repository and create a new branch.

1. Create your Feature Branch, e.g. `git checkout -b feature/AmazingFeature`
2. Check the files you have touched using `git status`
3. Stage the files you want to commit, e.g.
   `git add openbb_platform/platform/core/openbb_core/app/constants.py`.
   Note: **DON'T** add any files with personal information.
4. Write a concise commit message under 50 characters, e.g. `git commit -m "meaningful commit message"`. If your PR
   solves an issue raised by a user, you may specify such issue by adding #ISSUE_NUMBER to the commit message, so that
   these get linked. Note: If you installed pre-commit hooks and one of the formatters re-formats your code, you'll need
   to go back to step 3 to add these.

### Branch Naming Conventions

The accepted branch naming conventions are:

- `feature/feature-name`
- `hotfix/hotfix-name`

These branches can only have PRs pointing to the `develop` branch.
