@echo off
cd /d "%~dp0"

rem -- Check if Python is available.
python --version > nul 2>&1
if errorlevel 1 (
	echo.
	echo [Error] Python was not found on this system.
	echo Please install Python 3.9+ and make sure it's in your PATH/environment variables.
	pause
	exit /b 1
)

rem -- Create a venv if missing.
if not exist venv (
	python -m venv venv
)

rem -- Activate the virtual environment.
call venv/Scripts/Activate

rem -- Install dependencies.
python -m pip install --upgrade -r requirements.txt
