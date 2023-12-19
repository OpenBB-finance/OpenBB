---
title: DevTools
sidebar_position: 2
description: This page provides information about the `openbb-devtools` package, which includes a range of dependencies essential for robust and efficient software development on the OpenBB Platform.
keywords:
- DevTools
- Python
- Development
- OpenBB Platform
- Dependencies
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="DevTools - Developer Guidelines - Development | OpenBB Platform Docs" />

Please refer to the following PyPI distributed package: https://pypi.org/project/openbb-devtools/

This Python package, `openbb-devtools`, is designed for OpenBB Platform Developers and contains a range of dependencies essential for robust and efficient software development.

These dependencies cater to various aspects like code formatting, security analysis, type checking, testing, and kernel management.

The inclusion of these packages ensures that the development process is streamlined, the code quality is maintained, and the software is secure and reliable.

Included dependencies:

- `ruff`: A fast Python linter focused on performance and simplicity.
- `pylint`: A tool that checks for errors in Python code, enforces a coding standard, and looks for code smells.
- `mypy`: A static type checker for Python, helping catch type errors during development.
- `pydocstyle`: A linter for Python docstrings to ensure they meet certain style requirements.
- `black`: An uncompromising Python code formatter, ensuring consistent code style.
- `bandit`: A tool designed to find common security issues in Python code.
- `pre-commit`: Manages and maintains pre-commit hooks that run checks before each commit, ensuring code quality.
- `nox`: A generic virtualenv management and test command line tool for running tests in isolated environments.
- `pytest`: A mature full-featured Python testing tool that helps in writing better programs.
- `pytest-cov`: A plugin for pytest that measures code coverage during testing.
- `ipykernel`: A package that provides the IPython kernel for Jupyter.
- `types-python-dateutil`: Type stubs for python-dateutil, aiding in static type checking.
- `types-toml`: Type stubs for TOML, useful for static type checking in TOML parsing.
- `poetry`: A tool for dependency management and packaging in Python.

Each dependency plays a critical role in ensuring the code is clean, efficient, and functional, ultimately leading to the development of high-quality software.

While developing code for the OpenBB Platform, one should always install the DevTools packages so that the above development tooling is available out-of-the-box.

:::info
When setting up the environment using the `openbb_platform/dev_install.py` script, the DevTools will also be installed.
:::
