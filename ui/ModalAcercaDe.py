"""
Modal Emergente 'Acerca de y Historial de Cambios' (Changelog).
GestorBibliotecaMusical v4.0.
"""

import customtkinter as ctk
from configuracionEstetica import (
    COLOR_FONDO_OSCURO,
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    COLOR_ACENTO_VERDE,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)
from motores.motorChangelog import obtener_info_version, obtener_historial_commits

class ModalAcercaDe(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.info = obtener_info_version()
        self.title(f"Acerca de - {self.info.get('app_name', 'Gestor de Biblioteca Musical Pro')}")
        self.geometry("640x540")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.transient(parent)
        self.grab_set()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_icon = ctk.CTkLabel(self, text="🎵", font=("SF Pro Display", 40))
        lbl_icon.pack(pady=(15, 2))
        
        lbl_tit = ctk.CTkLabel(self, text=self.info.get("app_name", "Gestor de Biblioteca Musical Pro"), font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(0, 2))
        
        lbl_ver = ctk.CTkLabel(
            self,
            text=f"Versión {self.info.get('version', '4.0.0')} (Build {self.info.get('build_date', '2026-10-08')})",
            font=FUENTE_SUBTITULO, text_color=COLOR_ACENTO_AZUL
        )
        lbl_ver.pack(pady=(0, 10))
        
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        lbl_ch_tit = ctk.CTkLabel(card, text="📜 Historial de Cambios y Commits Integrados:", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_ch_tit.pack(anchor="w", padx=15, pady=(12, 5))
        
        scroll_c = ctk.CTkScrollableFrame(card, fg_color="#1C1C1E", corner_radius=8)
        scroll_c.pack(fill="both", expand=True, padx=15, pady=(0, 12))
        
        commits = obtener_historial_commits()
        for line in commits:
            row_f = ctk.CTkFrame(scroll_c, fg_color="#2C2C2E", corner_radius=6)
            row_f.pack(fill="x", pady=2, padx=2)
            
            color_txt = "#FFFFFF"
            if "feat:" in line or "🚀" in line: color_txt = "#30D158"
            elif "fix:" in line or "🔧" in line: color_txt = "#FF9F0A"
            elif "BREAKING:" in line: color_txt = "#FF453A"
            
            lbl_line = ctk.CTkLabel(row_f, text=line, font=FUENTE_NORMAL, text_color=color_txt, anchor="w", justify="left")
            lbl_line.pack(fill="x", padx=10, pady=6)
            
        btn_cerrar = ctk.CTkButton(self, text="Cerrar", font=FUENTE_NORMAL, width=120, command=self.destroy)
        btn_cerrar.pack(pady=(0, 15))
