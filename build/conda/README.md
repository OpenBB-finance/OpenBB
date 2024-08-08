# OpenBB Platform Installer

The code in this folder allows creating a packaged installer for the OpenBB Platform using conda constructor.

The installers can be created for Windows (.exe), MacOS (.pkg).

The installer is distributed with a conda environment that contains python and package management tools.
The installer is created by conda constructor.

The dependencies required to run the application are installed from pypi by the constructor's post_install script.

# Build Instructions

1. Create the build environment (see the [Build environment](#build-environment) section)
2. Build the installer (see the [Build command](#build-command) section)

## Build environment

The build environment should be created off the `environments/constructor-env.yml` file.

## Build command

In the `installer` folder run `constructor .` to build the installer.
