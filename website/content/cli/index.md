---
title: Introduction
sidebar_position: 0
description: The OpenBB Platform CLI is a command line interface wrapping the OpenBB Platform. It offers a convenient way to interact with the Platform and its extensions, as well as automate data collection via OpenBB Routine Scripts. No experience with Python, or other programming languages, is required.
keywords:
- OpenBB
- CLI
- Platform
- data connectors
- data access
- data processing
- third-party data providers
- introduction
---

<!-- markdownlint-disable MD012 MD031 MD033 -->

import NewReferenceCard from "@site/src/components/General/NewReferenceCard";
import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="OpenBB Platform CLI Docs" />

## Overview

The OpenBB Platform CLI is a command line interface wrapping the OpenBB Platform. It offers a convenient way to interact with the Platform and its extensions, as well as automate data collection via OpenBB Routine Scripts.

The CLI is the next iteration of the [OpenBB Terminal](/terminal), and leverages the extendability of the OpenBB Platform architecture in an easy-to-consume and script format.

![CLI Home](https://github.com/OpenBB-finance/OpenBBTerminal/assets/85772166/d1617c3b-c83d-4491-a7bc-986321fd7230)

## Guides & Documentation

<ul className="grid grid-cols-1 gap-4 -ml-6">
<NewReferenceCard
    title="Installation"
    description="An installation guide for the OpenBB Platform CLI."
    url="cli/installation"
/>
<NewReferenceCard
    title="Quick Start"
    description="A quick start guide for the OpenBB Platform CLI."
    url="cli/quickstart"
/>
<NewReferenceCard
    title="Configuration & Settings"
    description="An explanation of the settings and environment variables that customize the look and feel of the OpenBB Platform CLI."
    url="cli/configuration"
/>
<NewReferenceCard
    title="Hub Synchronization"
    description="An overview of the `/account` menu and synchronizing settings with the OpenBB Hub."
    url="cli/hub"
/>
<NewReferenceCard
    title="Data Sources"
    description="How-to switch providers for a command, and define the default source for a function."
    url="cli/data-sources"
/>
<NewReferenceCard
    title="OpenBBUserData Folder"
    description="The OpenBBUserData folder is where exports, routines, and other related files are saved."
    url="cli/openbbuserdata"
/>
<NewReferenceCard
    title="Interactive Tables"
    description="Understand how to sort, filter, hide columns, display more rows or export data on our tables."
    url="cli/interactive-tables"
/>
<NewReferenceCard
    title="Interactive Charts"
    description="Explore how to overlay charts, change titles, draw lines, add text and much more on our charts."
    url="cli/interactive-charts"
/>
</ul>

---

Want to contribute? Check out our [Development section](/platform/development).
