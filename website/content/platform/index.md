---
title: Introduction
sidebar_position: 0
description: Introduction to OpenBB Platform; a convenient and powerful tool that
  provides pre-built data connectors and libraries to design and build financial reports
  and applications. Learn more about contributing to the platform.
keywords:
- OpenBB Platform
- investment research infrastructure
- data connectors
- financial reports
- OpenBB team
- third-party data providers
- CONTRIBUTING GUIDELINES
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

The OpenBB Platform has been created and is currently maintained by the OpenBB team together with the contributions from hundreds of community members. This gives us an unrivaled speed of development and the ability to maintain stable integrations with numerous third-party data providers.

Developing and maintaining a full-blown investment research infrastructure from the ground up takes a lot of time and effort. However, it does not have to be this way. By taking advantage of OpenBB Platform with its out-of-the-box data connectors and library of extensions, you can focus on designing and building your financial reports and applications.

<img width="769" alt="sdk" src="https://github.com/OpenBB-finance/OpenBBTerminal/assets/25267873/f8ddb59a-b3b5-436c-80cb-2b97e246a8d9" />


## What is the OpenBB Platform?
Starting with V4, we have completely restructured the previous version of the OpenBB SDK.
Instead of a single monolithic SDK, that comes with dependency nightmares and compatibility issues with things you may not need, we have morphed into the OpenBB Platform, which serves as a collection of building blocks to be used for your own need.

We have broken the Platform into 2 main components:
- OpenBB Core
- OpenBB Extensions
   - OpenBB Providers
   - OpenBB Toolkits

The OpenBB core provides all of the groundwork for building custom applications.  It is a lightweight package that provides the ability to connect with data providers in a standardized way, or to build additional toolkits on top.  Additionally, this provides the ability to launch with not just a python library, but with a web api.

OpenBB extensions are the pieces that can be added to the core for building on top of.  We have distinguished into Providers and Toolkits here.
As the name suggests, Providers are the interface to obtaining any raw data from any data source. The data providers are accessed through asset class extensions, such as `openbb-equity`.
The OpenBB toolkits, such as `openbb-technical`, provide additional functionalities on top of the raw data access.

When you install the platform (openbb), we provide a default set of extensions that give access to a wide range of functionalities and data.  Additional data, functionalities and extensions are available to be used as desired.
The reason we are doing this is to avoid an overcomplicated environment with many dependencies that can cause issues.
The goal is that OpenBB can be used as a drop in to any environment for access and building of applications on top of.


---

Want to contribute? Check out our [CONTRIBUTING GUIDELINES](https://github.com/OpenBB-finance/OpenBBTerminal/blob/develop/CONTRIBUTING.md).
