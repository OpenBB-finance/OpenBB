#!/bin/bash

DISK_IMAGE_NAME="OpenBB Terminal"
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
BUNDLER_PATH="$SCRIPTPATH/macOS/build-macos.sh"

# exit when any command fails
set -e

# Clean Up artifacts from previous builds
rm -rf build/terminal && rm -rf dist && rm -rf DMG

# Clean up local logging id
rm -rf openbb_terminal/logs

# Running build
pyinstaller build/pyinstaller/terminal.spec # --clean

# Assign icons to the built folder and launcher
osascript build/pyinstaller/setup_icons.applescript

# Create the folder that is used for packaging
mkdir DMG

# Copy relevant artifacts to the packaging folder
cp -r build/pyinstaller/macOS_package_assets/* DMG/
mv dist/OpenBBTerminal DMG/"$DISK_IMAGE_NAME"/.OpenBB
