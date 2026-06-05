@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Python executable not found:
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

pushd "%SCRIPT_DIR%"

"%PYTHON_EXE%" -m src.scheduler
set "EXIT_CODE=%ERRORLEVEL%"

if not "%EXIT_CODE%"=="0" (
    echo Scheduler failed with exit code %EXIT_CODE%.
    echo Please check dependencies, .env, TUSHARE_TOKEN, Cloudflare D1 config, or network access.
    echo.
    echo If this is the first run, install dependencies with:
    echo "%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements.txt"
    popd
    pause
    exit /b %EXIT_CODE%
)

popd
