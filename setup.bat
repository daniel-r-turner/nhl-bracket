@echo off
echo Setting up NHL Bracket project...

:: Create virtual environment if it doesn't exist
if not exist "venv\" (
    echo Creating virtual environment...
    python -m venv venv
)

:: Activate virtual environment
call venv\Scripts\activate.bat

:: Install dependencies
echo Installing Python packages...
pip install -r requirements.txt

:: Run the app
echo Running the app...
python main.py

pause
