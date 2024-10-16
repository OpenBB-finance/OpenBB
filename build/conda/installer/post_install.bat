@echo off
echo Installing environment, this may take a few minutes... Watch for changes in post_install_log.txt file at the root of the installation directory.

cd "%PREFIX%\..\extensions\openbb_platform_installer"

PATH %PREFIX%;%PREFIX%\Scripts;%PREFIX%\Library\bin;%PATH%
SET LOG_FILE="%PREFIX%\..\post_install_log.txt"

call "%PREFIX%\Scripts\activate.bat"

call conda activate "%PREFIX%\envs\obb" >> "%LOG_FILE%" 2>&1

python -m pip install -U pip >> "%LOG_FILE%" 2>&1

pip install -U setuptools >> "%LOG_FILE%" 2>&1

pip install poetry >> "%LOG_FILE%" 2>&1

poetry config virtualenvs.path "%PREFIX%\envs" --local >> "%LOG_FILE%" 2>&1

poetry config virtualenvs.create false --local >> "%LOG_FILE%" 2>&1

poetry lock >> "%LOG_FILE%" 2>&1

poetry install >> "%LOG_FILE%" 2>&1

IF ERRORLEVEL 1 (
    echo %date% %time% "Error during post-installation: poetry install failed." >> %LOG_FILE%
    exit /b 1
) ELSE (
    echo %date% %time% "Python environment successfully installed... Building the OpenBB Python interface..." >> %LOG_FILE%
)

echo Python environment successfully installed... Building the OpenBB Python interface...

call openbb-build >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: building OpenBB's Python interface failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "OpenBB's Python interface built successfully."
)

cscript "%PREFIX%\assets\create_shortcut.vbs" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    echo %date% %time% "Error during post-installation: creating shortcuts failed."  >> %LOG_FILE%
    exit /b 1
) ELSE (
    echo %date% %time% "Shortcuts created successfully."  >> %LOG_FILE%
)

echo Post-installation steps completed successfully.

exit /b 0

goto :eof

REM Function to add timestamp
:log_with_timestamp
    echo %date%_%time% %1 >> %LOG_FILE%
    goto :eof