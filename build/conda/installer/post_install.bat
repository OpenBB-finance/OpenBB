@echo off
echo Running post-installation environment setup.

REM Full path to the Python executable inside the constructed environment
SET PYTHON_EXEC="%PREFIX%\python.exe"
SET REQUIREMENTS_FILE="%PREFIX%\requirements.txt"

REM Use the specific Python that comes bundled with the installer
"%PYTHON_EXEC%" -m pip install -U -r "%REQUIREMENTS_FILE%" >> "%PREFIX%\post_install_log.txt" 2>&1

REM Check if there was an error
IF ERRORLEVEL 1 (
    echo Error during post-installation: pip install failed.
    exit /b 1
)

cscript "%PREFIX%\assets\create_shortcut.vbs"

echo Post-installation steps completed successfully.
exit /b 0
