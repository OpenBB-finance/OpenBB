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
set "conda_prefix=!CONDA_PREFIX!"
if not defined conda_prefix (
    echo The obb conda environment is not activated
    echo Activate it by running 'conda activate obb'
    exit /b
)

if not "!conda_prefix!" == "obb" (
    echo The obb conda environment is not activated
    echo Activate it by running 'conda activate obb'
    exit /b
)

:: Remove build artifacts
for /f "delims=" %%A in ('where python') do set python_path=%%A
for /f "delims=" %%B in ('dirname "!python_path!"') do set dir=%%B
for /f "delims=" %%C in ('dirname "!dir!"') do set parent_dir=%%C
set site_packages_dir=!parent_dir!\lib\python*\site-packages
for /r "!site_packages_dir!" %%D in (direct_url.json) do if %%~zD LEQ 2 del /f /q "%%D"

:: Say goodbye
echo Done
