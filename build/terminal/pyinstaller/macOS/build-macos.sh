#!/bin/bash

#Parameters
SCRIPTPATH="$( cd -- "$(dirname "$0")" >/dev/null 2>&1 ; pwd -P )"
TARGET_DIRECTORY="$SCRIPTPATH/target"
BASE_DIRECTORY="$( cd -- "$(dirname "$1")" >/dev/null 2>&1 ; pwd -P )"
APP_DIRECTORY="$BASE_DIRECTORY/DMG/OpenBB Terminal"
BINARIES="$BASE_DIRECTORY/DMG/OpenBB\ Terminal/.OpenBB"
ENTITLEMENTS="$BASE_DIRECTORY/build/pyinstaller/entitlements.plist"
PRODUCT=${1}
VERSION=${2}
DATE=`date +%Y-%m-%d`
TIME=`date +%H:%M:%S`
LOG_PREFIX="[$DATE $TIME]"


function printUsage() {
  echo -e "\033[1mUsage:\033[0m"
  echo "$0 [APPLICATION_NAME] [APPLICATION_VERSION]"
  echo
  echo -e "\033[1mOptions:\033[0m"
  echo "  -h (--help)"
  echo
  echo -e "\033[1mExample::\033[0m"
  echo "$0 openbbpro 0.0.1"

}

#Argument validation
if [ -z "$APPLE_DEVELOPER_CERTIFICATE_ID" ]; then
    echo "APPLE_DEVELOPER_CERTIFICATE_ID environment variable is not set"
    echo "Please run 'security find-identity -v', and then use the value for"
    echo "the developer ID Installer (and NOT the Developer ID Application)"
    exit 1
fi
if [[ "$1" == "-h" ||  "$1" == "--help" ]]; then
    printUsage
    exit 1
fi
if [ -z "$1" ]; then
    echo "Please enter a valid application name for your application"
    echo
    printUsage
    exit 1
else
    echo "Application Name : $1"
fi
if [[ "$2" =~ [0-9]+.[0-9]+.[0-9]+ ]]; then
    echo "Application Version : $2"
else
    echo "Please enter a valid version for your application (format [0-9].[0-9].[0-9])"
    echo
    printUsage
    exit 1
fi
if [ -z "$APPLE_SIGNING_IDENTITY" ]; then
    echo "Please set the APPLE_SIGNING_IDENTITY environment variable"
    exit 1
fi

#Functions
go_to_dir() {
    pushd $1 >/dev/null 2>&1
}

log_info() {
    echo "${LOG_PREFIX}[INFO]" $1
}

log_warn() {
    echo "${LOG_PREFIX}[WARN]" $1
}

log_error() {
    echo "${LOG_PREFIX}[ERROR]" $1
}

deleteInstallationDirectory() {
    log_info "Cleaning $TARGET_DIRECTORY directory."
    rm -rf "$TARGET_DIRECTORY"

    if [[ $? != 0 ]]; then
        log_error "Failed to clean $TARGET_DIRECTORY directory" $?
        exit 1
    fi
}

