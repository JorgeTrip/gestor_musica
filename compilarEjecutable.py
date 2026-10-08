"""
Script de Compilación a Ejecutable Nativo de Windows (.exe) usando PyInstaller.
GestorBibliotecaMusical v4.0.
"""

import os
import subprocess
import sys
import tkinterdnd2
import customtkinter

sys.stdout.reconfigure(encoding='utf-8')
DIRECTORIO_PROYECTO = os.path.dirname(os.path.abspath(__file__))

def compilar():
    print("🚀 Iniciando proceso de compilación a ejecutable con PyInstaller...\n")
    
    path_dnd = os.path.dirname(tkinterdnd2.__file__)
    path_ctk = os.path.dirname(customtkinter.__file__)
    
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--name=GestorBibliotecaMusical",
        "--noconfirm",
        "--onedir",
        "--windowed",
        f"--add-data={path_dnd};tkinterdnd2",
        f"--add-data={path_ctk};customtkinter",
        f"--add-data={os.path.join(DIRECTORIO_PROYECTO, 'version.json')};.",
        os.path.join(DIRECTORIO_PROYECTO, "main.py")
    ]
    
    if os.path.exists(os.path.join(DIRECTORIO_PROYECTO, "git-log.txt")):
        cmd.insert(-1, f"--add-data={os.path.join(DIRECTORIO_PROYECTO, 'git-log.txt')};.")
        
    try:
        res = subprocess.run(cmd, cwd=DIRECTORIO_PROYECTO)
        if res.returncode == 0:
            print(f"\n✅ Compilación exitosa. Ejecutable generado en: {os.path.join(DIRECTORIO_PROYECTO, 'dist', 'GestorBibliotecaMusical')}")
        else:
            print(f"\n✗ Error durante la compilación. Código de salida: {res.returncode}")
    except Exception as e:
        print(f"\n✗ Excepción ejecutando PyInstaller: {e}")

if __name__ == "__main__":
    compilar()
