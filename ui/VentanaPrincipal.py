"""
Ventana Principal Shell (CustomTkinter UI con TkinterDnD) en Modo Oscuro 'Apple Grises Pro'.
GestorBibliotecaMusical v4.0.
"""

import os
import customtkinter as ctk
from tkinterdnd2 import TkinterDnD
from configuracionEstetica import (
    COLOR_FONDO_OSCURO,
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    COLOR_ACENTO_VERDE,
    COLOR_ACENTO_NARANJA,
    FUENTE_TITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA,
    TEMA_DEFECTO,
    COLOR_TEMA,
    cargar_configuracion,
    obtener_ruta_itunes_activa
)

from ui.PestanaExportarM3u import PestanaExportarM3u
from ui.PestanaGeneros import PestanaGeneros
from ui.PestanaLetrasLrc import PestanaLetrasLrc
from ui.PestanaAlbumOriginal import PestanaAlbumOriginal
from ui.PestanaAutoIngesta import PestanaAutoIngesta
from ui.PestanaHistorial import PestanaHistorial
from ui.ModalAcercaDe import ModalAcercaDe
from motores.motorChangelog import obtener_info_version

class CTkTkinterDnD(ctk.CTk, TkinterDnD.DnDWrapper):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.TkdndVersion = TkinterDnD._require(self)

class VentanaPrincipal(CTkTkinterDnD):
    def __init__(self):
        super().__init__()
        ctk.set_appearance_mode(TEMA_DEFECTO)
        ctk.set_default_color_theme(COLOR_TEMA)
        
        self.title("Gestor de Biblioteca Musical Pro")
        self.geometry("980x700")
        self.minsize(860, 600)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.crear_cabecera()
        self.crear_pestañas()
        self.crear_pie()
        
    def crear_cabecera(self):
        hdr = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, height=60, corner_radius=0)
        hdr.pack(fill="x", side="top")
        
        lbl_tit = ctk.CTkLabel(hdr, text="🎵 Gestor de Biblioteca Musical Pro", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(side="left", padx=20, pady=15)
        
        info_ver = obtener_info_version()
        btn_acerca = ctk.CTkButton(
            hdr, text=f"ℹ️ v{info_ver.get('version', '4.0.0')}", font=FUENTE_NORMAL, width=90, height=30,
            fg_color="#3A3A3C", hover_color="#4A4A4C", command=lambda: ModalAcercaDe(self)
        )
        btn_acerca.pack(side="right", padx=20, pady=15)

    def crear_pestañas(self):
        self.tabview = ctk.CTkTabview(
            self, fg_color=COLOR_FONDO_OSCURO, segmented_button_fg_color=COLOR_TARJETA_OSCURO,
            segmented_button_selected_color=COLOR_ACENTO_AZUL, segmented_button_selected_hover_color="#0066CC",
            corner_radius=10
        )
        self.tabview.pack(fill="both", expand=True, padx=15, pady=10)
        
        t1 = self.tabview.add(" 📋 Listas M3U ")
        t2 = self.tabview.add(" 🏷️ Géneros ")
        t3 = self.tabview.add(" 🎤 Letras LRC ")
        t4 = self.tabview.add(" 🖼️ Álbum Original ")
        t5 = self.tabview.add(" 📥 Auto-Ingesta Dual ")
        t6 = self.tabview.add(" 📜 Historial ")
        
        PestanaExportarM3u(t1).pack(fill="both", expand=True)
        PestanaGeneros(t2).pack(fill="both", expand=True)
        PestanaLetrasLrc(t3).pack(fill="both", expand=True)
        PestanaAlbumOriginal(t4).pack(fill="both", expand=True)
        PestanaAutoIngesta(t5).pack(fill="both", expand=True)
        PestanaHistorial(t6).pack(fill="both", expand=True)

    def crear_pie(self):
        ftr = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, height=36, corner_radius=0)
        ftr.pack(fill="x", side="bottom")
        
        config = cargar_configuracion()
        r_it = obtener_ruta_itunes_activa()
        st_it = "🟢 iTunes: Activo" if r_it else "⚠ iTunes: No detectado"
        col_it = COLOR_ACENTO_VERDE if r_it else COLOR_ACENTO_NARANJA
        
        lbl_it = ctk.CTkLabel(ftr, text=f"  {st_it}  ", font=FUENTE_PEQUENA, text_color="#FFFFFF", fg_color=col_it, corner_radius=10)
        lbl_it.pack(side="left", padx=8, pady=6)

        r_pc = config.get("ruta_biblioteca_pc")
        txt_pc = f"🖥️ PC: {os.path.basename(r_pc)}" if r_pc else "🖥️ PC: No configurada"
        lbl_pc = ctk.CTkLabel(ftr, text=f"  {txt_pc}  ", font=FUENTE_PEQUENA, text_color="#FFFFFF", fg_color="#3A3A3C", corner_radius=10)
        lbl_pc.pack(side="left", padx=5, pady=6)

        lbl_dnd = ctk.CTkLabel(ftr, text="  📥 Drag & Drop Activo  ", font=FUENTE_PEQUENA, text_color="#FFFFFF", fg_color=COLOR_ACENTO_AZUL, corner_radius=10)
        lbl_dnd.pack(side="right", padx=10, pady=6)
