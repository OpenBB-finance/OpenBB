---
title: Considerations
sidebar_position: 1
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

<HeadTitle title="Considerations - Development | OpenBB Platform Docs" />

These sections provide guidelines for developing with, and contributing to, the OpenBB Platform.
There are comprehensive guides on how to build extensions, add new data points, contribute to the code base, and more.

We generalize between two distinct types of users:

1. **Developers**: Those who are building on top of, and extending, the OpenBB Platform for their own purposes and have no intention of contributing the code directly to the GitHub repository. This includes those independently publishing extensions to PyPI or other package managers.
2. **Contributors**: Those who contribute to the existing codebase, by opening a Pull Request, thus giving back to the community.  This can include bug fixes, enhancements, documentation, and more.

**Why Is This Distinction Important?**

The OpenBB Platform has been designed as a foundation for further development of investment research applications. We anticipate a wide range of creative use cases.

Some of them may be highly specific, or detail-oriented, solving particular problems that may not necessarily fit within the OpenBB Platform Github repository. This is entirely acceptable, even encouraged. Regardless of intention, OpenBB is a proponent of building in public and sharing. We love seeing what people are building, so don't be shy about it!


## Before Beginning

- Familiarize yourself with the codebase, architecture, and components.
- Set clear goals with defined outcomes - i.e, I want to create a technical indicator that uses multiple data points and sources where the output is a chart.

Below is a high-level overview of the OpenBB Platform architecture.

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/6125cbf2-ff5b-4cd8-b5b8-452cd8d84418"/>
  <img alt="OpenBB Platform High-Level Architecture" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/48914296/6125cbf2-ff5b-4cd8-b5b8-452cd8d84418"/>
</picture>

Cloning the [GitHub repo](https://github.com/OpenBB-finance/OpenBBTerminal) will be the best way to inspect and play around with the code.

## What Is An Extension?

An extension is an installable component adding functionality to the OpenBB Platform. It can be a new data source, a new command, a new visualization, or anything imaginable. They can generally be classified as one of:

- Data Provider
  - The individual sources of data.
- Toolkit
  - Data processing, router modules, visualizations.
- OBBject
  - Extending the OBBject class itself.

The extensions within the OpenBB GitHub repository are maintained by the OpenBB Team. The pages under [how-to](how-to/add_obbject_extension) detail getting started building with the OpenBB Platform.

We welcome contributions, and anyone is free to publish their own OpenBB extension to PyPI, or elsewhere. If you do, please name the package beginning with, "openbb-". We love seeing what you build!
