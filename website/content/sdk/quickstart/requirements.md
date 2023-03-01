---
title: Requirements
sidebar_position: 1
description: General system requirements for installing the OpenBB SDK.
keywords: [installation, installer, install, guide, mac, windows, linux, python, github, macos, how to, explanation, requirements, openbb, sdk, system]
---
import Tabs from '@theme/Tabs';
import TabItem from '@theme/TabItem';

Installation of the OpenBB Terminal requires downloading around 4GB of data. Querying data (by running commands) does not require a lot of bandwidth but you will certainly have a more pleasant experience if you are on a fast internet connection. 4G networks provide a good enough experience so if you're traveling your personal hot-spot will do. While it's technically possible to use a subset of the functionality in off-line mode, you will not be able to use any data that is queried from the APIs of data providers and services.

## Minimum System Requirements

- A modern CPU compatible with the Intel Math Kernel Library, supporting SSE3 & SSE4.2 instructions.
- Windows 10 or higher.
- MacOS Monterey or higher, with Rosetta installed.
- Check the Ubuntu hardware certified hardware page [here](https://ubuntu.com/certified?q=&limit=20&category=Desktop&category=Laptop).
- 4GB RAM or more
- 5GB free storage
- Internet connection

## Virtual Environments

- [Miniconda3](https://docs.conda.io/en/latest/miniconda.html)
- [Installing Python Packages](https://packaging.python.org/en/latest/tutorials/installing-packages/)

Virtual Python environments are containers for Python applications, and allows the operating system to remain unchanged. The OpenBB SDK is built on top of 300+ open-source libraries. The dependency tree is complex and the components are carefully selected to work with each other. This makes it critical to install the OpenBB SDK in an isolated, dedicated, virtual environment. We recommend a Conda virtual environment because this is currently the only package manager compatible with every function.

It is not recommended to install in a Global environment, such as Homebrew or `usr/local/bin/python3`. Create and activate a new environment before installing the OpenBB SDK.

## GitHub

[GitHub](https://github.com/OpenBB-finance/OpenBBTerminal) is where the OpenBB source code is maintained. Cloning the [repository](https://github.com/OpenBB-finance/OpenBBTerminal.git) is recommended for those wishing to develop functions, inspect the source code, or be on the bleeding-edge of development. Syncing the local folder - `git pull` - to the main branch of the repository will keep the installation up-to-date, and `git checkout` provides a way to test development or contributor branches. GitHub can also be used as a personal storage vault and take advantage of automated actions. It's a great place to build, store, and maintain small databases for free.

Users encountering bugs are encouraged to report them [here](https://github.com/OpenBB-finance/OpenBBTerminal/issues/new/choose) by creating a new issue, if no open issue for the bug already exists.
