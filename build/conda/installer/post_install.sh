#!/bin/bash

# Full path to the Python executable inside the constructed environment
PYTHON_EXEC="$PREFIX/bin/python"
REQUIREMENTS_FILE="$PREFIX/requirements.txt"
LOG_FILE="$PREFIX/post_install_log.txt"

# Function to add timestamp
log_with_timestamp() {
    echo "$(date '+%Y-%m-%d_%H:%M:%S') $1" >>"$LOG_FILE"
}

# Use the specific Python that comes bundled with the installer
if "$PYTHON_EXEC" -m pip install -U -r "$REQUIREMENTS_FILE" >>"$LOG_FILE" 2>&1; then
    log_with_timestamp "pip install completed successfully."
else
    log_with_timestamp "Error during post-installation: pip install failed."
    exit 1
fi

# Build OpenBB's python interface
"$PYTHON_EXEC" - <<EOF >>"$LOG_FILE" 2>&1
import openbb
openbb.build()
exit()
EOF
log_with_timestamp "OpenBB's python interface built successfully."

# Create symlinks
if {
    ln -s "$PREFIX/bin/openbb" "$PREFIX/openbb-cli"
    ln -s "$PREFIX/bin/openbb-api" "$PREFIX/openbb-api"
} >>"$LOG_FILE" 2>&1; then
    log_with_timestamp "Symlinks created successfully."
else
    log_with_timestamp "Error during post-installation: creating symlinks failed."
    exit 1
fi

# Verify symlinks
verify_symlink() {
    if [ -L "$1" ] && [ -e "$1" ]; then
        log_with_timestamp "Symlink $1 verified successfully."
    else
        log_with_timestamp "Error: Symlink $1 is not working."
        exit 1
    fi
}

verify_symlink "$PREFIX/openbb-cli"
verify_symlink "$PREFIX/openbb-api"
