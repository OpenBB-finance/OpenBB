@echo off
echo Running post-installation environment setup.
REM Full path to the Python executable inside the constructed environment
SET PYTHON_EXEC="%PREFIX%\python.exe"
SET LOG_FILE="%PREFIX%\post_install_log.txt"

REM Use the specific Python that comes bundled with the installer
"%PYTHON_EXEC%" -m pip install -U openbb[all] openbb-cli openbb-platform-pro-backend >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    echo %date% %time% "Error during post-installation: pip install failed." >> %LOG_FILE%
    exit /b 1
) ELSE (
    echo %date% %time% "pip install completed successfully." >> %LOG_FILE%
)

REM Build OpenBB's python interface
"%PYTHON_EXEC%" -c "import openbb; openbb.build()" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    echo %date% %time% "Error during post-installation: building OpenBB's python interface failed."  >> %LOG_FILE%
    exit /b 1
) ELSE (
    echo %date% %time% "OpenBB's python interface built successfully."  >> %LOG_FILE%
)

REM Create shortcuts using the VBS script
cscript "%PREFIX%\assets\create_shortcut.vbs" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    echo %date% %time% "Error during post-installation: creating shortcuts failed."  >> %LOG_FILE%
    exit /b 1
) ELSE (
    echo %date% %time% "Shortcuts created successfully."  >> %LOG_FILE%
)

echo Post-installation steps completed successfully.
exit /b 0
