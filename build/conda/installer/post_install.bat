@echo off
echo Installing environment, this may take a few moments... Watch for changes in %PREFIX%\post_install_log.txt

cd %PREFIX%

PATH %PREFIX%;%PREFIX%\Scripts;%PREFIX%\Library\bin;%PATH%
SET LOG_FILE="%PREFIX%\post_install_log.txt"

python -m pip install -U pip >> "%LOG_FILE%" 2>&1
pip -m pip install -U setuptools >> "%LOG_FILE%" 2>&1
pip install -U -r requirements.txt >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: pip install failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "pip install completed successfully."
)

echo Package installation completed successfully. Building OpenBB's Python interface...

python -c "import openbb; openbb.build()" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: building OpenBB's Python interface failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "OpenBB's Python interface built successfully."
)

cscript "%PREFIX%\assets\create_shortcut.vbs" >> "%LOG_FILE%" 2>&1
IF ERRORLEVEL 1 (
    call :log_with_timestamp "Error during post-installation: creating shortcuts failed."
    exit /b 1
) ELSE (
    call :log_with_timestamp "Shortcuts created successfully."
)

echo Post-installation steps completed successfully.

exit /b 0

goto :eof

REM Function to add timestamp
:log_with_timestamp
    echo %date%_%time% %1 >> %LOG_FILE%
    goto :eof