"""
Componente UI de Pestaña: Incrustación y Corrección de Letras LRC con Alcance Flexible.
GestorBibliotecaMusical v4.0.
"""

import os
import threading
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_NARANJA,
    COLOR_ACENTO_AZUL,
    COLOR_ACENTO_ROJO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA,
    obtener_ruta_musica_activa
)
from motores.motorLetrasLrc import ejecutar_letras_incremental
from baseDatosEscaneo import obtener_estadisticas_cache
from ui.ModalCorrectorLetraLrc import ModalCorrectorLetraLrc

class PestanaLetrasLrc(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.cancel_event = threading.Event()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=15)
        
        lbl_tit = ctk.CTkLabel(card, text="🎤 Incrustación y Auditoría de Letras Sincronizadas LRC", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))
        
        desc = ("Incrusta letras LRC sincronizadas u opcionalmente letras de texto plano en canciones no instrumentales.\n"
                "Soporta búsquedas por variantes de título limpiando sufijos (ej: 'My All (album version)' -> 'My All').\n"
                "Permite auditar una CANCIÓN PUNTUAL, filtrar por LISTA M3U o escanear la biblioteca completa.")
        lbl_desc = ctk.CTkLabel(card, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))
        
        pnl_mode = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        pnl_mode.pack(fill="x", padx=20, pady=5)
        
        lbl_m = ctk.CTkLabel(pnl_mode, text="🎯 Alcance de la Revisión:", font=FUENTE_NORMAL, text_color="#FFFFFF")
        lbl_m.pack(side="left", padx=15, pady=10)
        
        self.var_modo = ctk.StringVar(value="completo")
        r1 = ctk.CTkRadioButton(pnl_mode, text="Biblioteca Completa", variable=self.var_modo, value="completo")
        r1.pack(side="left", padx=10)
        r2 = ctk.CTkRadioButton(pnl_mode, text="Por Lista M3U", variable=self.var_modo, value="lista_m3u")
        r2.pack(side="left", padx=10)
        r3 = ctk.CTkRadioButton(pnl_mode, text="Estricto (Re-Verificar)", variable=self.var_modo, value="estricto")
        r3.pack(side="left", padx=10)
        
        btn_puntual = ctk.CTkButton(
            pnl_mode, text="🔍 Corregir Canción Puntual", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_AZUL,
            hover_color="#0066CC", height=32, command=self.abrir_corrector_puntual
        )
        btn_puntual.pack(side="right", padx=15)
        
        pnl_btn = ctk.CTkFrame(self, fg_color="transparent")
        pnl_btn.pack(fill="x", padx=20, pady=5)
        
        self.btn_iniciar = ctk.CTkButton(
            pnl_btn, text="⚡ Iniciar Auditoría de Letras", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_NARANJA, hover_color="#E68A00", height=45, corner_radius=10,
            command=self.iniciar_proceso
        )
        self.btn_iniciar.pack(side="left", fill="x", expand=True, padx=(0, 10))
        
        self.btn_detener = ctk.CTkButton(
            pnl_btn, text="⏹ Detener", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_ROJO, hover_color="#D32F2F", height=45, width=110, corner_radius=10,
            state="disabled", command=self.detener_proceso
        )
        self.btn_detener.pack(side="right")
        
        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", progress_color=COLOR_ACENTO_NARANJA)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=10, fill="x")
        
        self.txt_log = ctk.CTkTextbox(self, font=FUENTE_PEQUENA, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        self.txt_log.insert("end", "Sistema de letras LRC e inspección listo.\n")

    def abrir_corrector_puntual(self):
        dir_musica = obtener_ruta_musica_activa() or os.path.expanduser("~")
        archivo = ctk.filedialog.askopenfilename(title="Seleccionar Canción para Corregir Letra LRC", initialdir=dir_musica, filetypes=[("Archivos de Audio", "*.m4a *.mp3")])
        if archivo: ModalCorrectorLetraLrc(self, archivo)

    def log(self, mensaje):
        self.txt_log.insert("end", mensaje + "\n"); self.txt_log.see("end")

    def callback_progreso(self, actual, total, mensaje):
        self.progress_bar.set(actual / max(total, 1)); self.log(f"[{actual}/{total}] {mensaje}")

    def detener_proceso(self):
        self.cancel_event.set(); self.log("\n⚠ Solicitando detención del proceso...")

    def iniciar_proceso(self):
        modo = self.var_modo.get()
        ruta_m3u = None
        if modo == "lista_m3u":
            dir_musica = obtener_ruta_musica_activa() or os.path.expanduser("~")
            ruta_m3u = ctk.filedialog.askopenfilename(title="Seleccionar Lista M3U", initialdir=dir_musica, filetypes=[("Listas M3U", "*.m3u")])
            if not ruta_m3u:
                self.log("⚠ Proceso cancelado: No se seleccionó ninguna lista M3U.")
                return
                
        self.cancel_event.clear()
        self.btn_iniciar.configure(state="disabled"); self.btn_detener.configure(state="normal")
        self.progress_bar.set(0); self.log(f"\n🚀 Iniciando auditoría de letras LRC [Modo: {modo.upper()}]...")
        threading.Thread(target=self._tarea_ejecutar, args=(modo, ruta_m3u), daemon=True).start()

    def _tarea_ejecutar(self, modo, ruta_m3u):
        exito, msg, cant = ejecutar_letras_incremental(self.callback_progreso, self.cancel_event, modo=modo, ruta_m3u=ruta_m3u)
        self.log(f"\n{msg}\n"); self.progress_bar.set(1.0)
        self.btn_iniciar.configure(state="normal"); self.btn_detener.configure(state="disabled")
