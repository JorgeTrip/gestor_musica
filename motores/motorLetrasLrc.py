"""
Motor Backend para Búsqueda e Incrustación Inteligente de Letras LRC/Texto con Variantes.
GestorBibliotecaMusical v4.0.
"""

import json
import os
import re
import urllib.parse
import urllib.request
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, USLT
from configuracionEstetica import obtener_ruta_musica_activa
from baseDatosEscaneo import (
    inicializar_base_datos,
    consultar_necesita_escaneo,
    registrar_resultado_escaneo
)

HEADERS = {'User-Agent': 'AntigravityLyricsApp/1.0 ( jorge@example.com )'}

def limpiar_titulo_para_busqueda(titulo):
    tit_clean = re.sub(r'[\(\[\{].*?[\)\]\}]', '', titulo)
    tit_clean = re.sub(r'\s+-\s+(single|remastered|deluxe|live|version|edit).*', '', tit_clean, flags=re.IGNORECASE)
    return tit_clean.strip()

def tiene_letras_incrustadas(ruta_abs):
    ext = os.path.splitext(ruta_abs)[1].lower()
    try:
        if ext == '.m4a':
            audio = MP4(ruta_abs); lyr = audio.tags.get('\xa9lyr', []); return len(lyr) > 0 and len(lyr[0].strip()) > 0
        elif ext == '.mp3':
            audio = ID3(ruta_abs)
            for k in audio.keys():
                if k.startswith('USLT'): return len(str(audio[k].text).strip()) > 0
    except Exception: pass
    return False

def buscar_lrc_online(artista, titulo, duracion_seg=0):
    lrc, es_sinc = _consultar_lrclib(artista, titulo, duracion_seg)
    if lrc: return lrc, es_sinc
    tit_limpio = limpiar_titulo_para_busqueda(titulo)
    if tit_limpio.lower() != titulo.lower():
        lrc, es_sinc = _consultar_lrclib(artista, tit_limpio, duracion_seg)
        if lrc: return lrc, es_sinc
    return None, False

def _consultar_lrclib(artista, titulo, duracion_seg=0):
    url = f"https://lrclib.net/api/get?artist_name={urllib.parse.quote(artista)}&track_name={urllib.parse.quote(titulo)}"
    if duracion_seg > 0: url += f"&duration={int(duracion_seg)}"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            if data.get('syncedLyrics'): return data['syncedLyrics'], True
            if data.get('plainLyrics') and not data.get('instrumental', False): return data['plainLyrics'], False
    except Exception: pass
    return None, False

def incrustar_lrc(ruta_abs, texto_lrc):
    ext = os.path.splitext(ruta_abs)[1].lower()
    try:
        if ext == '.m4a':
            audio = MP4(ruta_abs); audio.tags['\xa9lyr'] = [texto_lrc]; audio.save(); return True
        elif ext == '.mp3':
            audio = ID3(ruta_abs); audio.add(USLT(encoding=3, lang='eng', desc='', text=texto_lrc)); audio.save(); return True
    except Exception: pass
    return False

def extraer_letras_actuales(ruta_abs):
    ext = os.path.splitext(ruta_abs)[1].lower()
    try:
        if ext == '.m4a': audio = MP4(ruta_abs); return audio.tags.get('\xa9lyr', [''])[0]
        elif ext == '.mp3':
            audio = ID3(ruta_abs)
            for k in audio.keys():
                if k.startswith('USLT'): return str(audio[k].text)
    except Exception: pass
    return ""

def ejecutar_letras_incremental(callback_progreso=None, cancel_event=None, modo="completo", ruta_m3u=None):
    dir_musica = obtener_ruta_musica_activa()
    if not dir_musica or not os.path.exists(dir_musica):
        return False, "No existe el directorio de música de iTunes.", 0
    inicializar_base_datos()
    archivos = []
    if modo == "lista_m3u" and ruta_m3u and os.path.exists(ruta_m3u):
        with open(ruta_m3u, 'r', encoding='utf-8', errors='ignore') as f:
            for l in f:
                l_str = l.strip()
                if l_str and not l_str.startswith('#'):
                    r_abs = l_str if os.path.isabs(l_str) else os.path.normpath(os.path.join(dir_musica, l_str))
                    if os.path.exists(r_abs): archivos.append(r_abs)
    else:
        for root, dirs, files in os.walk(dir_musica):
            for f in files:
                if f.lower().endswith(('.m4a', '.mp3')): archivos.append(os.path.join(root, f))
                
    total = len(archivos)
    procesados, incrustadas, omitidas_cache = 0, 0, 0
    for idx, ruta_abs in enumerate(archivos, 1):
        if cancel_event and cancel_event.is_set(): return False, "Proceso cancelado.", incrustadas
        rel_path = os.path.relpath(ruta_abs, dir_musica)
        mtime = os.path.getmtime(ruta_abs)
        if modo != "estricto" and modo != "lista_m3u":
            if not consultar_necesita_escaneo(rel_path, mtime, "letras"): omitidas_cache += 1; procesados += 1; continue
        ext = os.path.splitext(ruta_abs)[1].lower()
        art, tit = None, None
        try:
            if ext == '.m4a': audio = MP4(ruta_abs); art = audio.tags.get('\xa9ART', [None])[0]; tit = audio.tags.get('\xa9nam', [None])[0]
            elif ext == '.mp3': audio = ID3(ruta_abs); art = str(audio['TPE1'].text[0]) if 'TPE1' in audio else None; tit = str(audio['TIT2'].text[0]) if 'TIT2' in audio else None
        except Exception: pass
        if not art or not tit: registrar_resultado_escaneo(rel_path, mtime, "letras", "Sin metadatos"); procesados += 1; continue
        lrc, es_sinc = buscar_lrc_online(art, tit)
        if lrc and incrustar_lrc(ruta_abs, lrc):
            st = "Sincronizada" if es_sinc else "Texto Plano"; registrar_resultado_escaneo(rel_path, mtime, "letras", st); incrustadas += 1
        else: registrar_resultado_escaneo(rel_path, mtime, "letras", "No hallada")
        procesados += 1
        if callback_progreso: callback_progreso(procesados, total, f"Letras: {art} - {tit}")
    return True, f"Escaneo de letras completado ({incrustadas} incrustadas, {omitidas_cache} en caché).", incrustadas
