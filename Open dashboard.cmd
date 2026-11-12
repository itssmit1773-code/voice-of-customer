@echo off
setlocal
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    py -3.12 -m venv .venv || goto setup_error
)
.venv\Scripts\python.exe -c "import streamlit, altair, pandas" >nul 2>nul
if errorlevel 1 (
    .venv\Scripts\python.exe -m pip install -r requirements.txt || goto setup_error
)
start "" "http://127.0.0.1:8501"
.venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
if errorlevel 1 goto setup_error
exit /b 0

:setup_error
echo Install Python 3.12 or see the setup instructions in README.md.
pause
exit /b 1
