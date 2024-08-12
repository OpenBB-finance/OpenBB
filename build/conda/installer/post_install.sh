#!/bin/bash

# Setup environment.
export PATH="$PREFIX/bin:$PATH"
LOG_FILE="$PREFIX/../post_install_log.txt"
CWDIR=$(dirname "$PREFIX")

# Function to add timestamp.
log_with_timestamp() {
    echo "$(date '+%Y-%m-%d_%H:%M:%S') $1" >>"$LOG_FILE"
}

cd "$PREFIX/.." >>"$LOG_FILE" 2>&1

source "$PREFIX/etc/profile.d/conda.sh" && conda activate "$PREFIX"

conda activate obb >>"$LOG_FILE" 2>&1

python -m pip install -U pip >>"$LOG_FILE" 2>&1

pip install -U setuptools poetry >>"$LOG_FILE" 2>&1

poetry config virtualenvs.path "$PREFIX/envs" --local >>"$LOG_FILE" 2>&1

poetry config virtualenvs.create false --local >>"$LOG_FILE" 2>&1

poetry lock >>"$LOG_FILE" 2>&1


# Install OpenBB packages.
if poetry install >>"$LOG_FILE" 2>&1; then
    log_with_timestamp "OpenBB Platform installation completed successfully."
else
    log_with_timestamp "Error during post-installation: poetry install failed."
    exit 1
fi

# Build OpenBB Python interface.
python - <<EOF >>"$LOG_FILE" 2>&1
import openbb
openbb.build()
EOF
log_with_timestamp "OpenBB's Python Interface built successfully."

# IPython launcher script initialized with OpenBB.
IPYTHON_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-ipython-launcher"

cat > "$IPYTHON_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate $PREFIX/envs/obb
ipython -c "from openbb import obb;obb" -i
EOF

chmod +x "$IPYTHON_WRAPPER_SCRIPT"

# Bash shell isolated for the OpenBB environment.
SHELL_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/bash"

cat > "$SHELL_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
cd "$PREFIX/.."
$PREFIX/bin/activate base
echo
echo "Conda base environment is active, but not initialized. Use this shell to create new environments."
echo "To initialize and activate the OpenBB environment, run 'source activate conda/envs/obb'."
echo
exec $PREFIX/bin/bash -i
EOF

chmod +x "$SHELL_WRAPPER_SCRIPT"

NOTEBOOK_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-notebook"

cat  > "$NOTEBOOK_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source "$PREFIX/etc/profile.d/conda.sh" && conda activate "$PREFIX"
conda activate obb
cd "$PREFIX/../.."
jupyter notebook "\$@"
EOF

chmod +x "$NOTEBOOK_WRAPPER_SCRIPT"

API_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-api"

cat  > "$API_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
cd "$PREFIX/.."
source activate $PREFIX/envs/obb
python -m openbb_platform.api --login True "\$@"
EOF

chmod +x "$API_WRAPPER_SCRIPT"

CLI_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-cli"

cat  > "$CLI_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate $PREFIX/envs/obb
openbb "\$@"
EOF

chmod +x "$CLI_WRAPPER_SCRIPT"

OPENBB_UPDATER_SCRIPT="$PREFIX/bin/openbb-updater"

cat > "$OPENBB_UPDATER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate $PREFIX/envs/obb
openbb-update "\$@"
EOF

chmod +x "$OPENBB_UPDATER_SCRIPT"

TARGET_DIR="$PREFIX/../Shortcuts"

mkdir -p "$TARGET_DIR"

if ln -s "$CLI_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-cli" && \
   ln -s "$API_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-api" && \
   ln -s "$NOTEBOOK_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-notebook" && \
   ln -s "$IPYTHON_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-ipython" && \
   ln -s "$SHELL_WRAPPER_SCRIPT" "$PREFIX/../Bash" && \
   ln -s "$OPENBB_UPDATER_SCRIPT" "$TARGET_DIR/openbb-update" && \
   ln -s "$HOME/.openbb_platform" "$PREFIX/../Settings"  && \
   ln -s "$PREFIX/envs" "$PREFIX/../Environments"  && \
   ln -s "$HOME/OpenBBUserData" "$PREFIX/../OpenBBUserData"; then
    log_with_timestamp "Symlinks created successfully." >>"$LOG_FILE" 2>&1
else
    log_with_timestamp "Error during post-installation: creating symlinks failed." >>"$LOG_FILE" 2>&1
fi

verify_symlink() {
    if [ -L "$1" ] && [ -e "$1" ]; then
        log_with_timestamp "Symlink $1 verified successfully."
    else
        log_with_timestamp "Error: Symlink $1 is not working."
        exit 1
    fi
}

verify_symlink "$PREFIX/../Shortcuts/openbb-cli"
verify_symlink "$PREFIX/../Shortcuts/openbb-api"
verify_symlink "$PREFIX/../Shortcuts/openbb-notebook"
verify_symlink "$PREFIX/../Shortcuts/openbb-ipython"
verify_symlink "$PREFIX/../Bash"
verify_symlink "$PREFIX/../Shortcuts/openbb-update"
verify_symlink "$PREFIX/../Settings"
verify_symlink "$PREFIX/../OpenBBUserData"
verify_symlink "$PREFIX/../Environments"
