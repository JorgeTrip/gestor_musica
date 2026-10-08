@echo off
chcp 65001 > nul
title Gestor de Biblioteca Musical Pro v4.0

python "%~dp0main.py"
if %errorlevel% neq 0 (
    echo.
    echo ==========================================================
    echo Ocurrió un error al lanzar la aplicación.
    echo Presiona cualquier tecla para salir...
    pause > nul
)
