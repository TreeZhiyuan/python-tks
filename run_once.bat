@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
set "PYTHON_EXE=C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10\python.exe"
set "OUTPUT_DIR=%SCRIPT_DIR%data\moneyflow_cnt_ths"

if not exist "%PYTHON_EXE%" (
    echo Python executable not found:
    echo %PYTHON_EXE%
    pause
    exit /b 1
)

pushd "%SCRIPT_DIR%"

echo Running moneyflow_cnt_ths task...
echo.
"%PYTHON_EXE%" -m src.main %*
set "EXIT_CODE=%ERRORLEVEL%"
echo.

if not "%EXIT_CODE%"=="0" (
    echo Task failed with exit code %EXIT_CODE%.
    echo Please check dependencies, .env, TUSHARE_TOKEN, network access, or input dates.
    echo.
    echo If this is the first run, install dependencies with:
    echo "%PYTHON_EXE%" -m pip install -r "%SCRIPT_DIR%requirements.txt"
    popd
    pause
    exit /b %EXIT_CODE%
)

echo Task completed successfully.

if exist "%OUTPUT_DIR%" (
    echo Opening CSV output directory:
    echo %OUTPUT_DIR%
    start "" "%OUTPUT_DIR%"
) else (
    echo CSV output directory not found:
    echo %OUTPUT_DIR%
)

popd
pause
