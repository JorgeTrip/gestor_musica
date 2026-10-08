"""
Componente UI de Pestaña: Auditoría de Álbum Original, Año de Lanzamiento y Carátula HD.
GestorBibliotecaMusical v4.0.
"""

import threading
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    COLOR_ACENTO_ROJO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)
from motores.motorAlbumOriginal import ejecutar_album_original_incremental
from baseDatosEscaneo import obtener_estadisticas_cache

class PestanaAlbumOriginal(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.cancel_event = threading.Event()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=15)
        
        lbl_tit = ctk.CTkLabel(card, text="🖼️ Auditoría de Álbum Original, Año de Origen y Carátula HD", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))
        
        desc = ("Detecta si una canción pertenece a un 'Greatest Hits' o 'Compilaciones' y rastrea su álbum de estudio original.\n"
                "Asigna el año exacto del lanzamiento de origen (ej: 1996) en la etiqueta de fecha principal ('©day').\n"
                "Descarga e incrusta la carátula en alta definición (1000x1000px+) directamente dentro del archivo de audio.")
        lbl_desc = ctk.CTkLabel(card, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))
        
        pnl_btn = ctk.CTkFrame(self, fg_color="transparent")
        pnl_btn.pack(fill="x", padx=20, pady=5)
        
        self.btn_iniciar = ctk.CTkButton(
            pnl_btn, text="⚡ Iniciar Auditoría de Álbum Original y Carátulas HD", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_AZUL, hover_color="#0066CC", height=45, corner_radius=10,
            command=self.iniciar_proceso
        )
        self.btn_iniciar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_detener = ctk.CTkButton(
            pnl_btn, text="⏹ Detener", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_ROJO, hover_color="#D32F2F", height=45, width=110, corner_radius=10,
            state="disabled", command=self.detener_proceso
        )
        self.btn_detener.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", progress_color=COLOR_ACENTO_AZUL)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=10, fill="x")
        
        self.txt_log = ctk.CTkTextbox(self, font=FUENTE_PEQUENA, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        self.actualizar_estado_inicial()
        
    def actualizar_estado_inicial(self):
        stats = obtener_estadisticas_cache()
        self.txt_log.delete("1.0", "end")
        self.txt_log.insert("end", f"Base de datos lista ({stats['albumes']} canciones auditadas previamente).\n")

    def log(self, mensaje):
        self.txt_log.insert("end", mensaje + "\n"); self.txt_log.see("end")

    def callback_progreso(self, actual, total, mensaje):
        self.progress_bar.set(actual / max(total, 1)); self.log(f"[{actual}/{total}] {mensaje}")

    def detener_proceso(self):
        self.cancel_event.set(); self.log("\n⚠ Solicitando detención del proceso...")

    def iniciar_proceso(self):
        self.cancel_event.clear(); self.btn_iniciar.configure(state="disabled"); self.btn_detener.configure(state="normal")
        self.progress_bar.set(0); self.log("\n🚀 Iniciando auditoría de álbum original y carátulas HD...")
        threading.Thread(target=self._tarea_ejecutar, daemon=True).start()

    def _tarea_ejecutar(self):
        exito, msg, cant = ejecutar_album_original_incremental(self.callback_progreso, self.cancel_event)
        self.log(f"\n{msg}\n"); self.progress_bar.set(1.0)
        self.btn_iniciar.configure(state="normal"); self.btn_detener.configure(state="disabled")
