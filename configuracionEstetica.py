"""
Módulo de Configuración Estética y Persistencia Global.
GestorBibliotecaMusical v4.0.
"""

import json
import os
from detectoriTunes import (
    detectar_ruta_itunes,
    obtener_xml_itunes,
    obtener_auto_add_itunes,
    obtener_music_dir_itunes
)

DIRECTORIO_PROYECTO = os.path.dirname(os.path.abspath(__file__))
BASE_DATOS_CACHE = os.path.join(DIRECTORIO_PROYECTO, "baseDatosEscaneo.db")
CONFIG_JSON = os.path.join(DIRECTORIO_PROYECTO, "configuracion.json")

# Paleta de Colores 'Apple Grises Pro'
COLOR_FONDO_OSCURO = "#1C1C1E"
COLOR_TARJETA_OSCURO = "#2C2C2E"
COLOR_BORDE_OSCURO = "#3A3A3C"
COLOR_TEXTO_PRINCIPAL = "#FFFFFF"
COLOR_TEXTO_SECUNDARIO = "#8E8E93"

COLOR_ACENTO_AZUL = "#0A84FF"
COLOR_ACENTO_VERDE = "#30D158"
COLOR_ACENTO_NARANJA = "#FF9F0A"
COLOR_ACENTO_ROJO = "#FF453A"

TEMA_DEFECTO = "Dark"
COLOR_TEMA = "blue"

FUENTE_TITULO = ("SF Pro Display", 20, "bold")
FUENTE_SUBTITULO = ("SF Pro Display", 14, "bold")
FUENTE_NORMAL = ("SF Pro Text", 12)
FUENTE_PEQUENA = ("SF Pro Text", 10)

def cargar_configuracion():
    config_defecto = {
        "ruta_itunes": None,
        "ruta_biblioteca_pc": None,
        "ruta_qaac": r"C:\Archivos de programa2\qaac_2.85\x64\qaac64.exe" if os.path.exists(r"C:\Archivos de programa2\qaac_2.85\x64\qaac64.exe") else None
    }
    if os.path.exists(CONFIG_JSON):
        try:
            with open(CONFIG_JSON, "r", encoding="utf-8") as f:
                data = json.load(f)
                config_defecto.update(data)
        except Exception:
            pass
    return config_defecto

def guardar_configuracion(clave, valor):
    config = cargar_configuracion()
    config[clave] = valor
    try:
        with open(CONFIG_JSON, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

def obtener_ruta_itunes_activa():
    config = cargar_configuracion()
    return detectar_ruta_itunes(config.get("ruta_itunes"))

def obtener_ruta_musica_activa():
    r_it = obtener_ruta_itunes_activa()
    return obtener_music_dir_itunes(r_it) if r_it else None

def obtener_ruta_auto_add_activa():
    r_it = obtener_ruta_itunes_activa()
    return obtener_auto_add_itunes(r_it) if r_it else None
