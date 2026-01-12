@echo off
python -m pip install --upgrade pyinstaller
python -m pip install --upgrade -r requirements.txt
python -m PyInstaller main.spec
echo.
echo Build complete. The executable can be found in the "dist" folder.
pause
