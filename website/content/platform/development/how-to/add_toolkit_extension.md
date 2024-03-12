---
title: How To Add Toolkit Extensions
sidebar_position: 4
description: This guide outlines the process for adding a new toolkit extension and router path to the OpenBB Platform.
keywords:
- OpenBB Platform
- Open source
- contribution
- contributing
- community
- toolkit
- code
- provider
- endpoint
- router
- openbb-provider
- openbb-core
- how to
- new
- template
---

import HeadTitle from '@site/src/components/General/HeadTitle.tsx';

<HeadTitle title="How To Add Toolkit Extensions - How-To - Development | OpenBB Platform Docs" />

This page will summarize some of the differences between toolkit and provider extensions,
and then walk through adding a new toolkit extension and router path to the OpenBB Platform using a supplied template.

## What Is A Toolkit?

Toolkits are a generalized category of functionality for performing operations beyond the scope of any provider fetcher.
The possibilities are virtually unlimited, and each component (`equity`, `etf`, `index`, etc.) can be installed or removed independently.
A toolkit might even be extending another extension, which itself is an extension of an extension.

An easy example to understand is, `openbb-technical`.
It has its own router where all functions are configured as a `POST` request, with data being sent by the user as a serialized JSON in the body.
Calculations are performed using the supplied data and parameters, returning a new instance of the OBBject class.

The `pyproject.toml` defining the extension is nearly nearly identical to a Provider.
Instead of registering the plugin as a provider extension, it is an `openbb_core` extension.

> `openbb-devtools` is an extension with no router entry points or added functionality. Its only purpose is to install a collection of Python packages.

### Provider

```toml
[tool.poetry.plugins."openbb_provider_extension"]
```

### Core

```toml
[tool.poetry.plugins."openbb_core_extension"]
```

Below is the contents of the `pyproject.toml` file that defines the `openbb-technincal` extension.

```toml
[tool.poetry]
name = "openbb-technical"
version = "1.1.3"
description = "Technical Analysis extension for OpenBB"
authors = ["OpenBB Team <hello@openbb.co>"]
readme = "README.md"
packages = [{ include = "openbb_technical" }]

[tool.poetry.dependencies]
python = ">=3.8,<3.12"  # scipy forces python <4.0 explicitly
scipy = "^1.10.1"
statsmodels = "^0.14.0"
scikit-learn = "^1.3.1"
pandas-ta = "^0.3.14b"
openbb-core = "^1.1.2"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.plugins."openbb_core_extension"]
technical = "openbb_technical.technical_router:router"
```

On [this page](add_data_provider_extension), we created a data provider extension using a template ZIP file.
The structure is familiar, but let's take a look at some subtle differences.

