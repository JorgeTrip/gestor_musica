"""
Modal Emergente Corrector e Inspector de Letras LRC de Canción Puntual.
GestorBibliotecaMusical v4.0.
"""

import os
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_FONDO_OSCURO,
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    COLOR_ACENTO_VERDE,
    COLOR_ACENTO_ROJO,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)
from motores.motorLetrasLrc import (
    extraer_letras_actuales,
    buscar_lrc_online,
    incrustar_lrc
)
from motores.motorGeneros import leer_artista_titulo

class ModalCorrectorLetraLrc(ctk.CTkToplevel):
    def __init__(self, parent, ruta_audio):
        super().__init__(parent)
        self.ruta_audio = ruta_audio
        self.artista, self.titulo = leer_artista_titulo(ruta_audio)
        
        self.title(f"Corrector de Letras LRC - {self.titulo or 'Canción'}")
        self.geometry("680x600")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.transient(parent)
        self.grab_set()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_tit = ctk.CTkLabel(self, text="🎤 Inspector y Corrector de Letras LRC", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(15, 5))
        
        lbl_sub = ctk.CTkLabel(self, text=f"{self.artista or 'Artista'} - \"{self.titulo or 'Título'}\"", font=FUENTE_SUBTITULO, text_color=COLOR_ACENTO_AZUL)
        lbl_sub.pack(pady=(0, 10))
        
        pnl_actions = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        pnl_actions.pack(fill="x", padx=20, pady=5)
        
        btn_rebuscar = ctk.CTkButton(pnl_actions, text="🔄 Re-Buscar en LRCLIB", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_AZUL, command=self.rebuscar_lrclib)
        btn_rebuscar.pack(side="left", padx=10, pady=10)
        
        btn_guardar = ctk.CTkButton(pnl_actions, text="💾 Guardar Cambios", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_VERDE, command=self.guardar_cambios)
        btn_guardar.pack(side="left", padx=10, pady=10)
        
        btn_borrar = ctk.CTkButton(pnl_actions, text="🗑️ Borrar Letras", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_ROJO, command=self.borrar_letras)
        btn_borrar.pack(side="right", padx=10, pady=10)
        
        self.txt_lrc = ctk.CTkTextbox(self, font=FUENTE_PEQUENA, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.txt_lrc.pack(fill="both", expand=True, padx=20, pady=(5, 10))
        
        letras_actuales = extraer_letras_actuales(self.ruta_audio)
        self.txt_lrc.insert("end", letras_actuales if letras_actuales else "[Sin letras incrustadas actualmente]")
        
        self.lbl_status = ctk.CTkLabel(self, text=f"Archivo: {os.path.basename(self.ruta_audio)}", font=FUENTE_PEQUENA, text_color="#8E8E93")
        self.lbl_status.pack(pady=(0, 10))

    def rebuscar_lrclib(self):
        if not self.artista or not self.titulo:
            self.lbl_status.configure(text="⚠ No se pudo extraer artista/título.", text_color="#FF453A"); return
        self.lbl_status.configure(text="🔎 Consultando LRCLIB con variantes de título...", text_color="#0A84FF")
        self.update_idletasks()
        lrc, es_sinc = buscar_lrc_online(self.artista, self.titulo)
        if lrc:
            self.txt_lrc.delete("1.0", "end"); self.txt_lrc.insert("end", lrc)
            st_text = "✓ ¡Letra sincronizada hallada!" if es_sinc else "✓ ¡Letra de texto plano hallada!"
            self.lbl_status.configure(text=st_text, text_color="#30D158")
        else:
            self.lbl_status.configure(text="⚠ No se encontró letra en LRCLIB.", text_color="#FF453A")

    def guardar_cambios(self):
        texto = self.txt_lrc.get("1.0", "end").strip()
        if texto and texto != "[Sin letras incrustadas actualmente]" and incrustar_lrc(self.ruta_audio, texto):
            self.lbl_status.configure(text="✓ Letras guardadas con éxito.", text_color="#30D158")
        else:
            self.lbl_status.configure(text="✗ Error incrustando letras.", text_color="#FF453A")

    def borrar_letras(self):
        if incrustar_lrc(self.ruta_audio, ""):
            self.txt_lrc.delete("1.0", "end"); self.txt_lrc.insert("end", "[Sin letras incrustadas actualmente]")
            self.lbl_status.configure(text="✓ Letra eliminada de la etiqueta.", text_color="#30D158")
