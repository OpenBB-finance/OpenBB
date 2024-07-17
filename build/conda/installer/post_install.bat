@echo off
echo Running post-installation environment setup.

REM Full path to the Python executable inside the constructed environment
SET PYTHON_EXEC="%PREFIX%\python.exe"
SET REQUIREMENTS_FILE="%PREFIX%\requirements.txt"
SET LOG_FILE="%PREFIX%\post_install_log.txt"

REM Function to add timestamp
:log_with_timestamp
    echo %date%_%time% %1 >> %LOG_FILE%
    goto :eof

REM Use the specific Python that comes bundled with the installer
"%PYTHON_EXEC%" -m pip install -U -r "%REQUIREMENTS_FILE%" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: pip install failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "pip install completed successfully."
)

REM Build OpenBB's python interface
"%PYTHON_EXEC%" -c "import openbb; openbb.build()" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: building OpenBB's python interface failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "OpenBB's python interface built successfully."
)

REM Create shortcuts using the VBS script
cscript "%PREFIX%\assets\create_shortcut.vbs" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: creating shortcuts failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "Shortcuts created successfully."
)

echo Post-installation steps completed successfully.
exit /b 0
