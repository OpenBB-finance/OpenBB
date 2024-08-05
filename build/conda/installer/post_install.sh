#!/bin/bash

# Setup environment.
export PATH="$PREFIX/bin:$PATH"
PYTHON_EXEC="$PREFIX/bin/python"
IPYTHON_EXEC="$PREFIX/bin/ipython"
POETRY_EXEC="$PREFIX/bin/poetry"
REQUIREMENTS_FILE="$PREFIX/requirements.txt"
LOG_FILE="$PREFIX/post_install_log.txt"
CWDIR=$(dirname "$PREFIX")

# Function to add timestamp.
log_with_timestamp() {
    echo "$(date '+%Y-%m-%d_%H:%M:%S') $1" >>"$LOG_FILE"
}

# Update pip and setuptools.
"$PYTHON_EXEC" -m pip install -U pip setuptools>>"$LOG_FILE" 2>&1

"$PYTHON_EXEC" -m pip install poetry >>"$LOG_FILE" 2>&1

cd "$CWDIR/openbb" >>"$LOG_FILE" 2>&1

"$POETRY_EXEC" config virtualenvs.create false --local >>"$LOG_FILE" 2>&1

"$POETRY_EXEC" env use "$PYTHON_EXEC" >>"$LOG_FILE" 2>&1

"$POETRY_EXEC" lock >>"$LOG_FILE" 2>&1

# Install OpenBB packages.
if "$POETRY_EXEC" install >>"$LOG_FILE" 2>&1; then
    log_with_timestamp "OpenBB Platform installation completed successfully."
else
    log_with_timestamp "Error during post-installation: poetry install failed."
    exit 1
fi

# Build OpenBB Python interface.
"$PYTHON_EXEC" - <<EOF >>"$LOG_FILE" 2>&1
import openbb
openbb.build()
EOF
log_with_timestamp "OpenBB's Python Interface built successfully."

# IPython launcher script initialized with OpenBB.
IPYTHON_WRAPPER_SCRIPT="$PREFIX/bin/openbb-ipython-launcher"

cat > "$IPYTHON_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
"$IPYTHON_EXEC" -c "from openbb import obb;obb" -i
EOF

chmod +x "$IPYTHON_WRAPPER_SCRIPT"

# Bash shell isolated for the OpenBB environment.
SHELL_WRAPPER_SCRIPT="$PREFIX/bin/openbb-bash"

cat > "$SHELL_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
cd "$PREFIX"
"$POETRY_EXEC" env use "$PYTHON_EXEC"
exec bin/bash -i
EOF

chmod +x "$SHELL_WRAPPER_SCRIPT"

# OpenBB package updater script.
OPENBB_UPDATER_SCRIPT="$PREFIX/bin/openbb-updater"

cat > "$OPENBB_UPDATER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
"$PYTHON_EXEC" -m pip install -U pip
cd "$PREFIX"
"$POETRY_EXEC" env use "$PYTHON_EXEC"
"$POETRY_EXEC" lock
"$POETRY_EXEC" install
"$PYTHON_EXEC" -c "import openbb; openbb.build()"
echo "OpenBB Platform updated successfully."
EOF

chmod +x "$OPENBB_UPDATER_SCRIPT"

NOTEBOOK_WRAPPER_SCRIPT="$PREFIX/bin/openbb-notebook"

cat  > "$NOTEBOOK_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
cd "$CWDIR/openbb"
"$POETRY_EXEC" env use "$PYTHON_EXEC"
"$PREFIX/bin/jupyter-notebook"
EOF

chmod +x "$NOTEBOOK_WRAPPER_SCRIPT"

# Create symlinks
if ln -s "$PREFIX/bin/openbb" "$PREFIX/openbb-cli" && \
   ln -s "$PREFIX/bin/openbb-api" "$PREFIX/openbb-api" && \
   ln -s "$NOTEBOOK_WRAPPER_SCRIPT" "$PREFIX/openbb-notebook" && \
   ln -s "$IPYTHON_WRAPPER_SCRIPT" "$PREFIX/openbb-ipython" && \
   ln -s "$SHELL_WRAPPER_SCRIPT" "$PREFIX/openbb-bash" && \
   ln -s "$OPENBB_UPDATER_SCRIPT" "$PREFIX/openbb-updater" && \
   ln -s "$HOME/.openbb_platform" "$PREFIX/openbb-settings"
   ln -s "$HOME/OpenBBUserData" "$PREFIX/openbb-userdata"; then
    log_with_timestamp "Symlinks created successfully." >>"$LOG_FILE" 2>&1
else
    log_with_timestamp "Error during post-installation: creating symlinks failed." >>"$LOG_FILE" 2>&1
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
verify_symlink "$PREFIX/openbb-notebook"
verify_symlink "$PREFIX/openbb-ipython"
verify_symlink "$PREFIX/openbb-bash"
verify_symlink "$PREFIX/openbb-updater"
verify_symlink "$PREFIX/openbb-settings"
verify_symlink "$PREFIX/openbb-userdata"
