@echo off
python -m pip install --upgrade pytest

:: Run the pytest command
python -m pytest

echo.
echo Tested with pyTest
pause
