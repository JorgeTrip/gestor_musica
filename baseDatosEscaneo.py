"""
Motor de Base de Datos SQLite para Escaneo Incremental e Historial de Ingesta.
GestorBibliotecaMusical v4.0.
"""

import os
import sqlite3
from configuracionEstetica import BASE_DATOS_CACHE

def obtener_conexion():
    os.makedirs(os.path.dirname(BASE_DATOS_CACHE), exist_ok=True)
    conn = sqlite3.connect(BASE_DATOS_CACHE)
    conn.row_factory = sqlite3.Row
    return conn

def inicializar_base_datos():
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS registro_archivos (
                ruta_relativa TEXT PRIMARY KEY,
                mtime REAL NOT NULL,
                generos_estado TEXT,
                letras_estado TEXT,
                album_orig_estado TEXT,
                ultimo_escaneo TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS historial_ingesta (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                fecha_ingesta TEXT NOT NULL,
                destino TEXT NOT NULL,
                ruta_relativa TEXT NOT NULL,
                artista TEXT,
                titulo TEXT,
                album TEXT,
                anio TEXT,
                pista_nro TEXT,
                generos TEXT,
                letras_status TEXT,
                caratula_status TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.commit()

def consultar_necesita_escaneo(ruta_relativa, mtime_actual, modulo):
    inicializar_base_datos()
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT mtime, generos_estado, letras_estado, album_orig_estado FROM registro_archivos WHERE ruta_relativa = ?", (ruta_relativa,))
        row = cursor.fetchone()
        if not row: return True
        if abs(row["mtime"] - mtime_actual) > 1.0: return True
        if modulo == "generos" and not row["generos_estado"]: return True
        if modulo == "letras" and not row["letras_estado"]: return True
        if modulo == "album_orig" and not row["album_orig_estado"]: return True
        return False

def registrar_resultado_escaneo(ruta_relativa, mtime_actual, modulo, resultado_texto):
    inicializar_base_datos()
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ruta_relativa FROM registro_archivos WHERE ruta_relativa = ?", (ruta_relativa,))
        row = cursor.fetchone()
        columna = f"{modulo}_estado"
        if row:
            cursor.execute(f"UPDATE registro_archivos SET mtime = ?, {columna} = ?, ultimo_escaneo = CURRENT_TIMESTAMP WHERE ruta_relativa = ?", (mtime_actual, resultado_texto, ruta_relativa))
        else:
            cursor.execute(f"INSERT INTO registro_archivos (ruta_relativa, mtime, {columna}) VALUES (?, ?, ?)", (ruta_relativa, mtime_actual, resultado_texto))
        conn.commit()

def registrar_ingesta_historial(fecha_str, destino, rel_path, art, tit, alb, anio, pista, gen, let_st, car_st):
    inicializar_base_datos()
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO historial_ingesta (fecha_ingesta, destino, ruta_relativa, artista, titulo, album, anio, pista_nro, generos, letras_status, caratula_status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (fecha_str, destino, rel_path, art, tit, alb, anio, pista, gen, let_st, car_st))
        conn.commit()

def obtener_historial_agrupado():
    inicializar_base_datos()
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, fecha_ingesta, destino, ruta_relativa, artista, titulo, album, anio, generos
            FROM historial_ingesta ORDER BY fecha_ingesta DESC, id DESC LIMIT 500
        """)
        rows = cursor.fetchall()
        historial = {}
        for r in rows:
            f = r["fecha_ingesta"]
            historial.setdefault(f, []).append(dict(r))
        return historial

def obtener_detalle_historial_por_id(hist_id):
    inicializar_base_datos()
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM historial_ingesta WHERE id = ?", (hist_id,))
        row = cursor.fetchone()
        return dict(row) if row else None

def obtener_estadisticas_cache():
    inicializar_base_datos()
    with obtener_conexion() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM registro_archivos"); total = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registro_archivos WHERE generos_estado IS NOT NULL"); gen = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registro_archivos WHERE letras_estado IS NOT NULL"); let = cursor.fetchone()[0]
        cursor.execute("SELECT COUNT(*) FROM registro_archivos WHERE album_orig_estado IS NOT NULL"); alb = cursor.fetchone()[0]
        return {"total": total, "generos": gen, "letras": let, "albumes": alb}
