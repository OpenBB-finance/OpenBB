---
title: Manage Extensions
sidebar_position: 4
description: This page provides detailed guidance on how to install locally developed
  extensions and external extensions hosted on PyPI, including the use of pip install
  commands, how to add an extension as a dependency, and instructions for using the
  LOCAL_DEPS variable in the dev_install.py file and the pyproject.toml file.
keywords:
- pip install extension
- pyproject.toml
- LOCAL_DEPS
- python dev_install.py
- poetry.dependencies
- openbb-extension
- openbb-qa
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Manage Extensions - Platform Development - Contributing | OpenBB Platform Docs" />

To install extensions hosted on PyPI, use the `pip install <extension>` command.

To install an extension that is developed locally, ensure that it contains a `pyproject.toml` file and then use the `pip install <extension>` command.

> To install the extension in editable mode using pip, add the `-e` argument.

Alternatively, for local extensions, you can add this line in the `LOCAL_DEPS` variable in `dev_install.py` file:

```toml
# If this is a community dependency, add this under "Community dependencies",
# with additional argument optional = true
openbb-extension = { path = "<relative-path-to-the-extension>", develop = true }
```

Now you can use the `python dev_install.py [-e]` command to install the local extension.

## Add an extension as a dependency

To add the `openbb-qa` extension as a dependency, you'll need to add it to the `pyproject.toml` file:

```toml
[tool.poetry.dependencies]
openbb-qa = "^0.0.0a2"
```

Then you can follow the same process as above to install the extension.
