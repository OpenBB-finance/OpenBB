---
title: Building Extensions for OpenBB Platform
sidebar_position: 4
description: This guide provides a comprehensive walkthrough on how to create custom extensions for the OpenBB Platform. It covers the process from generating the extension structure to sharing it with the community.
keywords:
- OpenBB Platform
- Custom extension
- Python development
- Data integration
- Community contribution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Build OpenBB Extensions - Developer Guidelines - Development | OpenBB Platform Docs" />

In order to speed up the process of building an extension, we have provided a **Cookiecutter** template. It serves as a jumpstart for your extension development, so you can focus on the data and not on the boilerplate.

:::info
Take into consideration that building an extension requires a good understanding of the OpenBB Platform and that it is limited to a small set of use cases.
Before starting, please read the [Integrating Data Sources and Points](/platform/development/developer-guidelines/add_data_point) guide to make sure you really need a new extension.

Extension use cases might include:

- Adding a new data provider
- Adding a new toolkit
- Adding a new charting library
- Adding a new asset class
:::

Please refer to the [Cookiecutter template](https://github.com/OpenBB-finance/openbb-cookiecutter) and follow the instructions there.

This document will walk you through the steps of adding a new extension to the OpenBB Platform.

The high level steps are:

- Generate the extension structure
- Install your dependencies
- Install your new package
- Use your extension (either from Python or the API interface)
- QA your extension
- Share your extension with the community

## Best Practices

1. **Review Platform Dependencies**: Before adding any dependency, ensure it aligns with the Platform's existing dependencies.
2. **Use Loose Versioning**: If possible, specify a range to maintain compatibility. E.g., `>=1.4,<1.5`.
3. **Testing**: Test your extension with the Platform's core to avoid conflicts. Both unit and integration tests are recommended.
4. **Document Dependencies**: Use `pyproject.toml` and `poetry.lock` for clear, up-to-date records.


## Walkthrough

If you do not wish to use the cookiecutter template, this section will walk through the steps of creating a new provider extension.

### Generate the extension structure

We first create a new directory for our provider.  This should be located under the `openbb_platform/providers` directory.  If I am adding `cooldatasource`, I would create the following directory structure:

```md
cooldatasource/
├── openbb_cooldatasource/
│   ├── models/
│   │   └── cooldatamodel.py
│   ├── utils/
│   │   └── helper_functions.py
│   └── __init__.py
├── pyproject.toml
└── README.md
```

In this structure, the `cooldatamodel.py` and `helper_functions.py` are the folders handling the logic for obtaining data, as described in the next sections.
The `__init__.py` defines the provider, using the following code:

```python
from openbb_core.provider.abstract.provider import Provider
cooldatasource_provider = Provider(
    name="cooldatasource",
    website="",
    description="",
    credentials=["api_key"],
    fetcher_dict={
        "MyModel": MyFetcher,
    },
)
```
The pyproject.toml defines the package itself

```[tool.poetry]
name = "openbb-cooldatasource"
version = "latest version"
description = "Cool OpenBB Extension"
authors = ["You"]
readme = "README.md"
packages = [{ include = "openbb_cooldatasource" }]

[tool.poetry.dependencies]
python = "^3.9"
openbb-core = "latest openbb core version"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.plugins."openbb_provider_extension"]
cooldatasource = "openbb_cooldatasource:cooldatasource_provider"
```
Where the last line (poetry.plugins) maps to the provider defined in the `__init__.py` file.

### Install your dependencies and package

The next step is to install the dependencies.  We use poetry for dependency management, so from our new directory, we generate the lock file using:
```console
poetry lock
```
In order to use the extension we will install it using pip.  For development mode, we run the following from our directory
```console
pip install -e .
```
This will install the extension in editable mode, so any changes we make will be reflected in the installed package.

### Use your provider extension

Once this is installed, you can use it directly in the openbb package.  If you wish to add this to the repo, please follow the instructions in the contributing section, which enforces QA guidelines for adding tests and ensuring the package is implemented properly.
