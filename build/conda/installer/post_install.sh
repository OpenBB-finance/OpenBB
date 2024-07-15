#!/bin/bash

# Full path to the Python executable inside the constructed environment
PYTHON_EXEC="$PREFIX/bin/python"
REQUIREMENTS_FILE="$PREFIX/requirements.txt"

# Use the specific Python that comes bundled with the installer
"$PYTHON_EXEC" -m pip install -U -r "$REQUIREMENTS_FILE" >>"$PREFIX/post_install_log.txt" 2>&1

# Check if there was an error
if [ $? -ne 0 ]; then
    echo "Error during post-installation: pip install failed."
    exit 1
fi

# Create launcher
echo "'$PREFIX/bin/openbb'" >>"$PREFIX/openbb"
