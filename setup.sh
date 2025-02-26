#!/bin/bash

# Set colors for better readability
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}==================================================${NC}"
echo -e "${BLUE}   Literature Review Manager - Setup Script       ${NC}"
echo -e "${BLUE}==================================================${NC}"

# Function to check if a command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Check if Python3 is installed
echo -e "\n${YELLOW}Checking for Python 3...${NC}"
if ! command_exists python3; then
  echo -e "${RED}Python3 is not installed. Please install it and try again.${NC}"
  echo -e "Visit: https://www.python.org/downloads/"
  exit 1
else
  python_version=$(python3 --version)
  echo -e "${GREEN}✓ $python_version is installed${NC}"
fi

# Check if pip3 is installed
echo -e "\n${YELLOW}Checking for pip...${NC}"
if ! command_exists pip3 && ! command_exists pip; then
  echo -e "${RED}pip is not installed. Attempting to install...${NC}"
  
  if command_exists apt-get; then
    sudo apt-get update
    sudo apt-get install -y python3-pip
  elif command_exists brew; then
    brew install python # Includes pip
  else
    echo -e "${RED}Could not install pip automatically. Please install pip manually.${NC}"
    exit 1
  fi
else
  echo -e "${GREEN}✓ pip is installed${NC}"
fi

# Create a virtual environment
echo -e "\n${YELLOW}Setting up a virtual environment...${NC}"

# Check if venv exists already
if [ -d "venv" ]; then
  echo -e "${YELLOW}Virtual environment already exists. Recreate? (y/n)${NC}"
  read -r response
  if [[ "$response" =~ ^([yY][eE][sS]|[yY])$ ]]; then
    rm -rf venv
  else
    echo -e "${YELLOW}Using existing virtual environment.${NC}"
  fi
fi

# Create venv if it doesn't exist
if [ ! -d "venv" ]; then
  python3 -m venv venv
  if [ $? -ne 0 ]; then
    echo -e "${RED}Failed to create virtual environment. Trying to install venv...${NC}"
    if command_exists apt-get; then
      sudo apt-get install -y python3-venv
      python3 -m venv venv
    elif command_exists brew; then
      brew install python # Should include venv
      python3 -m venv venv
    else
      echo -e "${RED}Could not install venv. Please install manually with:${NC}"
      echo -e "${YELLOW}pip install virtualenv${NC}"
      exit 1
    fi
  fi
fi

# Activate virtual environment
echo -e "\n${YELLOW}Activating virtual environment...${NC}"
source venv/bin/activate
if [ $? -ne 0 ]; then
  echo -e "${RED}Failed to activate virtual environment.${NC}"
  exit 1
fi
echo -e "${GREEN}✓ Virtual environment activated${NC}"

# Upgrade pip in the virtual environment
echo -e "\n${YELLOW}Upgrading pip...${NC}"
pip install --upgrade pip
echo -e "${GREEN}✓ pip upgraded${NC}"

# Install required Python libraries
echo -e "\n${YELLOW}Installing required Python packages...${NC}"
# Base packages
echo -e "${BLUE}Installing core dependencies...${NC}"
pip install pandas PyYAML markdown python-docx flask openpyxl

# PDF handling packages
echo -e "${BLUE}Installing PDF handling packages...${NC}"
pip install pdfplumber PyPDF2

# DOCX handling packages
echo -e "${BLUE}Installing DOCX handling packages...${NC}"
pip install docx2txt

# GUI packages (for Tkinter - usually included with Python but ensure it's there)
echo -e "${BLUE}Checking for Tkinter...${NC}"
python3 -c "import tkinter" 2>/dev/null
if [ $? -ne 0 ]; then
  echo -e "${YELLOW}Tkinter not found. Installing...${NC}"
  if command_exists apt-get; then
    sudo apt-get install -y python3-tk
  elif command_exists brew; then
    brew install python-tk
  else
    echo -e "${YELLOW}Could not install Tkinter automatically.${NC}"
    echo -e "${YELLOW}Please install Tkinter manually for your system to use the GUI application.${NC}"
  fi
else
  echo -e "${GREEN}✓ Tkinter is available${NC}"
fi

# Check for PDF dependencies at system level
echo -e "\n${YELLOW}Checking for system PDF dependencies...${NC}"
if command_exists apt-get; then
  # For Debian/Ubuntu
  if ! command_exists pdftotext; then
    echo -e "${YELLOW}Installing poppler-utils for better PDF support...${NC}"
    sudo apt-get install -y poppler-utils
  else
    echo -e "${GREEN}✓ poppler-utils is installed${NC}"
  fi
elif command_exists brew; then
  # For macOS
  if ! command_exists pdftotext; then
    echo -e "${YELLOW}Installing poppler for better PDF support...${NC}"
    brew install poppler
  else
    echo -e "${GREEN}✓ poppler is installed${NC}"
  fi
else
  echo -e "${YELLOW}Please install PDF utilities manually if you need PDF support:${NC}"
  echo -e "${YELLOW}- For Ubuntu/Debian: sudo apt-get install poppler-utils${NC}"
  echo -e "${YELLOW}- For macOS: brew install poppler${NC}"
  echo -e "${YELLOW}- For Windows: See pdfplumber documentation${NC}"
fi

# Create a Windows batch file equivalent
echo -e "\n${YELLOW}Creating Windows setup script...${NC}"
cat > setup.bat << 'EOF'
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
EOF

echo -e "\n${GREEN}==================================================${NC}"
echo -e "${GREEN}          Installation complete!                  ${NC}"
echo -e "${GREEN}==================================================${NC}"
echo -e "\nTo run the applications:"
echo -e "1. ${BLUE}Activate the virtual environment:${NC}"
echo -e "   ${YELLOW}source venv/bin/activate${NC}  (Linux/Mac)"
echo -e "   ${YELLOW}venv\\Scripts\\activate${NC}   (Windows)"
echo -e "\n2. ${BLUE}Run one of the applications:${NC}"
echo -e "   ${YELLOW}python LRSheets.py${NC}   (Flask Web App - then visit http://127.0.0.1:5000)"
echo -e "   ${YELLOW}python LRSheets2.py${NC}  (Desktop GUI App)"
echo -e "   Or simply open the HTML files in your browser:"
echo -e "   ${YELLOW}collectreviewsall.html${NC} or ${YELLOW}CollectReviewsmd.html${NC}"
echo -e "\n3. ${BLUE}Deactivate the virtual environment when done:${NC}"
echo -e "   ${YELLOW}deactivate${NC}"
echo -e "\nFor more information, please refer to the README.md file."
