"""
Componente UI de Pestaña: Etiquetado Incremental de Géneros Combinados.
GestorBibliotecaMusical v4.0.
"""

import threading
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_VERDE,
    COLOR_ACENTO_ROJO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)
from motores.motorGeneros import ejecutar_etiquetado_generos_incremental
from baseDatosEscaneo import obtener_estadisticas_cache

class PestanaGeneros(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.cancel_event = threading.Event()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=15)
        
        lbl_tit = ctk.CTkLabel(card, text="🏷️ Etiquetado Incremental de Géneros Combinados", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))
        
        desc = ("Consulta MusicBrainz, Last.fm, Deezer e iTunes API en cadena.\n"
                "Asigna géneros combinados con el separador '/' (ej: 'Pop / Soft Rock / 80s').\n"
                "⚡ ESCANEO INTELIGENTE: Utiliza la base de datos de caché SQLite y revisa ÚNICAMENTE los archivos modificados.")
        lbl_desc = ctk.CTkLabel(card, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))
        
        pnl_btn = ctk.CTkFrame(self, fg_color="transparent")
        pnl_btn.pack(fill="x", padx=20, pady=5)
        
        self.btn_iniciar = ctk.CTkButton(
            pnl_btn, text="⚡ Iniciar Escaneo Inteligente de Géneros", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_VERDE, hover_color="#28B84D", height=45, corner_radius=10,
            command=self.iniciar_proceso
        )
        self.btn_iniciar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_detener = ctk.CTkButton(
            pnl_btn, text="⏹ Detener", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_ROJO, hover_color="#D32F2F", height=45, width=110, corner_radius=10,
            state="disabled", command=self.detener_proceso
        )
        self.btn_detener.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", progress_color=COLOR_ACENTO_VERDE)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=10, fill="x")
        
        self.txt_log = ctk.CTkTextbox(self, font=FUENTE_PEQUENA, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        self.actualizar_estado_inicial()
        
    def actualizar_estado_inicial(self):
        stats = obtener_estadisticas_cache()
        self.txt_log.delete("1.0", "end")
        self.txt_log.insert("end", f"Base de datos lista ({stats['generos']} canciones en caché de géneros).\n")

    def log(self, mensaje):
        self.txt_log.insert("end", mensaje + "\n"); self.txt_log.see("end")

    def callback_progreso(self, actual, total, mensaje):
        self.progress_bar.set(actual / max(total, 1)); self.log(f"[{actual}/{total}] {mensaje}")

    def detener_proceso(self):
        self.cancel_event.set(); self.log("\n⚠ Solicitando detención del proceso...")

    def iniciar_proceso(self):
        self.cancel_event.clear(); self.btn_iniciar.configure(state="disabled"); self.btn_detener.configure(state="normal")
        self.progress_bar.set(0); self.log("\n🚀 Iniciando escaneo inteligente de géneros...")
        threading.Thread(target=self._tarea_ejecutar, daemon=True).start()

    def _tarea_ejecutar(self):
        exito, msg, cant = ejecutar_etiquetado_generos_incremental(self.callback_progreso, self.cancel_event)
        self.log(f"\n{msg}\n"); self.progress_bar.set(1.0)
        self.btn_iniciar.configure(state="normal"); self.btn_detener.configure(state="disabled")
