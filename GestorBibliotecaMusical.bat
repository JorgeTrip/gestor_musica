@echo off
chcp 65001 > nul
title Gestor de Biblioteca Musical Pro v4.0

if exist "%~dp0dist\GestorBibliotecaMusical\GestorBibliotecaMusical.exe" (
    start "" "%~dp0dist\GestorBibliotecaMusical\GestorBibliotecaMusical.exe"
    exit /b 0
)

set "PYTHON_EXE=python"
where python.exe >nul 2>&1
if %errorlevel% neq 0 (
    if exist "C:\Program Files\Python313\python.exe" (
        set "PYTHON_EXE=C:\Program Files\Python313\python.exe"
    ) else (
        set "PYTHON_EXE=py"
    )
)

"%PYTHON_EXE%" "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo ==========================================================
    echo Ocurrió un error al lanzar la aplicación.
    echo Presiona cualquier tecla para salir...
    pause > nul
)
