"""
Motor Backend para Conversión Audiófila FLAC -> M4A con qaac64.exe (Apple CoreAudio).
GestorBibliotecaMusical v4.0.
"""

import os
import subprocess
from configuracionEstetica import cargar_configuracion

def obtener_ruta_qaac():
    config = cargar_configuracion()
    return config.get("ruta_qaac")

def verificar_qaac_instalado(ruta_qaac=None):
    if not ruta_qaac:
        ruta_qaac = obtener_ruta_qaac()
    if not ruta_qaac or not os.path.exists(ruta_qaac):
        return False
    try:
        res = subprocess.run([ruta_qaac, "--check"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return res.returncode == 0 and "qaac" in res.stdout.lower()
    except Exception:
        return False

def convertir_flac_a_m4a(ruta_flac, ruta_m4a_salida, ruta_qaac=None, bitrate=320, callback_log=None):
    if not ruta_qaac:
        ruta_qaac = obtener_ruta_qaac()
        
    if not verificar_qaac_instalado(ruta_qaac):
        if callback_log: callback_log(f"  ✗ Error: qaac64.exe no está configurado o no funciona en: {ruta_qaac}")
        return False
        
    os.makedirs(os.path.dirname(ruta_m4a_salida), exist_ok=True)
    
    cmd = [
        ruta_qaac,
        "-v", str(bitrate),
        "--copy-artwork",
        "--copy-time",
        ruta_flac,
        "-o", ruta_m4a_salida
    ]
    
    try:
        if callback_log: callback_log(f"  🎵 Codificando FLAC -> AAC {bitrate}kbps (qaac): {os.path.basename(ruta_flac)}")
        res = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if res.returncode == 0 and os.path.exists(ruta_m4a_salida):
            return True
        else:
            if callback_log: callback_log(f"  ✗ Error qaac: {res.stderr}")
            return False
    except Exception as e:
        if callback_log: callback_log(f"  ✗ Excepción ejecutando qaac: {e}")
        return False
