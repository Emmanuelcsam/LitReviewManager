@echo off
echo ================================================
echo    Literature Review Manager - Setup Script
echo ================================================

echo.
echo Checking for Python 3...
where python >nul 2>nul
if %ERRORLEVEL% neq 0 (
    echo Python is not installed. Please install it and try again.
    echo Visit: https://www.python.org/downloads/
    exit /b 1
) else (
    python --version
    echo Python is installed
)

echo.
echo Setting up a virtual environment...
if exist venv (
    echo Virtual environment already exists.
    set /p answer="Recreate? (y/n): "
    if /i "%answer%"=="y" (
        rmdir /s /q venv
        python -m venv venv
    )
) else (
    python -m venv venv
)

echo.
echo Activating virtual environment...
call venv\Scripts\activate

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing required Python packages...
echo Installing core dependencies...
pip install pandas PyYAML markdown python-docx flask openpyxl

echo Installing PDF handling packages...
pip install pdfplumber PyPDF2

echo Installing DOCX handling packages...
pip install docx2txt

echo.
echo Installation complete!
echo.
echo To run the applications:
echo 1. Flask Web App: python LRSheets.py
echo 2. Desktop App: python LRSheets2.py
echo 3. Or simply open the HTML files in a web browser
echo.
echo For PDF support on Windows, please refer to the README.md file.

pause
