@echo off
setlocal
chcp 65001 >nul

rem Se positionner dans le repertoire racine du projet
cd /d "%~dp0"

echo ====================================================================
echo      EXECUTION DES TESTS AUTOMATISES - GEODESIE (MERCHICH 3D)
echo ====================================================================
echo.

rem 1. Verification de l'environnement virtuel .venv
if exist ".venv\Scripts\python.exe" goto :VENV_EXISTS

echo [INFO] Environnement virtuel .venv non trouve. Initialisation...

set "PYTHON_CMD="
python --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=python"
    goto :PYTHON_AVAILABLE
)

py -3 --version >nul 2>&1
if not errorlevel 1 (
    set "PYTHON_CMD=py -3"
    goto :PYTHON_AVAILABLE
)

echo ====================================================================
echo [ERREUR] Python n'est pas installe ou n'a pas ete trouve dans le PATH.
echo Impossible d'executer les tests sans interpréteur Python.
echo.
echo Veuillez installer Python 3.10 ou superieur avec l'option :
echo   "Add python.exe to PATH"
echo ====================================================================
echo.
pause
exit /b 1

:PYTHON_AVAILABLE
echo [INFO] Creation de l'environnement virtuel .venv...
%PYTHON_CMD% -m venv .venv
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo [ERREUR] Echec lors de la creation de l'environnement virtuel.
    echo ====================================================================
    echo.
    pause
    exit /b 1
)

if exist "requirements.txt" (
    echo [INFO] Installation des dependances depuis requirements.txt...
    ".venv\Scripts\python.exe" -m pip install -r requirements.txt
    if errorlevel 1 (
        echo.
        echo ====================================================================
        echo [ERREUR] Echec lors de l'installation des dependances de test.
        echo ====================================================================
        echo.
        pause
        exit /b 1
    )
)
echo.

:VENV_EXISTS
rem 2. Execution des tests unitaires et de validation avec pytest
echo [INFO] Lancement de la suite de tests avec pytest...
echo.
".venv\Scripts\python.exe" -m pytest tests/ -v
if errorlevel 1 (
    echo.
    echo ====================================================================
    echo [ECHEC] Un ou plusieurs tests ont echoue.
    echo Examinez les messages de trace ci-dessus pour identifier l'origine.
    echo ====================================================================
    echo.
    pause
    exit /b 1
) else (
    echo.
    echo ====================================================================
    echo [SUCCES] Tous les tests automatises ont ete valides avec succes !
    echo ====================================================================
    echo.
    pause
    exit /b 0
)

endlocal
