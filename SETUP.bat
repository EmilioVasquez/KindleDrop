@echo off
SETLOCAL ENABLEDELAYEDEXPANSION

:: Ask for Python path
set /p PYTHON_PATH=Enter full path to your Python executable (e.g., C:\Users\you\AppData\Local\Programs\Python\Python310\python.exe): 


:: Create virtual environment
echo Creating virtual environment in 'venv' folder...
"%PYTHON_PATH%" -m venv venv

:: Activate and install requirements
call venv\Scripts\activate
echo Installing dependencies from requirements.txt...
pip install paramiko python-dotenv

echo.
echo Setup complete! Your virtual environment and Chrome profile are ready.
pause
