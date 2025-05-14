@echo off
cd /d "%~dp0"

rem -- Create a venv if missing.
if not exist venv (
	python -m venv venv
)

rem -- Activate the virtual environment.
call venv/Scripts/Activate

rem -- Install dependencies.
python -m pip install --upgrade -r requirements.txt