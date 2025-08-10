@echo off
echo ========================================
echo  Social Media Automation V2
echo  Starting Application...
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python from https://python.org
    pause
    exit /b 1
)

REM Check if virtual environment exists
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if requirements are installed
if not exist "venv\Lib\site-packages\flask" (
    echo Installing dependencies...
    pip install -r requirements.txt
    if errorlevel 1 (
        echo ERROR: Failed to install dependencies
        pause
        exit /b 1
    )
)

REM Check if .env file exists
if not exist ".env" (
    echo Creating .env file from template...
    copy .env.example .env
    echo.
    echo IMPORTANT: Please edit .env file with your API keys and settings
    echo Press any key to continue after editing .env file...
    pause
)

REM Create necessary directories
if not exist "database" mkdir database
if not exist "logs" mkdir logs
if not exist "uploads" mkdir uploads
if not exist "backups" mkdir backups

REM Check for ChromeDriver
if not exist "chromedriver.exe" (
    echo WARNING: ChromeDriver not found in current directory
    echo Please download ChromeDriver from https://chromedriver.chromium.org/
    echo Or the application will try to find it in system PATH
    echo.
)

echo Starting Social Media Automation V2...
echo.
echo Dashboard will be available at: http://localhost:5000
echo Press Ctrl+C to stop the application
echo.

REM Start the application
python app.py

REM Pause if there's an error
if errorlevel 1 (
    echo.
    echo Application stopped with an error
    pause
)

echo.
echo Application stopped
pause

