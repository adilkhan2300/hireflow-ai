@echo off
title HireFlow AI - Autonomous HR Agent
echo =========================================================================
echo               HireFlow AI - Recruitment & Onboarding System
echo            Academic Subject: AI Agents & Autonomous Business Operations
echo =========================================================================
echo.
echo [1/2] Checking Python environment...
python --version
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    pause
    exit /b
)
echo.
echo [2/2] Launching HireFlow AI Streamlit Application...
echo The dashboard will automatically open in your default browser at:
echo http://localhost:8501
echo.
echo Press Ctrl+C in this terminal window to stop the server when done.
echo -------------------------------------------------------------------------
python -m streamlit run app.py
pause

