@echo off
setlocal enabledelayedexpansion

:: This script is used to remove artifacts left from the conda build process

:: Ensure that conda is installed
where conda >nul 2>nul
if errorlevel 1 (
    echo conda could not be found
    exit /b
)


:: Ensure that the obb conda environment exists
for /f %%A in ('conda env list ^| findstr /c:"obb"') do set env_exists=1
if not defined env_exists (
    echo The obb conda environment does not exist
    echo Create it by running:
    echo conda env create -n obb --file build/conda/conda-3-10-env.yaml
    exit /b
)


:: Ensure that the obb conda environment is activated
set "path=!CONDA_PREFIX!"
set "conda_prefix=%CONDA_DEFAULT_ENV%"
if not defined conda_prefix (
    echo The obb conda environment is not activated
    echo Activate it by running 'conda activate obb'
    exit /b
)

if not !conda_prefix! == %CONDA_DEFAULT_ENV% (
    echo The obb conda environment is not activated
    echo Activate it by running 'conda activate obb'
    exit /b
)

:: Remove build artifacts
set site_packages_dir=!path!\Lib\site-packages
cd !site_packages_dir!
echo !site_packages_dir!
@REM For /r %%~1f IN (direct_url.json) do Echo "%~1f"

set "cwd=!site_packages_dir!"
for /f "delims=" %%a in ('dir /b /s /a-d direct_url.json') do (del /f /q %%a)


:: Say goodbye
echo Done
