"""
Motor Backend para Ingesta Dual (PC vs. Celular/iTunes), Compresión FLAC y Auto-Inicio iTunes.
GestorBibliotecaMusical v4.0.
"""

import datetime
import os
import re
import shutil
import subprocess
import zipfile
from mutagen.mp4 import MP4
from mutagen.id3 import ID3
from configuracionEstetica import obtener_ruta_auto_add_activa, cargar_configuracion
from baseDatosEscaneo import registrar_ingesta_historial
from motores.motorQaac import convertir_flac_a_m4a
from motores.motorGeneros import leer_artista_titulo, obtener_generos_combinados, aplicar_genero_archivo
from motores.motorLetrasLrc import tiene_letras_incrustadas, buscar_lrc_online, incrustar_lrc
from motores.motorAlbumOriginal import consultar_datos_originales_mb, descargar_caratula_hd, aplicar_metadatos_originales

def verificar_e_iniciar_itunes_minimizado(callback_log=None):
    try:
        tasks = subprocess.check_output(["tasklist"], text=True)
        if "itunes.exe" not in tasks.lower():
            if callback_log: callback_log("  🚀 iTunes cerrado. Iniciando iTunes minimizado para forzar digestión...")
            subprocess.Popen(["powershell", "-Command", "Start-Process iTunes -WindowStyle Minimized"])
    except Exception as e:
        if callback_log: callback_log(f"  ⚠ Aviso auto-inicio iTunes: {e}")

def extraer_metadatos_completos(ruta_abs):
    ext = os.path.splitext(ruta_abs)[1].lower()
    art, tit, alb, anio, pista, disco = "Varios", "Desconocido", "Álbum", "ND", "01", "01"
    try:
        if ext == '.m4a':
            audio = MP4(ruta_abs)
            art = audio.tags.get('\xa9ART', [art])[0]
            tit = audio.tags.get('\xa9nam', [tit])[0]
            alb = audio.tags.get('\xa9alb', [alb])[0]
            anio = audio.tags.get('\xa9day', [anio])[0]
            trkn = audio.tags.get('trkn', [(1, 1)])[0]; pista = f"{trkn[0]:02d}"
            disk = audio.tags.get('disk', [(1, 1)])[0]; disco = f"{disk[0]:02d}"
        elif ext == '.mp3':
            audio = ID3(ruta_abs)
            if 'TPE1' in audio: art = str(audio['TPE1'].text[0])
            if 'TIT2' in audio: tit = str(audio['TIT2'].text[0])
            if 'TALB' in audio: alb = str(audio['TALB'].text[0])
            if 'TDRC' in audio: anio = str(audio['TDRC'].text[0])
            if 'TRCK' in audio: pista = f"{int(str(audio['TRCK'].text[0]).split('/')[0]):02d}"
    except Exception: pass
    return art, tit, alb, anio, pista, disco

def procesar_pipeline_celular(ruta_abs, callback_log=None):
    art, tit, alb, anio, pista, disco = extraer_metadatos_completos(ruta_abs)
    if callback_log: callback_log(f"  🔎 Pipeline Celular (Origen Original): {art} - \"{tit}\"...")
    gen_comb = obtener_generos_combinados(art, tit)
    if gen_comb: aplicar_genero_archivo(ruta_abs, gen_comb)
    if not tiene_letras_incrustadas(ruta_abs):
        lrc, es_sinc = buscar_lrc_online(art, tit)
        if lrc: incrustar_lrc(ruta_abs, lrc)
    anio_orig, album_orig, release_id = consultar_datos_originales_mb(art, tit)
    img_data, img_fmt = descargar_caratula_hd(release_id, art, tit)
    if anio_orig or album_orig or img_data:
        aplicar_metadatos_originales(ruta_abs, anio_orig, album_orig, img_data, img_fmt)
    return gen_comb or "Generos"

def procesar_pipeline_pc(ruta_abs, callback_log=None):
    art, tit, alb, anio, pista, disco = extraer_metadatos_completos(ruta_abs)
    if callback_log: callback_log(f"  🔎 Pipeline PC (Álbum Actual): {art} - \"{tit}\"...")
    gen_comb = obtener_generos_combinados(art, tit)
    if gen_comb: aplicar_genero_archivo(ruta_abs, gen_comb)
    if not tiene_letras_incrustadas(ruta_abs):
        lrc, es_sinc = buscar_lrc_online(art, tit)
        if lrc: incrustar_lrc(ruta_abs, lrc)
    img_data, img_fmt = descargar_caratula_hd(None, art, tit)
    if img_data: aplicar_metadatos_originales(ruta_abs, None, None, img_data, img_fmt)
    return gen_comb or "Generos"

