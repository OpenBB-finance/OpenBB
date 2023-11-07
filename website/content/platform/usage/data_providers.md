---
title: Data Providers
sidebar_position: 3
description: Learn about the OpenBB Platform and its extension framework that allows
  seamless integration of modules like 'openbb-yfinance'. Discover how installations
  and removals automatically update the router when the Python interpreter is refreshed.
keywords:
- OpenBB Platform
- extension framework
- yFinance
- install openbb-yfinance
- Python interpreter
- PyPI
- openbb-qa
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Data Providers - Usage | OpenBB Platform Docs" />

When the core OpenBB Platform package is installed, familiar components might be missing.  The extension framework allows individual pieces to be installed and removed seamlessly within the environment.

For example, yFinance.

```console
pip install openbb-yfinance
```

Additions and removals update the router automatically to reflect the changes when the Python interpreter is refreshed.

Search [PyPI](https://pypi.org/search/?q=openbb-) to find more, like `openbb-qa`.
