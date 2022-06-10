#!/bin/bash

DISK_IMAGE_NAME="OpenBB Terminal"

# exit when any command fails
set -e

# Clean Up artifacts from previous builds
rm -rf build/terminal && rm -rf dist && rm -rf DMG

# Clean up local logging id
rm -rf openbb_terminal/logs

pyinstaller build/pyinstaller/terminal.spec

# Assign icons to the built folder and launcher
osascript build/pyinstaller/setup_icons.applescript

# Create the folder that is used for packaging
mkdir DMG

# Copy relevant artifacts to the packaging folder
cp -r build/pyinstaller/macOS_package_assets/* DMG/

# Copy launcher and other artifacts to the DMG
hdiutil create \
        -volname "$DISK_IMAGE_NAME" \
        -srcfolder DMG \
        -ov \
        -format UDZO \
        "$DISK_IMAGE_NAME".dmg
mv dist/OpenBBTerminal DMG/"$DISK_IMAGE_NAME"/.OpenBB

# Clean Up artifacts from this build
rm -rf build/terminal && rm -rf dist && rm -rf DMG
