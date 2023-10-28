---
title: Charting Extension
sidebar_position: 4
description: Learn how to install and use the powerful OpenBB Charting Extension for
  the OpenBB Platform. It utilizes PyWry and Plotly for the display of interactive
  charts and tables - an essential tool for developers.
keywords:
- OpenBB Charting Extension
- OpenBB Platform
- REST API
- Python Client
- PyWry
- Plotly
- interactive charts
- router pipeline
- python interface
- Interactive tables
- Installation
- OpenBBFigure
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="Charting Extension - Usage | OpenBB Platform Docs" />


The OpenBB Charting Extension supplies charting infrastructure and services to the OpenBB Platform.  Figure objects are served via REST API or Python Client.  It utilizes PyWry for handling the display of interactive charts and tables in a separate window, with a Plotly library.  The extension framework allows developers to easily insert other Python charting libraries into the router pipeline.

## Installation

To install the extension, run the following command in this folder:

```bash
pip install openbb-charting
```

After installation, the Python interface will automatically rebuild on initialization.  This process can also be triggered manually with:

```python
import openbb
openbb.build()
```

The Python interpreter may require a restart.

### PyWry dependency in Linux

When using Linux distributions, the PyWry dependency requires certain dependencies to be installed first.

- Debian-based / Ubuntu / Mint:
`sudo apt install libwebkit2gtk-4.0-dev`

- Arch Linux / Manjaro:
`sudo pacman -S webkit2gtk`

- Fedora:
`sudo dnf install gtk3-devel webkit2gtk3-devel`

## Usage

The OpenBB Charting Extension can be used in different ways:

- A base class in the Python interface.
- An easy way to get started working with Plotly charts.
- The basic infrastructure for generating REST-compliant charts.
- Parameterized in existing router endpoints.
- Interactive tables.

### Python Interface

Import the `OpenBBFigure` class with:

```python
from openbb_charting.core.openbb_figure import OpenBBFigure
```
