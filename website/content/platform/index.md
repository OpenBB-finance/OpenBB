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

![Platform Docs pic](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/74520441-5e95-4ba6-9d16-6a2d5c966cf9)

## What is the OpenBB Platform?

Starting with V4, we have completely restructured the previous version of the OpenBB SDK.
Instead of a single monolithic SDK, that comes with dependency nightmares and compatibility issues with things you may not need, we have morphed into the OpenBB Platform, which serves as a collection of building blocks to be used for your own need.

We have broken the Platform into two main components:

- OpenBB Core
- OpenBB Extensions
  - OpenBB Providers
  - OpenBB Toolkits

The OpenBB Core provides all of the groundwork for building custom applications.  It is a lightweight package providing connections with data providers in a standardized way, and the ability to build additional toolkits on top.  Additionally, the `openbb-core` library contains the infrastructure for Fast API deployments.

OpenBB Extensions are the pieces that can be added to the core for building on top of.  We have grouped them categorically as, Providers and Toolkits.
As the name suggests, Providers are the interface to obtaining any raw data from any data source. The data providers are accessed through asset class extensions, such as `openbb-equity`. OpenBB toolkits, such as `openbb-technical`, provide additional functionalities on top of the raw data access.

When you install the Platform (openbb), we provide a default set of extensions that give access to a wide range of functionalities and data.  Additional data and processing tools are available to be installed and used as desired. The reason we are doing this is to avoid an overcomplicated environment with many dependencies that can cause issues. The goal is that OpenBB can be used as a drop-in within any environment for building and extending applications.

---

Want to contribute? Check out our [Development section](/platform/development).
