@echo off
setlocal

set "PYTHON_EXE=C:\Users\cuizy52127\AppData\Local\miniconda3\envs\python3.10\python.exe"

if not exist "%PYTHON_EXE%" (
    echo Python executable not found:
    echo %PYTHON_EXE%
    exit /b 1
)

"%PYTHON_EXE%" -m src.scheduler
