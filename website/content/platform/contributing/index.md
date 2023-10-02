---
title: Introduction to the OpenBB Platform
sidebar_position: 1
description: Introduction to the OpenBB Platform
keywords: [openbb, platform, introduction, contributing, documentation]
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Introduction - Platform | OpenBB Docs" />

The OpenBB Platform is built by the Open-Source community and is characterized by its core and extensions. The core handles data integration and standardization, while the extensions enable customization and advanced functionalities. The OpenBB Platform is designed to be used both from a Python interface and a REST API.

The REST API is built on top of FastAPI and can be started by running the following command from the root:

```bash
uvicorn openbb_platform.platform.core.openbb_core.api.rest_api:app --host 0.0.0.0 --port 8000 --reload
```

The Python interfaces we provide to users is the `openbb` python package.

The code you will find in this package is generated from a script and it is just a wrapper around the `openbb-core` and any installed extensions.

When the user runs `import openbb`, `from openbb import obb` or other variants, the script that generates the package code is triggered. It detects if there are new openbb extensions installed in the environment and rebuilds the package code accordingly. If new extensions are not found, it just uses the current package version.

When you are developing chances are you want to manually trigger the package rebuild.

You can do that with:

```python
python -c "import openbb; openbb.build()"
```

The Python interface can be imported with:

```python
from openbb import obb
```

This section will take you through two types of contributions:

1. Building a custom extension
2. Contributing directly to the OpenBB Platform
