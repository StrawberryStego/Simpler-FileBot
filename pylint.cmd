@echo off
python -m pip install --upgrade pylint

:: Run the pylint command using PowerShell's execution engine
powershell -Command "python -m pylint $(git ls-files '*.py')"

echo.
echo Tested with pylint
pause
