#!/bin/bash

# Setup environment.
export PATH="$PREFIX/bin:$PATH"
LOG_FILE="$PREFIX/../post_install_log.txt"

# Function to add timestamp.
log_with_timestamp() {
    echo "$(date '+%Y-%m-%d_%H:%M:%S') $1" >>"$LOG_FILE"
}

cd "$PREFIX/../extensions/openbb_platform_installer" >>"$LOG_FILE" 2>&1

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
source activate base
conda activate obb
ipython -c "from openbb import obb;obb" -i
EOF

chmod +x "$IPYTHON_WRAPPER_SCRIPT"

# Bash shell isolated for the OpenBB environment.
SHELL_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/bash"

cat > "$SHELL_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
cd "$PREFIX/.."
source activate base
echo "Conda base environment is active but not initialized. Use this shell to create new environments."
echo "To initialize and activate the OpenBB environment, run 'source activate obb'."
exec $PREFIX/bin/bash -i
EOF

chmod +x "$SHELL_WRAPPER_SCRIPT"

NOTEBOOK_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-notebook"

cat  > "$NOTEBOOK_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate base
conda activate obb
cd "$PREFIX/.."
jupyter notebook "\$@"
EOF

chmod +x "$NOTEBOOK_WRAPPER_SCRIPT"

API_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-api-launcher"

cat  > "$API_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate base
conda activate obb
openbb-api --login True "\$@"
EOF

chmod +x "$API_WRAPPER_SCRIPT"

CLI_WRAPPER_SCRIPT="$PREFIX/envs/obb/bin/openbb-cli"

cat  > "$CLI_WRAPPER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate base
conda activate obb
openbb "\$@"
EOF

chmod +x "$CLI_WRAPPER_SCRIPT"

OPENBB_UPDATER_SCRIPT="$PREFIX/envs/obb/bin/openbb-updater"

cat > "$OPENBB_UPDATER_SCRIPT" <<EOF
#!$PREFIX/bin/bash
export PATH="$PREFIX/bin:\$PATH"
source activate base
conda activate obb
openbb-update "\$@"
EOF

chmod +x "$OPENBB_UPDATER_SCRIPT"

TARGET_DIR="$PREFIX/.."

mkdir -p "$TARGET_DIR"

if ln -s "$CLI_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-cli" && \
   ln -s "$API_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-api" && \
   ln -s "$NOTEBOOK_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-notebook" && \
   ln -s "$IPYTHON_WRAPPER_SCRIPT" "$TARGET_DIR/openbb-ipython" && \
   ln -s "$SHELL_WRAPPER_SCRIPT" "$TARGET_DIR/Bash" && \
   ln -s "$OPENBB_UPDATER_SCRIPT" "$TARGET_DIR/Update" && \
   ln -s "$HOME/.openbb_platform" "$TARGET_DIR/Settings"  && \
   ln -s "$PREFIX/envs" "$TARGET_DIR/Environments"  && \
   ln -s "$HOME/OpenBBUserData" "$TARGET_DIR/OpenBBUserData"; then
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

verify_symlink "$TARGET_DIR/openbb-cli"
verify_symlink "$TARGET_DIR/openbb-api"
verify_symlink "$TARGET_DIR/openbb-notebook"
verify_symlink "$TARGET_DIR/openbb-ipython"
verify_symlink "$TARGET_DIR/Bash"
verify_symlink "$TARGET_DIR/Update"
verify_symlink "$TARGET_DIR/Settings"
verify_symlink "$TARGET_DIR/OpenBBUserData"
verify_symlink "$TARGET_DIR/Environments"
