"""
Motor Backend para Lectura de Versionado Semántico e Historial de Cambios (Changelog).
GestorBibliotecaMusical v4.0.
"""

import json
import os
import subprocess
from configuracionEstetica import DIRECTORIO_PROYECTO

VERSION_JSON = os.path.join(DIRECTORIO_PROYECTO, "version.json")
GIT_LOG_TXT = os.path.join(DIRECTORIO_PROYECTO, "git-log.txt")

def obtener_info_version():
    info_defecto = {"version": "4.0.0", "app_name": "Gestor de Biblioteca Musical Pro", "build_date": "2026-10-08"}
    if os.path.exists(VERSION_JSON):
        try:
            with open(VERSION_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                info_defecto.update(data)
        except Exception:
            pass
    return info_defecto

def obtener_historial_commits():
    if os.path.exists(GIT_LOG_TXT):
        try:
            with open(GIT_LOG_TXT, "r", encoding="utf-8") as f:
                contenido = f.read().strip()
                if contenido:
                    return contenido.splitlines()
        except Exception:
            pass
            
    try:
        res = subprocess.run(["git", "log", "--oneline", "-n", "40"], cwd=DIRECTORIO_PROYECTO, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, encoding="utf-8")
        if res.returncode == 0 and res.stdout.strip():
            return res.stdout.strip().splitlines()
    except Exception:
        pass
        
    return ["v4.0.0 - Se inicializa versión semántica e historial de cambios."]
