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
mv dist/OpenBBTerminal DMG/"$DISK_IMAGE_NAME"/.OpenBB

# Create a DMG with create-dmg
#
# NOTE:
# Code signing and notarization requires adding the following:
#
# --codesign "Common name of the Developer certificate"
# --format UDIF
# --notarize "Notarization identity " see:
# https://developer.apple.com/documentation/security/notarizing_macos_software_before_distribution/customizing_the_notarization_workflow

if ! command -v create-dmg &> /dev/null
then
    echo "create could not be found"
    echo "install create-dmg from brew or github"
    exit
fi

create-dmg \
    --volname "OpenBB Terminal" \
    --volicon "images/dmg_volume.icns" \
    --background "images/openbb_dmg_background.png" \
    --icon "OpenBB Terminal" 190 250 \
    --window-pos 190 120 \
    --window-size 800 400 \
    --icon-size 100 \
    --text-size 14 \
    --app-drop-link 600 250 \
    --eula LICENSE \
    --format UDZO \
    --no-internet-enable \
    "OpenBB Terminal".dmg DMG


# Clean Up artifacts from this build
rm -rf build/terminal && rm -rf dist && rm -rf DMG
