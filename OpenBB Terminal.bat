@echo off
call %UserProfile%/anaconda3/Scripts/activate.bat
call conda activate gst
cd "%UserProfile%\OpenBBTerminal"
call python terminal.py
pause
