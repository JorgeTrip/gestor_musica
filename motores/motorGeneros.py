"""
Motor Backend Autónomo para Etiquetado Inteligente Incremental de Géneros Combinados.
GestorBibliotecaMusical v4.0.
"""

import json
import os
import re
import sys
import time
import urllib.parse
import urllib.request
from mutagen.mp4 import MP4
from mutagen.id3 import ID3, TCON
from configuracionEstetica import obtener_ruta_musica_activa
from baseDatosEscaneo import (
    inicializar_base_datos,
    consultar_necesita_escaneo,
    registrar_resultado_escaneo
)

HEADERS = {'User-Agent': 'AntigravityMusicTagger/1.0 ( jorge@example.com )'}
LASTFM_KEY = "b25b959554ed76058ac220b7b2e0a026"
TAGS_BASURA = {"seen live", "favorites", "favourite", "awesome", "love", "loved", "my favorites", "spotify", "male vocalists", "female vocalists", "check out", "beautiful", "masterpiece", "tracks i own", "favorite songs", "albums i own", "chill", "relax", "all"}

def consultar_musicbrainz(artista, titulo):
    time.sleep(1.1)
    query = f'artist:"{artista}" AND recording:"{titulo}"'
    url = f"https://musicbrainz.org/ws/2/recording/?query={urllib.parse.quote(query)}&fmt=json"
    tags = set()
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            recs = json.loads(resp.read().decode('utf-8')).get('recordings', [])
            if recs:
                for t in recs[0].get('tags', []) + recs[0].get('genres', []):
                    n = t.get('name', '').strip().title()
                    if n and n.lower() not in TAGS_BASURA and n.lower() != artista.lower(): tags.add(n)
    except Exception: pass
    return list(tags)

def consultar_lastfm(artista, titulo):
    tags = set()
    url = f"http://ws.audioscrobbler.com/2.0/?method=track.gettoptags&artist={urllib.parse.quote(artista)}&track={urllib.parse.quote(titulo)}&api_key={LASTFM_KEY}&format=json"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            for item in data.get('toptags', {}).get('tag', []):
                cnt = int(item.get('count', 0))
                n = item.get('name', '').strip()
                if cnt > 5 and n.lower() not in TAGS_BASURA and n.lower() != artista.lower():
                    if re.match(r'^(19|20)?\d0s$', n.lower()): tags.add(n.lower())
                    else: tags.add(n.title())
    except Exception: pass
    return list(tags)

def consultar_deezer_fallback(artista, titulo):
    url = f'https://api.deezer.com/search?q=artist:"{urllib.parse.quote(artista)}" track:"{urllib.parse.quote(titulo)}"&limit=1'
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode('utf-8')).get('data', [])
            if data and data[0].get('album', {}).get('id'):
                alb_id = data[0]['album']['id']
                url_alb = f"https://api.deezer.com/album/{alb_id}"
                with urllib.request.urlopen(urllib.request.Request(url_alb, headers=HEADERS), timeout=5) as resp_alb:
                    d_alb = json.loads(resp_alb.read().decode('utf-8'))
                    return [g['name'].title() for g in d_alb.get('genres', {}).get('data', []) if g.get('name')]
    except Exception: pass
    return []

def consultar_itunes_fallback(artista, titulo):
    url = f"https://itunes.apple.com/search?term={urllib.parse.quote(artista + ' ' + titulo)}&entity=song&limit=1"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            res = json.loads(resp.read().decode('utf-8')).get('results', [])
            if res and res[0].get('primaryGenreName'): return [res[0]['primaryGenreName'].title()]
    except Exception: pass
    return []

def obtener_generos_combinados(artista, titulo):
    mb_tags = consultar_musicbrainz(artista, titulo)
    lfm_tags = consultar_lastfm(artista, titulo)
    combinados, vistos = [], set()
    for t in mb_tags + lfm_tags:
        tl = t.lower()
        if tl not in vistos and tl not in TAGS_BASURA and tl != artista.lower(): vistos.add(tl); combinados.append(t)
    if not combinados:
        for t in consultar_deezer_fallback(artista, titulo):
            tl = t.lower()
            if tl not in vistos and tl not in TAGS_BASURA and tl != artista.lower(): vistos.add(tl); combinados.append(t)
    if not combinados:
        for t in consultar_itunes_fallback(artista, titulo):
            tl = t.lower()
            if tl not in vistos and tl not in TAGS_BASURA and tl != artista.lower(): vistos.add(tl); combinados.append(t)
    return " / ".join(combinados[:6]) if combinados else None

def aplicar_genero_archivo(ruta, nuevo_genero):
    ext = os.path.splitext(ruta)[1].lower()
    try:
        if ext == '.m4a':
            audio = MP4(ruta); audio.tags["\xa9gen"] = [nuevo_genero]; audio.save(); return True
        elif ext == '.mp3':
            audio = ID3(ruta); audio.add(TCON(encoding=3, text=nuevo_genero)); audio.save(); return True
    except Exception: pass
    return False

def leer_artista_titulo(ruta):
    ext = os.path.splitext(ruta)[1].lower()
    art, tit = None, None
    try:
        if ext == '.m4a':
            audio = MP4(ruta); a_l, n_l = audio.tags.get('\xa9ART', []), audio.tags.get('\xa9nam', []); art = a_l[0] if a_l else None; tit = n_l[0] if n_l else None
        elif ext == '.mp3':
            audio = ID3(ruta); art = str(audio['TPE1'].text[0]) if 'TPE1' in audio else None; tit = str(audio['TIT2'].text[0]) if 'TIT2' in audio else None
    except Exception: pass
    return art, tit

def ejecutar_etiquetado_generos_incremental(callback_progreso=None, cancel_event=None):
    dir_musica = obtener_ruta_musica_activa()
    if not dir_musica or not os.path.exists(dir_musica):
        return False, "No existe el directorio de música de iTunes.", 0
    inicializar_base_datos()
    archivos = [os.path.join(root, f) for root, dirs, files in os.walk(dir_musica) for f in files if f.lower().endswith(('.m4a', '.mp3'))]
    total = len(archivos)
    procesados, actualizados, omitidos_cache = 0, 0, 0
    for idx, ruta_abs in enumerate(archivos, 1):
        if cancel_event and cancel_event.is_set(): return False, "Proceso cancelado.", actualizados
        rel_path = os.path.relpath(ruta_abs, dir_musica)
        mtime = os.path.getmtime(ruta_abs)
        if not consultar_necesita_escaneo(rel_path, mtime, "generos"):
            omitidos_cache += 1; procesados += 1; continue
        art, tit = leer_artista_titulo(ruta_abs)
        if not art or not tit: registrar_resultado_escaneo(rel_path, mtime, "generos", "Sin metadatos"); procesados += 1; continue
        genero_comb = obtener_generos_combinados(art, tit)
        if genero_comb and aplicar_genero_archivo(ruta_abs, genero_comb):
            registrar_resultado_escaneo(rel_path, mtime, "generos", genero_comb); actualizados += 1
        else: registrar_resultado_escaneo(rel_path, mtime, "generos", "No hallado")
        procesados += 1
        if callback_progreso: callback_progreso(procesados, total, f"Procesado: {art} - {tit}")
    return True, f"Escaneo de géneros completado ({actualizados} etiquetadas, {omitidos_cache} en caché).", actualizados
