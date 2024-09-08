@echo off

set VENV_DIR="venv"
set REQUIREMENTS_FILE="requirements.txt"

REM Determine if 'python' or 'python3' is available
where python > nul 2>&1
if errorlevel 1 (
    set PYTHON_CMD=python3
) else (
    set PYTHON_CMD=python
)

:: Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Creating...
    %PYTHON_CMD% -m venv venv

    if errorlevel 1 (
        echo Failed to create virtual environment. Exiting.
        exit /b 1
    )

    :: Install requirements (since venv was just created)
    if exist "requirements.txt" (
        echo Installing requirements from requirements.txt...
        call venv\Scripts\activate.bat 
        %PYTHON_CMD% -m pip install -r requirements.txt --disable-pip-version-check

        if errorlevel 1 (
            echo Failed to install requirements. Exiting.
            exit /b 1
        )
    )
) else (
    :: Activate the virtual environment
    call venv\Scripts\activate.bat 

    :: Check if requirements are already installed
    %PYTHON_CMD% -m pip install --upgrade --dry-run -r requirements.txt --disable-pip-version-check > requirements_check.txt 2>&1
    findstr /C:"Requirement already satisfied" requirements_check.txt > nul
    if errorlevel 1 (
        echo Installing missing or outdated requirements from requirements.txt...
        %PYTHON_CMD% -m pip install -r requirements.txt --disable-pip-version-check

        if errorlevel 1 (
            echo Failed to install requirements. Exiting.
            exit /b 1
        )
    ) else (
        REM echo All requirements are already up-to-date.
    )
    del requirements_check.txt
)

:: Execute Python script
%PYTHON_CMD% ScriptMetricsMonitor.py

:: Optionally, deactivate the virtual environment after the script finishes
call venv\Scripts\deactivate.bat
exit