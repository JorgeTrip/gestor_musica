"""
Componente UI de Pestaña: Exportar Listas M3U desde XML de iTunes.
GestorBibliotecaMusical v4.0.
"""

import threading
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)
from motores.motorExportarM3u import ejecutar_exportacion_m3u

class PestanaExportarM3u(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.crear_interfaz()
        
    def crear_interfaz(self):
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=15)
        
        lbl_tit = ctk.CTkLabel(card, text="📋 Exportación de Listas M3U desde iTunes XML", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))
        
        desc = ("Lee automáticamente la biblioteca 'iTunes Music Library.xml' y exporta todas las listas\n"
                "de reproducción personales a la raíz de tu biblioteca musical ('iTunes Media/Music') en formato M3U relativo.\n"
                "Resuelve automáticamente nombres con '#' (.\\#Música Clásica) para garantizar compatibilidad con iTunes y Poweramp.")
        lbl_desc = ctk.CTkLabel(card, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))
        
        self.btn_exportar = ctk.CTkButton(
            self, text="⚡ Exportar Listas M3U Ahora", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_AZUL, hover_color="#0066CC", height=45, corner_radius=10,
            command=self.iniciar_exportacion
        )
        self.btn_exportar.pack(padx=20, pady=10, fill="x")
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", progress_color=COLOR_ACENTO_AZUL)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=10, fill="x")
        
        self.txt_log = ctk.CTkTextbox(self, font=FUENTE_PEQUENA, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        self.txt_log.insert("end", "Listo para exportar listas M3U.\n")
        
    def log(self, mensaje):
        self.txt_log.insert("end", mensaje + "\n"); self.txt_log.see("end")

    def callback_progreso(self, actual, total, mensaje):
        self.progress_bar.set(actual / max(total, 1)); self.log(f"[{actual}/{total}] {mensaje}")

    def iniciar_exportacion(self):
        self.btn_exportar.configure(state="disabled"); self.progress_bar.set(0)
        self.log("\n🚀 Iniciando exportación de listas M3U...")
        threading.Thread(target=self._tarea_exportar, daemon=True).start()

    def _tarea_exportar(self):
        exito, msg, cant = ejecutar_exportacion_m3u(self.callback_progreso)
        self.log(f"\n{msg}\n"); self.progress_bar.set(1.0); self.btn_exportar.configure(state="normal")
