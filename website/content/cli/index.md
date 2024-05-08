---
id: index
title: OpenBB CLI
sidebar_position: 0
description: The OpenBB CLI is a command line interface wrapping the OpenBB Platform. It offers a convenient way to interact with the Platform and its extensions, as well as automate data collection via OpenBB Routine Scripts. No experience with Python, or other programming languages, is required.
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

<HeadTitle title="OpenBB CLI Docs" />

## Overview

The OpenBB CLI is a command line interface wrapping the OpenBB Platform. It offers a convenient way to interact with the Platform and its extensions, as well as automate data collection via OpenBB Routine Scripts.

The CLI is the next iteration of the [OpenBB Terminal](/terminal), and leverages the extendability of the OpenBB Platform architecture in an easy-to-consume and script format.

![CLI Home](cli_home.png)

## Guides & Documentation

<ul className="grid grid-cols-1 gap-4 -ml-6">
<NewReferenceCard
    title="Installation"
    description="An installation guide for the OpenBB CLI."
    url="cli/installation"
/>
<NewReferenceCard
    title="Quick Start"
    description="A quick start guide for the OpenBB CLI."
    url="cli/quickstart"
/>
<NewReferenceCard
    title="Structure and Navigation"
    description="Understand the terminal structure and how to navigate in it efficiently"
    url="overview/structure-and-navigation"
/>
<NewReferenceCard
    title="Commands and arguments"
    description="Understand what argument can be added to each command and leverage the auto-complete functionality"
    url="overview/commands-and-arguments"
/>
<NewReferenceCard
    title="Customization"
    description="Customize the OpenBB Terminal settings and feature flags"
    url="overview/customizing-the-terminal"
/>
</ul>

---

Want to contribute? Check out our [Development section](/platform/development).
