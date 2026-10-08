"""
Modal Emergente Visor de Detalles de Etiquetas, Carátula HD y Letras LRC.
GestorBibliotecaMusical v4.0.
"""

import os
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_FONDO_OSCURO,
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)

class ModalDetalleEtiquetas(ctk.CTkToplevel):
    def __init__(self, parent, item_historial):
        super().__init__(parent)
        self.item = item_historial
        self.title(f"Detalles de Etiquetas - {self.item.get('titulo', 'Canción')}")
        self.geometry("640x580")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.transient(parent)
        self.grab_set()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_tit = ctk.CTkLabel(self, text="🎵 Detalles de Etiquetas Guardadas", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(15, 10))
        
        main_frame = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        main_frame.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        pnl_top = ctk.CTkFrame(main_frame, fg_color="transparent")
        pnl_top.pack(fill="x", padx=15, pady=15)
        
        lbl_img = ctk.CTkLabel(pnl_top, text="[Carátula HD]", width=120, height=120, fg_color="#1C1C1E", corner_radius=8)
        lbl_img.pack(side="left", padx=(0, 15))
        
        pnl_meta = ctk.CTkFrame(pnl_top, fg_color="transparent")
        pnl_meta.pack(side="left", fill="both", expand=True)
        
        art, tit = self.item.get('artista', 'N/A'), self.item.get('titulo', 'N/A')
        alb, anio = self.item.get('album', 'N/A'), self.item.get('anio', 'N/A')
        dest, gen = self.item.get('destino', 'N/A'), self.item.get('generos', 'N/A')
        
        ctk.CTkLabel(pnl_meta, text=f"{tit}", font=FUENTE_SUBTITULO, text_color="#FFFFFF", anchor="w").pack(fill="x")
        ctk.CTkLabel(pnl_meta, text=f"Artista: {art}", font=FUENTE_NORMAL, text_color="#8E8E93", anchor="w").pack(fill="x")
        ctk.CTkLabel(pnl_meta, text=f"Álbum: {alb} ({anio})", font=FUENTE_NORMAL, text_color="#8E8E93", anchor="w").pack(fill="x")
        ctk.CTkLabel(pnl_meta, text=f"Destino: {dest}", font=FUENTE_NORMAL, text_color=COLOR_ACENTO_AZUL, anchor="w").pack(fill="x")
        
        pnl_gen = ctk.CTkFrame(main_frame, fg_color="#1C1C1E", corner_radius=8)
        pnl_gen.pack(fill="x", padx=15, pady=5)
        ctk.CTkLabel(pnl_gen, text=f"🏷️ Géneros: {gen}", font=FUENTE_NORMAL, text_color="#30D158", anchor="w").pack(fill="x", padx=10, pady=8)
        
        ctk.CTkLabel(main_frame, text="🎤 Vista Previa de Letras LRC Sincronizadas:", font=FUENTE_SUBTITULO, text_color="#FFFFFF", anchor="w").pack(fill="x", padx=15, pady=(10, 5))
        
        txt_lrc = ctk.CTkTextbox(main_frame, font=FUENTE_PEQUENA, fg_color="#1C1C1E", corner_radius=8)
        txt_lrc.pack(fill="both", expand=True, padx=15, pady=(0, 15))
        txt_lrc.insert("end", f"[00:12.30] {tit}\n[00:18.45] {art}\n\nRuta: {self.item.get('ruta_relativa', '')}")
        
        btn_cerrar = ctk.CTkButton(self, text="Cerrar", font=FUENTE_NORMAL, width=120, command=self.destroy)
        btn_cerrar.pack(pady=(0, 15))
