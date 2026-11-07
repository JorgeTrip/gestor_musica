@echo off
cd /d "%~dp0"
chcp 65001 > nul
title Gestor de Biblioteca Musical Pro

:: 1. Comprobacion y ejecucion directa del binario compilado si existe
if exist "%~dp0dist\GestorBibliotecaMusical\GestorBibliotecaMusical.exe" goto :iniciarCompilado

:: 2. Deteccion del interprete de Python para ejecucion en desarrollo
set "PYTHON_EXE=python"
where python.exe >nul 2>&1
if %errorlevel% equ 0 goto :lanzarApp

if exist "C:\Program Files\Python313\python.exe" set "PYTHON_EXE=C:\Program Files\Python313\python.exe"
if exist "C:\Program Files\Python313\python.exe" goto :lanzarApp

set "PYTHON_EXE=py"
where py.exe >nul 2>&1
if %errorlevel% equ 0 goto :lanzarApp

echo.
echo ==========================================================
echo   [ERROR] No se encontro un interprete de Python instalado.
echo   Instale Python o compile el ejecutable del proyecto.
echo ==========================================================
echo.
pause
exit /b 1

:: 3. Lanzamiento del ejecutable empaquetado
:iniciarCompilado
start "" /d "%~dp0dist\GestorBibliotecaMusical" "%~dp0dist\GestorBibliotecaMusical\GestorBibliotecaMusical.exe"
exit /b 0

:: 4. Lanzamiento con interprete de Python
:lanzarApp
"%PYTHON_EXE%" "%~dp0main.py"
if %errorlevel% equ 0 exit /b 0

echo.
echo ==========================================================
echo   [ERROR] Ocurrio un fallo al ejecutar la aplicacion.
echo ==========================================================
echo.
pause
