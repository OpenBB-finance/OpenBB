@echo off

rem Check if Python is installed
where python >nul 2>nul
if errorlevel 1 (
    echo Python is not installed. Installing Python...
    goto installPython
)

rem Check if pip is installed
python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo Pip is not installed. Installing Pip...
    goto installPip
)

rem Install OpenBB Platform
echo Installing OpenBB Platform...
pip install openbb

rem Install OpenBB Platform CLI
echo Installing OpenBB Platform CLI...
pip install openbb-cli

rem Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

rem Run the OpenBB Platform
echo Starting the OpenBB Platform...
openbb

echo OpenBB Platform setup complete!
pause
exit /b

:installPython
echo Downloading and installing Python...
powershell Invoke-WebRequest -Uri "https://www.python.org/ftp/python/3.9.7/python-3.9.7-amd64.exe" -OutFile "python-installer.exe"
start /wait python-installer.exe /quiet
del python-installer.exe
goto checkPip

:installPip
echo Downloading and installing Pip...
powershell Invoke-WebRequest -Uri "https://bootstrap.pypa.io/get-pip.py" -OutFile "get-pip.py"
python get-pip.py
del get-pip.py
goto installOpenBB

:checkPip
python -m pip --version >nul 2>nul
if errorlevel 1 (
    echo Pip is not installed. Installing Pip...
    goto installPip
)
goto installOpenBB
