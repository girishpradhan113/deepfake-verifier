@echo off
TITLE DeepShield Forensic Suite Launcher
COLOR 0A

echo ========================================================
echo   Launching DeepShield Multimodal Forensics Suite...
echo ========================================================

:: 1. Launch FastAPI Backend in a new window
echo Starting FastAPI Backend (Port 8000)...
start "DeepShield Backend" cmd /k "cd /d %~dp0 && call venv\Scripts\activate && uvicorn app.api:app --reload --port 8000"

:: 2. Wait 3 seconds for backend initialization
timeout /t 3 /nobreak >nul

:: 3. Launch Streamlit Dashboard in a new window
echo Starting Streamlit Dashboard (Port 8501)...
start "DeepShield Dashboard" cmd /k "cd /d %~dp0 && call venv\Scripts\activate && streamlit run app/dashboard.py --server.port 8501"

echo.
echo [SUCCESS] Both servers are running in separate windows!
echo - Backend API: http://localhost:8000
echo - Dashboard:   http://localhost:8501
echo.
pause