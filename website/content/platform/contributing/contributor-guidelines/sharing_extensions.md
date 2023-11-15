---
title: Sharing Your Extension
sidebar_position: 4
description: Learn about the OpenBB Platform, an open-source solution built by the
  community. Understand its use via Python interface and REST API, and acquaint yourself
  with how to build a custom extension or contribute directly to the platform
keywords:
- OpenBB Platform
- Open source
- Python interface
- REST API
- Data integration
- Data standardization
- OpenBB extensions
- openbb-core
- Python package
- High-Level Architecture
- Custom extension
- Contribution
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Sharing Your Extension - Contributor Guidelines - Contributing | OpenBB Platform Docs" />

We encourage you to share your extension with the community. You can do that by publishing it to PyPI.

## Publish your extension to PyPI

To publish your extension to PyPI, you'll need to have a PyPI account and a PyPI API token.

### Setup

Create an account and get an API token from <https://pypi.org/manage/account/token/>
Store the token with

```bash
poetry config pypi-token.pypi pypi-YYYYYYYY
```

### Release

`cd` into the directory where your extension `pyproject.toml` lives and make sure that the `pyproject.toml` specifies the version tag you want to release and run.

```bash
poetry build
```

This will create a `/dist` folder in the directory, which will contain the `.whl` and `tar.gz` files matching the version to release.

If you want to test your package locally you can do it with

```bash
pip install dist/openbb_[FILE_NAME].whl
```

### Publish

To publish your package to PyPI run:

```bash
poetry publish
```

Now, you can pip install your package from PyPI with:

```bash
pip install openbb-some_ext
```
