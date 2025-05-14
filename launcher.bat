@echo off
rem -- Ensure we're running in Simpler FileBot's directory.
cd /d "%~dp0"

rem -- Check for venv.
if not exist venv (
	echo [Error] Virtual environment not found.
	echo Please run install_dependencies.bat first.
	pause
	exit /b 1
)

rem -- Activate venv.
call venv/Scripts/activate


rem -- Launch GUI without leaving a console.
start "" pythonw main.py
exit /b 0