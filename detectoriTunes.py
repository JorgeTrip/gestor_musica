"""
Módulo de Detección Inteligente de Carpetas y Biblioteca XML de iTunes.
GestorBibliotecaMusical v4.0.
"""

import os
import winreg

CANDIDATOS_HABITUALES = [
    r"E:\@Musica\iTunes",
    os.path.join(os.path.expanduser("~"), "Music", "iTunes"),
    r"D:\iTunes",
    r"E:\iTunes",
    r"C:\iTunes"
]

def obtener_ruta_registro_itunes():
    try:
        clave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Apple Computer, Inc.\iTunes", 0, winreg.KEY_READ)
        val, _ = winreg.QueryValueEx(clave, "iTunes Folder")
        winreg.CloseKey(clave)
        if val and os.path.exists(val):
            return val
    except Exception:
        pass
    return None

def es_directorio_itunes_valido(ruta):
    if not ruta or not os.path.exists(ruta):
        return False
    xml1 = os.path.join(ruta, "iTunes Music Library.xml")
    xml2 = os.path.join(ruta, "iTunes Library.xml")
    media = os.path.join(ruta, "iTunes Media")
    return os.path.exists(xml1) or os.path.exists(xml2) or os.path.exists(media)

def detectar_ruta_itunes(ruta_configurada=None):
    if ruta_configurada and es_directorio_itunes_valido(ruta_configurada):
        return ruta_configurada
        
    reg_path = obtener_ruta_registro_itunes()
    if reg_path and es_directorio_itunes_valido(reg_path):
        return reg_path
        
    for cand in CANDIDATOS_HABITUALES:
        if es_directorio_itunes_valido(cand):
            return cand
            
    return None

def obtener_xml_itunes(ruta_itunes):
    if not ruta_itunes or not os.path.exists(ruta_itunes):
        return None
    xml1 = os.path.join(ruta_itunes, "iTunes Music Library.xml")
    xml2 = os.path.join(ruta_itunes, "iTunes Library.xml")
    if os.path.exists(xml1): return xml1
    if os.path.exists(xml2): return xml2
    return None

def obtener_auto_add_itunes(ruta_itunes):
    if not ruta_itunes: return None
    
    cand1 = os.path.join(ruta_itunes, "iTunes Media", "Agregar automáticamente a iTunes")
    cand2 = os.path.join(ruta_itunes, "iTunes Media", "Automatically Add to iTunes")
    cand3 = os.path.join(ruta_itunes, "Agregar automáticamente a iTunes")
    cand4 = os.path.join(ruta_itunes, "Automatically Add to iTunes")
    
    for cand in [cand1, cand2, cand3, cand4]:
        if os.path.exists(cand):
            return cand
            
    os.makedirs(cand1, exist_ok=True)
    return cand1

def obtener_music_dir_itunes(ruta_itunes):
    if not ruta_itunes: return None
    ruta_musica = os.path.join(ruta_itunes, "iTunes Media", "Music")
    os.makedirs(ruta_musica, exist_ok=True)
    return ruta_musica
