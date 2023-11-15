---
title: Build OpenBB Extensions
sidebar_position: 2
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

<HeadTitle title="Build OpenBB Extensions - Developer Guidelines - Contributing | OpenBB Platform Docs" />

We have a **Cookiecutter** template that will help you get started. It serves as a jumpstart for your extension development, so you can focus on the data and not on the boilerplate.

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
