@echo off
echo Installing dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo.
    echo [ERROR] Installation failed.
    echo If you see "cmake" errors, Python 3.13 might still be too new for some libraries.
    echo Try installing Python 3.12 instead.
    pause
    exit /b
)

echo.
echo Starting Backend...
start "Filament Backend" cmd /k "uvicorn app.main:app --reload"

echo Starting Frontend...
start "Filament Dashboard" cmd /k "streamlit run dashboard.py"

echo.
echo Done! Both windows should be open.
pause
