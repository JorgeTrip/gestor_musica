"""
Motor Backend para la Exportación de Listas M3U desde XML de iTunes.
GestorBibliotecaMusical v4.0.
"""

import os
import re
import urllib.parse
import xml.etree.ElementTree as ET
from configuracionEstetica import obtener_ruta_itunes_activa, obtener_ruta_musica_activa
from detectoriTunes import obtener_xml_itunes

def ejecutar_exportacion_m3u(callback_progreso=None):
    ruta_itunes = obtener_ruta_itunes_activa()
    if not ruta_itunes:
        return False, "No se encontró el directorio de la biblioteca iTunes.", 0
        
    ruta_xml = obtener_xml_itunes(ruta_itunes)
    if not ruta_xml:
        return False, f"No se encontró el archivo XML de biblioteca en {ruta_itunes}", 0
        
    dir_musica = obtener_ruta_musica_activa()
    tree = ET.parse(ruta_xml)
    root = tree.getroot()
    dict_root = root.find('dict')
    
    tracks, playlists = {}, []
    key_curr = None
    
    for elem in dict_root:
        if elem.tag == 'key': key_curr = elem.text
        elif key_curr == 'Tracks' and elem.tag == 'dict':
            track_k = None
            for tr_elem in elem:
                if tr_elem.tag == 'key': track_k = tr_elem.text
                elif tr_elem.tag == 'dict':
                    tr_dict, sub_k = {}, None
                    for k in tr_elem:
                        if k.tag == 'key': sub_k = k.text
                        elif sub_k: tr_dict[sub_k] = k.text; sub_k = None
                    if track_k: tracks[track_k] = tr_dict
        elif key_curr == 'Playlists' and elem.tag == 'array':
            for pl_elem in elem:
                pl_dict, sub_k = {}, None
                for k in pl_elem:
                    if k.tag == 'key': sub_k = k.text
                    elif k.tag == 'array' and sub_k == 'Playlist Items':
                        items = [ik.text for item_dict in k for ik in item_dict if ik.tag == 'integer']
                        pl_dict['Items'] = items
                    elif sub_k: pl_dict[sub_k] = k.text; sub_k = None
                playlists.append(pl_dict)

    listas_agrupadas = {}
    for pl in playlists:
        nombre = pl.get('Name', '').strip()
        es_sistema = pl.get('Distinguished Kind') or pl.get('Master') or pl.get('Folder')
        items = pl.get('Items', [])
        if es_sistema or not items or nombre in ['Music', 'Música', 'Library', 'Podcasts', 'Audiobooks', 'Biblioteca', 'Todo']:
            continue
        nombre_clean = re.sub(r'[\\/*?:"<>|]', '_', nombre)
        if nombre_clean not in listas_agrupadas or len(items) > len(listas_agrupadas[nombre_clean]['Items']):
            listas_agrupadas[nombre_clean] = pl

    os.makedirs(dir_musica, exist_ok=True)
    exportadas = 0
    total_listas = len(listas_agrupadas)
    
    for idx, (nombre_clean, pl) in enumerate(sorted(listas_agrupadas.items()), 1):
        items = pl.get('Items', [])
        ruta_m3u = os.path.join(dir_musica, f"{nombre_clean}.m3u")
        lineas = ["#EXTM3U\n"]
        tracks_validos = 0
        
        for tid in items:
            t_info = tracks.get(tid)
            if t_info and 'Location' in t_info:
                loc_unquoted = urllib.parse.unquote(t_info['Location'])
                loc_clean = re.sub(r'^file://(localhost)?/', '', loc_unquoted, flags=re.IGNORECASE)
                loc_norm = os.path.normpath(loc_clean)
                if os.path.exists(loc_norm):
                    rel_path = os.path.relpath(loc_norm, dir_musica)
                    if rel_path.startswith("#"): rel_path = f".\\{rel_path}"
                    artist = t_info.get('Artist', 'Varios')
                    name = t_info.get('Name', '')
                    time_sec = int(int(t_info.get('Total Time', 0)) / 1000)
                    lineas.append(f"#EXTINF:{time_sec},{artist} - {name}\n{rel_path}\n")
                    tracks_validos += 1
                    
        if tracks_validos > 0:
            with open(ruta_m3u, 'w', encoding='utf-8') as f_out:
                f_out.writelines(lineas)
            exportadas += 1
            
        if callback_progreso:
            callback_progreso(idx, total_listas, f"Exportada: {nombre_clean}.m3u ({tracks_validos} temas)")

    return True, f"Se exportaron con éxito {exportadas} listas M3U en formato relativo.", exportadas
