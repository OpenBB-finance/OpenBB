---
title: Manage Extensions
sidebar_position: 4
description: Learn how to manage extensions in the OpenBB Platform.
keywords: [openbb, platform, introduction, manage extensions, contributing,
 documentation, pypi]
---

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
