set -ex

# Determine the absolute path of the directory containing this script
SCRIPT_DIR=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
# Determine the project root directory, which is two levels above src-tauri/scripts
PROJECT_ROOT="$SCRIPT_DIR/../.."

if [ "$TAURI_ENV_DEBUG" = "true" ]; then
  PROFILE="debug"
else
  PROFILE="release"
fi

# --- Step 1: Fix dylibs for the main binary of the current profile ---
BIN_PATH="$PROJECT_ROOT/target/$PROFILE/openbb-platform"

if [ ! -f "$BIN_PATH" ]; then
  echo "Error: Main binary not found at $BIN_PATH"
  exit 1
fi

LIBCRYPTO_PATH=$(otool -L "$BIN_PATH" | grep 'libcrypto.3.dylib' | awk '{print $1}')
LIBSSL_PATH=$(otool -L "$BIN_PATH" | grep 'libssl.3.dylib' | awk '{print $1}')

install_name_tool -change \
"$LIBCRYPTO_PATH" \
"@executable_path/../Frameworks/libcrypto.3.dylib" \
"$BIN_PATH"

install_name_tool -change \
"$LIBSSL_PATH" \
"@executable_path/../Frameworks/libssl.3.dylib" \
"$BIN_PATH"

echo "Successfully fixed dylibs for $PROFILE binary."

# --- Step 2: If it's a debug build, copy the release binary into the .app's Resources folder ---
if [ "$PROFILE" = "debug" ]; then
  echo "DEBUG BUILD DETECTED: Copying release binary to app bundle."

  # This is the source: the release binary that has already been built
  RELEASE_BIN_SOURCE_PATH="$PROJECT_ROOT/target/release/openbb-platform"

  # This is the destination, inside the .app bundle that Tauri creates before this script runs
  APP_RESOURCES_DIR="$PROJECT_ROOT/target/debug/bundle/macos/OpenBB Platform.app/Contents/Resources"
  DEST_PATH="$APP_RESOURCES_DIR/openbb-platform-release"

  # Verify source and destination exist
  if [ ! -f "$RELEASE_BIN_SOURCE_PATH" ]; then
    echo "Error: Release binary not found at $RELEASE_BIN_SOURCE_PATH. A release build must exist."
    exit 1
  fi
  if [ ! -d "$APP_RESOURCES_DIR" ]; then
    echo "Error: App bundle resources directory not found at $APP_RESOURCES_DIR"
    exit 1
  fi

  echo "Copying $RELEASE_BIN_SOURCE_PATH to $DEST_PATH"
  cp "$RELEASE_BIN_SOURCE_PATH" "$DEST_PATH"
  echo "Successfully copied release binary."
fi