signFiles() {
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*.so
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*.so
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*/*.so
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*/*/*.so
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*/*/*/*.so
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*/*/*/*/*.so
    echo "Code Signing DYLIB Files"
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*/*/*/*/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/pyarrow/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/.dylibs/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/scipy/.dylibs/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/xgboost/.dylibs/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/stan_model/cmdstan-2.26.1/stan/lib/stan_math/lib/tbb/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/torch/.dylibs/*.dylib
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/sklearn/.dylibs/*.dylib
    echo "Coce Signing LIB Files"
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/*.lib
    echo "Code Signing Other Files"
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/stan_model/prophet_model.bin
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/stan_model/cmdstan-2.26.1/bin/diagnose
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/stan_model/cmdstan-2.26.1/bin/print
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/stan_model/cmdstan-2.26.1/bin/stanc
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/prophet/stan_model/cmdstan-2.26.1/bin/stansummary
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/pyarrow/plasma-store-server
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/torch/bin/protoc
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/torch/bin/protoc-3.13.0.0
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/torch/bin/torch_shm_manager
    echo "Code Sign OpenBB Executable File"
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/OpenBBTerminal
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/OpenBBPlotsBackend
    codesign --deep --force --verify --verbose --options runtime --entitlements "$ENTITLEMENTS" -s "$APPLE_SIGNING_IDENTITY" build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/pywry
}

createInstallationDirectory() {
    if [ -d "${TARGET_DIRECTORY}" ]; then
        deleteInstallationDirectory
    fi
    mkdir -pv "$TARGET_DIRECTORY"

    if [[ $? != 0 ]]; then
        log_error "Failed to create $TARGET_DIRECTORY directory" $?
        exit 1
    fi
}

copyDarwinDirectory(){
  createInstallationDirectory
  cp -r "$SCRIPTPATH/darwin" "${TARGET_DIRECTORY}/"
  chmod -R 755 "${TARGET_DIRECTORY}/darwin/scripts"
  chmod -R 755 "${TARGET_DIRECTORY}/darwin/Resources"
  chmod 755 "${TARGET_DIRECTORY}/darwin/Distribution"
}

# This creates the target/darwin folder which contains the contents for formatting the installer
# It also created the target/darkwinpkg folder which has the .app to install
copyBuildDirectory() {
    sed -i '' -e 's/__VERSION__/'${VERSION}'/g' "${TARGET_DIRECTORY}/darwin/scripts/postinstall"
    sed -i '' -e 's/__PRODUCT__/'${PRODUCT}'/g' "${TARGET_DIRECTORY}/darwin/scripts/postinstall"
    chmod -R 755 "${TARGET_DIRECTORY}/darwin/scripts/postinstall"

    sed -i '' -e 's/__VERSION__/'${VERSION}'/g' "${TARGET_DIRECTORY}/darwin/Distribution"
    sed -i '' -e 's/__PRODUCT__/'${PRODUCT}'/g' "${TARGET_DIRECTORY}/darwin/Distribution"
    chmod -R 755 "${TARGET_DIRECTORY}/darwin/Distribution"

    sed -i '' -e 's/__VERSION__/'${VERSION}'/g' "${TARGET_DIRECTORY}"/darwin/Resources/*.html
    sed -i '' -e 's/__PRODUCT__/'${PRODUCT}'/g' "${TARGET_DIRECTORY}"/darwin/Resources/*.html
    chmod -R 755 "${TARGET_DIRECTORY}/darwin/Resources/"

    rm -rf "${TARGET_DIRECTORY}/darwinpkg"
    mkdir -p "${TARGET_DIRECTORY}/darwinpkg"

    mkdir -p "${TARGET_DIRECTORY}"/darwinpkg/Applications
    cp -a "${APP_DIRECTORY}" "${TARGET_DIRECTORY}"/darwinpkg/Applications

    rm -rf "${TARGET_DIRECTORY}/package"
    mkdir -p "${TARGET_DIRECTORY}/package"
    chmod -R 755 "${TARGET_DIRECTORY}/package"

    rm -rf "${TARGET_DIRECTORY}/pkg"
    mkdir -p "${TARGET_DIRECTORY}/pkg"
    chmod -R 755 "${TARGET_DIRECTORY}/pkg"
}

# Creates the target/package folder. This includes a basic.pkg file with no formatting
function buildPackage() {
    log_info "Application installer package building started.(1/3)"
    # For now I removed the --identifier
    pkgbuild --version "${VERSION}" \
    --scripts "${TARGET_DIRECTORY}/darwin/scripts" \
    --root "${TARGET_DIRECTORY}/darwinpkg" \
    --identifier "OpenBB Terminal" \
    --ownership preserve \
    "${TARGET_DIRECTORY}/package/${PRODUCT}.pkg"
}

# Creates the target/pkg folder. This includes the finished pkg file to let users download
function buildProduct() {
    log_info "Application installer product building started.(2/3)"
    productbuild --distribution "${TARGET_DIRECTORY}/darwin/Distribution" \
    --resources "${TARGET_DIRECTORY}/darwin/Resources" \
    --package-path "${TARGET_DIRECTORY}/package" \
    --sign "${APPLE_DEVELOPER_CERTIFICATE_ID}" \
    "${TARGET_DIRECTORY}/pkg/$1"
}

function createInstaller() {
    log_info "Application installer generation process started.(3 Steps)"
    buildPackage
    chmod -R 754 "${TARGET_DIRECTORY}/darwinpkg"
    buildProduct OpenBBTerminalM1.pkg
    log_info "Application installer generation steps finished."
}

#Main script
log_info "Installer generating process started."

copyDarwinDirectory
copyBuildDirectory
signFiles
chmod 755 build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/.env
# chmod -R 755 build/pyinstaller/macOS/target/darwinpkg/Applications/OpenBB\ Terminal/.OpenBB/
createInstaller

log_info "Installer generating process finished"
exit 0
