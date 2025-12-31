@echo off
setlocal

REM === Prefer Python 3.11 if present, else fall back ===
set PYEXE=
if exist "C:\Program Files\Python311\python.exe" set "PYEXE=C:\Program Files\Python311\python.exe"
if "%PYEXE%"=="" where py >nul 2>nul && for /f "delims=" %%A in ('py -3.11 -c "print(1)" 2^>nul') do set "PYEXE=py -3.11"
if "%PYEXE%"=="" where python >nul 2>nul && set "PYEXE=python"
if "%PYEXE%"=="" (
  echo Could not find Python. Install Python 3.11 or add it to PATH.
  pause
  exit /b 1
)

REM === cd to this script's directory ===
cd /d "%~dp0"

echo Upgrading essentials...
"%PYEXE%" -m pip install --upgrade pip wheel setuptools >nul
"%PYEXE%" -m pip install -r requirements_flask.txt

echo.
echo Starting Golden Goose APEX (Flask) on http://127.0.0.1:5000
start "" http://127.0.0.1:5000
"%PYEXE%" app_flask.py
pause
