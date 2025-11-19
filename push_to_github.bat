@echo off
chcp 65001 >nul
cd /d "%~dp0"
echo Initializing git repository...
git init
echo.
echo Adding remote repository...
git remote add origin https://github.com/amitnh/Fillament_manager.git
echo.
echo Adding all files...
git add .
echo.
echo Committing changes...
git commit -m "Fix run_app.bat to use python -m for uvicorn and streamlit"
echo.
echo Pushing to GitHub...
git branch -M main
git push -u origin main
echo.
echo Done!
pause

