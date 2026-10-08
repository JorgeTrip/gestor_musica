"""
Modal de Resumen Visual Post-Ingesta ("Apple Grises Pro").
GestorBibliotecaMusical v4.0.
"""

import os
import subprocess
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_BORDE_OSCURO,
    COLOR_ACENTO_AZUL,
    COLOR_ACENTO_VERDE,
    COLOR_ACENTO_NARANJA,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA,
    cargar_configuracion
)

class ModalResumenIngesta(ctk.CTkToplevel):
    def __init__(self, parent, cant_items, destino_tipo, info_extra=""):
        super().__init__(parent)
        self.title("Resumen de Ingesta")
        self.geometry("520x360")
        self.resizable(False, False)
        self.configure(fg_color="#1C1C1E")
        self.transient(parent)
        self.grab_set()
        
        self.cant_items = cant_items
        self.destino_tipo = destino_tipo
        self.info_extra = info_extra
        
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_header = ctk.CTkLabel(self, text="🎉 ¡Ingesta Completada!", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_header.pack(pady=(20, 10))
        
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=14, border_width=1, border_color=COLOR_BORDE_OSCURO)
        card.pack(fill="both", expand=True, padx=25, pady=10)
        
        lbl_sub = ctk.CTkLabel(card, text=f"Se han procesado {self.cant_items} elemento(s) correctamente.", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_sub.pack(pady=(15, 10))
        
        pnl_pills = ctk.CTkFrame(card, fg_color="transparent")
        pnl_pills.pack(pady=10)
        
        txt_dest = "📱 Celular (iTunes)" if self.destino_tipo == "celular" else "🖥️ Biblioteca PC"
        col_dest = COLOR_ACENTO_AZUL if self.destino_tipo == "celular" else COLOR_ACENTO_VERDE
        
        lbl_dest = ctk.CTkLabel(pnl_pills, text=f"  {txt_dest}  ", font=FUENTE_NORMAL, text_color="#FFFFFF", fg_color=col_dest, corner_radius=12)
        lbl_dest.pack(side="left", padx=5)
        
        lbl_status = ctk.CTkLabel(pnl_pills, text="  🟢 100% Conforme  ", font=FUENTE_NORMAL, text_color="#FFFFFF", fg_color="#3A3A3C", corner_radius=12)
        lbl_status.pack(side="left", padx=5)
        
        if self.info_extra:
            lbl_extra = ctk.CTkLabel(card, text=self.info_extra, font=FUENTE_PEQUENA, text_color="#8E8E93")
            lbl_extra.pack(pady=(5, 10))
            
        pnl_actions = ctk.CTkFrame(self, fg_color="transparent")
        pnl_actions.pack(fill="x", padx=25, pady=(0, 20))
        
        btn_open = ctk.CTkButton(pnl_actions, text="📂 Abrir Carpeta Destino", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_VERDE, command=self.abrir_destino)
        btn_open.pack(side="left", padx=5, expand=True, fill="x")
        
        btn_ok = ctk.CTkButton(pnl_actions, text="✓ Aceptar", font=FUENTE_NORMAL, fg_color="#3A3A3C", hover_color="#4A4A4C", command=self.destroy)
        btn_ok.pack(side="right", padx=5, expand=True, fill="x")

    def abrir_destino(self):
        config = cargar_configuracion()
        ruta = config.get("ruta_biblioteca_pc") if self.destino_tipo == "pc" else config.get("ruta_itunes")
        if ruta and os.path.exists(ruta):
            subprocess.Popen(f'explorer "{ruta}"')
        self.destroy()
