@echo off
cd /d %~dp0

REM Activate virtual environment
call venv\Scripts\activate.bat

python send_to_kindle.py

echo.
pause