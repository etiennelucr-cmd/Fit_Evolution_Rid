@echo off
chcp 65001 >nul
cd /d "%~dp0"
where python >nul 2>nul
if errorlevel 1 (echo Python introuvable. Installez Python 3.10+ et cochez Add to PATH. & pause & exit /b 1)
python -m pip install -r requirements.txt
if errorlevel 1 (echo Erreur installation des dependances. & pause & exit /b 1)
python demarrer.py
if errorlevel 1 (echo Erreur de configuration. & pause & exit /b 1)
python -m streamlit run app.py --server.address 0.0.0.0 --server.port 8501 --server.headless true --browser.gatherUsageStats false
pause
