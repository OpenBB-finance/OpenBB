@echo off
setlocal enabledelayedexpansion

REM Check if CONDA_PREFIX is set to check for an active conda environment
IF NOT DEFINED CONDA_PREFIX (
    echo No active conda environment detected.
    exit /b
)

REM Add path to the Python executable in the active conda environment
SET "PYTHON_PATH=%CONDA_PREFIX%\python.exe"

REM Verify the python executable exists
IF NOT EXIST "%PYTHON_PATH%" (
    echo Python executable not found in active conda environment.
    exit /b
)

echo Installing all packages in editable mode ...
for /d /r %%d in (openbb_*) do (
    REM Extract the parent directory from the full path
    for %%i in ("%%~dpd") do set "parentdir=%%~dpi"
    REM Move up one level to the parent directory
    set "parentdir=!parentdir:~0,-1!"

    for %%j in (!parentdir!) do set "dirname=%%~nxj"
    echo Installing !dirname!

    pushd "!parentdir!"
    "%PYTHON_PATH%" -m pip install -U -e . >NUL 2>&1

    popd
)
