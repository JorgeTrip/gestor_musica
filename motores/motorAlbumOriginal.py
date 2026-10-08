"""
Motor Backend para Auditoría e Incrustación de Álbum Original, Año de Origen y Carátula HD.
GestorBibliotecaMusical v4.0.
"""

import json
import os
import urllib.parse
import urllib.request
from io import BytesIO
from PIL import Image
from mutagen.mp4 import MP4, MP4Cover
from mutagen.id3 import ID3, APIC, TDRC
from configuracionEstetica import obtener_ruta_musica_activa
from baseDatosEscaneo import (
    inicializar_base_datos,
    consultar_necesita_escaneo,
    registrar_resultado_escaneo
)

HEADERS = {'User-Agent': 'AntigravityOriginalAlbumApp/1.0 ( jorge@example.com )'}

def consultar_datos_originales_mb(artista, titulo):
    query = f'artist:"{artista}" AND recording:"{titulo}"'
    url = f"https://musicbrainz.org/ws/2/recording/?query={urllib.parse.quote(query)}&fmt=json"
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=6) as resp:
            data = json.loads(resp.read().decode('utf-8'))
            recs = data.get('recordings', [])
            if recs:
                rec = recs[0]
                first_release_date = rec.get('first-release-date', '')
                anio_orig = first_release_date.split('-')[0] if first_release_date else None
                releases = rec.get('releases', [])
                album_orig, release_id = None, None
                for rel in releases:
                    if rel.get('status') == 'Official':
                        album_orig = rel.get('title'); release_id = rel.get('id'); break
                if not album_orig and releases:
                    album_orig = releases[0].get('title'); release_id = releases[0].get('id')
                return anio_orig, album_orig, release_id
    except Exception: pass
    return None, None, None

def descargar_caratula_hd(release_id, artista, titulo):
    if release_id:
        url_caa = f"https://coverartarchive.org/release/{release_id}/front-1000"
        try:
            req = urllib.request.Request(url_caa, headers=HEADERS)
            with urllib.request.urlopen(req, timeout=6) as resp:
                data_img = resp.read()
                img = Image.open(BytesIO(data_img))
                if img.width >= 600: return data_img, img.format
        except Exception: pass

    url_it = f"https://itunes.apple.com/search?term={urllib.parse.quote(artista + ' ' + titulo)}&entity=song&limit=1"
    try:
        req = urllib.request.Request(url_it, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=5) as resp:
            res = json.loads(resp.read().decode('utf-8')).get('results', [])
            if res and res[0].get('artworkUrl100'):
                url_hd = res[0]['artworkUrl100'].replace('100x100bb', '1000x1000bb')
                with urllib.request.urlopen(urllib.request.Request(url_hd, headers=HEADERS), timeout=6) as resp_img:
                    data_img = resp_img.read()
                    img = Image.open(BytesIO(data_img))
                    return data_img, img.format
    except Exception: pass
    return None, None

def aplicar_metadatos_originales(ruta_abs, anio_orig, album_orig, img_data, img_fmt):
    ext = os.path.splitext(ruta_abs)[1].lower()
    try:
        if ext == '.m4a':
            audio = MP4(ruta_abs)
            if anio_orig: audio.tags['\xa9day'] = [anio_orig]
            if album_orig: audio.tags['\xa9alb'] = [album_orig]
            if img_data:
                fmt_flag = MP4Cover.FORMAT_PNG if img_fmt == 'PNG' else MP4Cover.FORMAT_JPEG
                audio.tags['covr'] = [MP4Cover(img_data, imageformat=fmt_flag)]
            audio.save(); return True
        elif ext == '.mp3':
            audio = ID3(ruta_abs)
            if anio_orig: audio.add(TDRC(encoding=3, text=anio_orig))
            if img_data:
                mime = 'image/png' if img_fmt == 'PNG' else 'image/jpeg'
                audio.add(APIC(encoding=3, mime=mime, type=3, desc='Cover', data=img_data))
            audio.save(); return True
    except Exception: pass
    return False

def ejecutar_album_original_incremental(callback_progreso=None, cancel_event=None):
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
        if not consultar_necesita_escaneo(rel_path, mtime, "album_orig"): omitidos_cache += 1; procesados += 1; continue
        ext = os.path.splitext(ruta_abs)[1].lower()
        art, tit = None, None
        try:
            if ext == '.m4a': audio = MP4(ruta_abs); art = audio.tags.get('\xa9ART', [None])[0]; tit = audio.tags.get('\xa9nam', [None])[0]
            elif ext == '.mp3': audio = ID3(ruta_abs); art = str(audio['TPE1'].text[0]) if 'TPE1' in audio else None; tit = str(audio['TIT2'].text[0]) if 'TIT2' in audio else None
        except Exception: pass
        if not art or not tit: registrar_resultado_escaneo(rel_path, mtime, "album_orig", "Sin metadatos"); procesados += 1; continue
        anio_orig, album_orig, release_id = consultar_datos_originales_mb(art, tit)
        img_data, img_fmt = descargar_caratula_hd(release_id, art, tit)
        if (anio_orig or album_orig or img_data) and aplicar_metadatos_originales(ruta_abs, anio_orig, album_orig, img_data, img_fmt):
            registrar_resultado_escaneo(rel_path, mtime, "album_orig", f"Año: {anio_orig or 'ND'}"); actualizados += 1
        else: registrar_resultado_escaneo(rel_path, mtime, "album_orig", "No hallado")
        procesados += 1
        if callback_progreso: callback_progreso(procesados, total, f"Álbum: {art} - {tit}")
    return True, f"Auditoría de álbum original completada ({actualizados} actualizadas, {omitidos_cache} en caché).", actualizados
