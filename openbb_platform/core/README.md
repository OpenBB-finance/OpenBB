# Open Data Platform by OpenBB

Open Data Platform by OpenBB (ODP) is the open-source toolset that helps data engineers integrate proprietary, licensed, and public data sources into downstream applications like AI copilots and research dashboards.

ODP operates as the "connect once, consume everywhere" infrastructure layer that consolidates and exposes data to multiple surfaces at once: Python environments for quants, OpenBB Workspace and Excel for analysts, MCP servers for AI agents, and REST APIs for other applications.

## Overview

The Core extension is used as the basis for building and integrating Open Data Platform Python packages.
It provides the necessary classes and structures for standardizing and handling data.
It is also responsible for generating a REST API and Python package static assets,
which operate independently and interface with various consumption vehicles.

Typically, this library will be used as a project dependency, and extended.

Go to the [documentation](https://docs.openbb.co/python/developer) for information on getting started.

### Prerequisites

- Python >=3.10,<3.14
- Familiarity with FastAPI and Pydantic.

### Installation

Installing through pip:

```sh
pip install openbb-core
```

> Note that, the openbb-core is an infrastructural component of the OpenBB Platform. It is not intended to be used as a standalone package.

### Build

Build the Python application, with installed extensions, by running:

```sh
openbb-build
```

## Key Features

- **Standardized Data Model** (`Data` Class): A flexible and dynamic Pydantic model capable of handling various data structures.
- **Standardized Query Params** (`QueryParams` Class): A Pydantic model for handling querying to different providers.
- **Dynamic Field Support**: Enables handling of undefined fields, providing versatility in data processing.
- **Robust Data Validation**: Utilizes Pydantic's validation features to ensure data integrity.
- **API Routing Mechanism** (`Router` Class): Simplifies the process of defining API routes and endpoints - out of the box Python and Web endpoints.

## Bugs

Report bugs on [Github](https://github.com/OpenBB-finance/OpenBB/issues/new/choose) by opening a new issue, or commenting on an already open one, with all the details.

## License

This project is licensed under the AGPL-3.0 License - see the [LICENSE.md](https://github.com/OpenBB-finance/OpenBB/blob/main/LICENSE) file for details.