For convenience, a template router extension ZIP file can be downloaded [here](https://github.com/OpenBB-finance/OpenBBTerminal/files/14542427/dashboards.zip) to follow along with.

## Folder Structure

A couple of notable differences between a provider and toolkit extension are:

- In the OpenBB GitHub repo, extensions are all located under:
    ```console
    ~/OpenBBTerminal/openbb_platform/extensions
    ```
- An additional folder housing integration tests, with the `tests` folder staying empty.
- There is a `router` file, and there can be sub-folders with additional routers.
- Utility functions don't need their own sub-folder.
- `__init__.py` files are all empty.

## How To Create A Router Extension

Let's create an extension which defines a new router entry point at the base of the `obb` namespace.
It's going to be called, `openbb-dashboards`, and will serve as an empty router for various dashboard packages to populate **future** endpoints with.
By itself, it might not have any functions. Some other extension will name it as a dependency, using it as an entry point.

We'll use the [ZIP file](https://github.com/OpenBB-finance/OpenBBTerminal/files/14542427/dashboards.zip) template as a starting point, renaming everything as the first step.

### Create Folder

The folder does not have to be kept with the OpenBB code, and could be its own GitHub repo.
For demonstration purposes, we'll unpack the ZIp file template with the rest of the OpenBB extensions:

```console
~/OpenBBTerminal/openbb_platform/extensions/dashboards
```

### Add Dependencies

This extension will be agnostic as to the type of components that might populate this space in the future - Plotly Dash, Streamlit, etc.
The only addition to the dependencies will be `openbb-charting`.
This will provide a Plotly charting library and custom backend with PyWry for window creation.

```toml
[tool.poetry]
name = "openbb-dashboards"
version = "1.0.0"
description = "Dashboards Extension for OpenBB"
authors = ["OpenBB Team <hello@openbb.co>"]
readme = "README.md"
packages = [{ include = "openbb_dashboards" }]

[tool.poetry.dependencies]
python = ">=3.8,<3.12"  # scipy forces python <4.0 explicitly
openbb-core = "^1.1.2"
openbb-charting = "^2.0.0"

[build-system]
requires = ["poetry-core"]
build-backend = "poetry.core.masonry.api"

[tool.poetry.plugins."openbb_core_extension"]
dashboards = "openbb_dashboards.dashboards_router:router"
```

## Build and Install Package

Open a Terminal and navigate into the folder where the extension is, then enter:

```console
poetry lock

pip install -e .
```

## Add Router Commands

To demonstrate this extension, we'll make a simple function for creating and returning a line chart. This adds one endpoint to the new namespace, `obb.dashboards.line_chart()`.

:::tip
After creating a new function, remember to rebuild the Python interface and static assets.
```python
import openbb
openbb.build()
exit()
```
:::

```python
"""Dashboards Router."""

# pylint: disable = unused-argument

from typing import List, Optional, Union

from openbb_charting import charting_router
from openbb_charting.core.openbb_figure import OpenBBFigure
from openbb_core.app.model.charts.chart import Chart
from openbb_core.app.model.obbject import OBBject
from openbb_core.app.router import Router
from openbb_core.app.utils import basemodel_to_df, df_to_basemodel
from openbb_core.provider.abstract.data import Data

router = Router(prefix="")


@router.command(
    methods=["POST"],
)
def line_chart(
    data: Union[Data, List[Data]],
    x: Optional[str] = None,
    y: Optional[Union[str, List[str]]] = None,
    layout_kwargs: Optional[dict] = None,
    scatter_kwargs: Optional[dict] = None,
) -> OBBject:
    """Create a line chart."""
    index = "date" if x is None else x
    df = basemodel_to_df(data, index=index)

    y = y.split(",") if isinstance(y, str) else y
    if y is None:
        y = df.columns.to_list()

    if scatter_kwargs is None:
        scatter_kwargs = {}

    fig = OpenBBFigure(create_backend=True)
    for col in y:
        fig = fig.add_scatter(
            x=df.index,
            y=df[col],
            name=col,
            hovertemplate=
            "<b>%{fullData.name}</b>: " +
            "%{y:.2f}" +
            "<extra></extra>",
            hoverlabel=dict(font_size=10),
            **scatter_kwargs,
        )

    if layout_kwargs is None:
        layout_kwargs = {}

    fig.update_layout(
        hovermode="x unified",
        **layout_kwargs,
    )

    results = OBBject(results=df_to_basemodel(df))

    results.chart = Chart(
        fig=fig,
        content=fig.show(external=True).to_plotly_json(),
        format=charting_router.CHART_FORMAT
    )

    return results
```

An example syntax for use is:

```python
data = obb.equity.price.historical("AAPL", provider="yfinance")
chart = obb.dashboards.line_chart(
    data.results, y=["high", "low"],
    scatter_kwargs = {"showlegend": False},
    layout_kwargs={"template":"plotly_white"}
)
chart.show()
```

This is demonstration is not meant to represent a finished product, only a path to explore while getting started.
We hope you enjoy the journey and look forward to seeing what you build!
