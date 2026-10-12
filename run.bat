@echo off
setlocal
chcp 65001 >nul

rem Se positionner dans le repertoire racine du projet
cd /d "%~dp0"

echo ====================================================================
echo        LANCEUR DE L'APPLICATION DE GEODESIE - MERCHICH 3D
echo ====================================================================
echo.

rem 1. Verification de la disponibilite de Python
set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :PYTHON_FOUND
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :PYTHON_FOUND
)

rem Si aucun Python n'est trouve
echo ====================================================================
echo [ERREUR] Python n'est pas installe ou n'est pas accessible via le PATH.
echo.
echo Ce projet necessite Python 3.10 ou une version superieure.
echo.
echo Guide d'installation :
echo   1. Telechargez l'installateur officiel : https://www.python.org/downloads/
echo   2. Lors de l'installation sous Windows, cochez imperativement la case :
echo      "Add python.exe to PATH"
echo   3. Fermez cette invite et relancez 'run.bat'.
echo ====================================================================
echo.
pause
exit /b 1

:PYTHON_FOUND
echo [OK] Python detecte sur le systeme :
%PYTHON_CMD% --version
echo.

rem 2. Verification et creation de l'environnement virtuel .venv si necessaire
if exist ".venv\Scripts\python.exe" goto :VENV_READY

echo [INFO] Environnement virtuel .venv absent. Creation en cours...
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo [ERREUR] Impossible de creer l'environnement virtuel dans '.venv'.
    echo Verifiez que le paquetage venv est installe avec votre version de Python.
    echo ====================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] Environnement virtuel cree avec succes dans .venv.
echo.

:VENV_READY
rem 3. Verification et installation des dependances
if not exist "requirements.txt" goto :SKIP_REQUIREMENTS

echo [INFO] Verification des dependances requises (requirements.txt)...
".venv\Scripts\python.exe" -m pip install -r requirements.txt
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo [ERREUR] Echec lors de l'installation des dependances dans .venv.
    echo Verifiez votre acces Internet ou les paquets listes dans requirements.txt.
    echo ====================================================================
    echo.
    pause
    exit /b 1
)
echo [OK] Dependances verifiees et operationnelles.
echo.

:SKIP_REQUIREMENTS
rem 4. Lancement de l'application graphique principale
echo [INFO] Demarrage de l'application graphique (main.py)...
echo.
".venv\Scripts\python.exe" main.py
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo [ERREUR] L'application s'est arretee suite a une erreur.
    echo Veuillez consulter les messages ci-dessus pour le diagnostic.
    echo ====================================================================
    echo.
    pause
    exit /b 1
)

endlocal
exit /b 0