def comprimir_flacs_zip9(lista_flacs, ruta_zip_salida, callback_log=None):
    try:
        os.makedirs(os.path.dirname(ruta_zip_salida), exist_ok=True)
        if callback_log: callback_log(f"  📦 Comprimiendo másteres FLAC (ZIP9): {os.path.basename(ruta_zip_salida)}")
        with zipfile.ZipFile(ruta_zip_salida, 'w', compression=zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
            for f in lista_flacs:
                zf.write(f, arcname=os.path.basename(f)); os.remove(f)
        return True
    except Exception as e:
        if callback_log: callback_log(f"  ✗ Error comprimiendo ZIP: {e}")
        return False

def procesar_ingesta_lote(lista_rutas, destino_tipo, callback_progreso=None, callback_log=None):
    config = cargar_configuracion()
    ruta_pc_root = config.get("ruta_biblioteca_pc")
    dir_auto_add = obtener_ruta_auto_add_activa()
    fecha_hoy = datetime.date.today().strftime("%Y-%m-%d")
    
    archivos_validos = []
    for r in lista_rutas:
        if os.path.isfile(r) and r.lower().endswith(('.m4a', '.mp3', '.flac', '.wav')): archivos_validos.append(r)
        elif os.path.isdir(r):
            for root, dirs, files in os.walk(r):
                for f in files:
                    if f.lower().endswith(('.m4a', '.mp3', '.flac', '.wav')): archivos_validos.append(os.path.join(root, f))
                    
    total = len(archivos_validos)
    if total == 0: return True, "No se encontraron archivos de audio válidos.", 0
    
    procesados_cnt = 0
    flacs_para_zip = {}
    
    for idx, r_src in enumerate(archivos_validos, 1):
        ext = os.path.splitext(r_src)[1].lower()
        r_trabajo = r_src
        if ext in ['.flac', '.wav']:
            m4a_temp = os.path.splitext(r_src)[0] + ".m4a"
            if convertir_flac_a_m4a(r_src, m4a_temp, callback_log=callback_log):
                r_trabajo = m4a_temp
                if destino_tipo == "pc": flacs_para_zip.setdefault(os.path.dirname(r_src), []).append(r_src)
            else: continue
                
        art, tit, alb, anio, pista, disco = extraer_metadatos_completos(r_trabajo)
        
        if destino_tipo == "celular":
            os.makedirs(dir_auto_add, exist_ok=True)
            r_dest = os.path.join(dir_auto_add, os.path.basename(r_trabajo))
            if ext in ['.flac', '.wav']:
                gen_final = procesar_pipeline_celular(r_trabajo, callback_log)
                shutil.move(r_trabajo, r_dest)
            else:
                shutil.copy2(r_src, r_dest)
                gen_final = procesar_pipeline_celular(r_dest, callback_log)
            registrar_ingesta_historial(fecha_hoy, "Celular (iTunes)", os.path.basename(r_dest), art, tit, alb, anio, pista, gen_final, "OK", "OK")
            verificar_e_iniciar_itunes_minimizado(callback_log)
        else:
            gen_final = procesar_pipeline_pc(r_trabajo, callback_log)
            registrar_ingesta_historial(fecha_hoy, "Biblioteca PC", os.path.basename(r_trabajo), art, tit, alb, anio, pista, gen_final, "OK", "OK")
            
        procesados_cnt += 1
        if callback_progreso: callback_progreso(idx, total, f"Procesado: {art} - {tit}")

    if destino_tipo == "pc" and flacs_para_zip:
        for dir_flac, lista_f in flacs_para_zip.items():
            if lista_f:
                art, tit, alb, anio, pista, disco = extraer_metadatos_completos(lista_f[0])
                art_c, alb_c = re.sub(r'[\\/*?:"<>|]', '_', art), re.sub(r'[\\/*?:"<>|]', '_', alb)
                fold = f"{anio} - {alb_c}" if anio != "ND" else alb_c
                r_zip = os.path.join(dir_flac, f"{fold} (FLAC Master).zip")
                comprimir_flacs_zip9(lista_f, r_zip, callback_log)

    return True, f"Proceso de ingesta finalizado ({procesados_cnt} canciones ingresadas).", procesados_cnt
