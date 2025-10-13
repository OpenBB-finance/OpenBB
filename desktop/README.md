# Open Data Platform - by OpenBB - Desktop Application

The ODP Desktop Application enhances the developer experience by lowering the technical barriers to entry
for building, presenting, and sharing data pipelines, insights or dashboarding experiences over multiple interfaces.

This code library represents the complete source code for the Open Data Platform (ODP) desktop application and system tray icon, as published by OpenBB.

The distributed binaries (currently macOS and Windows) are the direct output of build actions, located in this repository, responsible for generating release artifacts.

Please note that while there are no build pipelines for a Linux distribution, it is possible to build and install locally.

## User Documentation & Installation

Official user documentation is located [here](https://docs.openbb.co/desktop).

Download the latest version [here](https://github.com/OpenBB-finance/OpenBB/releases/tag/odp)

The remainder of this document is intended for orienting and onboarding to the codebase.

## Stack Overview

ODP Desktop is built with a Tauri & React framework, the code is approximately 50/50, Rust/TypeScript.

This stack reduces the distribution size by relying on the operating system for window creation.
Installed, it is approximately 35 MB; compressed, 12 MB.

The application is tray icon - background service - where functions rely on developer tools that are installed separately via ODP.
In other words, the application itself is a GUI and wrapper for interacting with the operating system and command line.

It is assumed that no developer tools are installed in the operating system, and the user does not have admin/root access to the machine.
Multi-user machines must be configured per-user.

To facilitate environment management and dependency solving, Miniforge is installed when ODP Desktop is first run.
Conda was selected for its effective isolation patterns, as well as platform and language-agnostic qualities.

The initial installation environment provides a production-ready REST API, MCP server, NodeJS, and Jupyter Lab IDE.

## Running Code

Run this code locally from a development server by following the steps below.

### Rust

You must install, or update, Rust to use version 1.90.0

```sh
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh
```

If you have previously installed Rust, update to the latest version (currently rustc 1.90.0)

```sh
rustup update
```

### NodeJS

NodeJS and NPM must also be available on $PATH.

Follow the instructions [here](https://docs.npmjs.com/downloading-and-installing-node-js-and-npm) if you do not have it installed.

If you already have `npm`, update it before installing the project.

### OpenSSL

OpenSSL must be installed on the system, with exposed environment variables for:

```env
OPENSSL_DIR
OPENSSL_INCLUDE_DIR
OPENSSL_LIB_DIR
```

### Install Project

With those three, items installed and updated, install the project by running the command from the `/desktop` root folder.

```sh
npm install
```

### Develop

Build and start the development server:

```sh
npm run tauri dev
```

This will start the development server and watch for changes to the codebase. Most changes will be picked up, but some events may require a full restart.

If you use a browser, instead of the window, to view the development server there will be stuff that just doesn't work. This is expected.

Ignore all of the warning messages for now, we'll clean those up later.


### Helpful VS Code Extension

- rust-analyzer
- Tauri
- Tailwind CSS IntelliSense

## Building

Production builds are intended to be completed and signed via GitHub actions. Adjustments to `beforeBundleCommand` may be required for builds outside of the official release structure.

