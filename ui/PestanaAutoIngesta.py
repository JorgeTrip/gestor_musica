"""
Componente UI de Pestaña: Auto-Ingesta con Drag-and-Drop, Destino por Lote y Pipeline Diferenciado.
GestorBibliotecaMusical v4.0.
"""

import os
import re
import threading
import customtkinter as ctk
from tkinterdnd2 import DND_FILES
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_VERDE,
    COLOR_ACENTO_AZUL,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA,
    cargar_configuracion,
    guardar_configuracion,
    obtener_ruta_itunes_activa
)
from motores.motorAutoIngesta import procesar_ingesta_lote
from motores.motorQaac import verificar_qaac_instalado
from ui.ModalSelectorDestino import ModalSelectorDestino
from ui.ModalConfiguracionQaac import ModalConfiguracionQaac
from ui.ModalConfiguracioniTunes import ModalConfiguracioniTunes
from ui.ModalResumenIngesta import ModalResumenIngesta

class PestanaAutoIngesta(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.crear_interfaz()
        
    def crear_interfaz(self):
        self.drop_card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=16, border_width=2, border_color="#3A3A3C")
        self.drop_card.pack(fill="x", padx=20, pady=15)
        
        lbl_icon = ctk.CTkLabel(self.drop_card, text="📥", font=("SF Pro Display", 36))
        lbl_icon.pack(pady=(15, 5))
        
        lbl_tit = ctk.CTkLabel(self.drop_card, text="Arrastra y Suelta tus Canciones o Carpetas Aquí", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(0, 5))
        
        desc = ("Al ingresar música nueva, la aplicación ejecutará el PIPELINE COMPLETO de controles\n"
                "y te preguntará el DESTINO DEL LOTE (📱 Celular/iTunes vs 🖥️ Biblioteca PC en Alta Fidelidad).")
        lbl_desc = ctk.CTkLabel(self.drop_card, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="center")
        lbl_desc.pack(padx=20, pady=(0, 15))
        
        pnl_btn = ctk.CTkFrame(self.drop_card, fg_color="transparent")
        pnl_btn.pack(pady=(0, 15))
        
        btn_arch = ctk.CTkButton(pnl_btn, text="🎵 Seleccionar Archivos", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_AZUL, command=self.seleccionar_archivos)
        btn_arch.pack(side="left", padx=8)
        
        btn_carp = ctk.CTkButton(pnl_btn, text="📂 Seleccionar Carpeta", font=FUENTE_NORMAL, fg_color=COLOR_ACENTO_VERDE, command=self.seleccionar_carpeta)
        btn_carp.pack(side="left", padx=8)

        btn_itunes = ctk.CTkButton(pnl_btn, text="🍎 Carpeta iTunes", font=FUENTE_NORMAL, fg_color="#3A3A3C", hover_color="#4A4A4C", command=self.abrir_config_itunes)
        btn_itunes.pack(side="left", padx=8)

        btn_pc = ctk.CTkButton(pnl_btn, text="🖥️ Biblioteca PC", font=FUENTE_NORMAL, fg_color="#3A3A3C", hover_color="#4A4A4C", command=self.abrir_config_pc)
        btn_pc.pack(side="left", padx=8)

        self.configurar_dnd()

        self.progress_bar = ctk.CTkProgressBar(self, mode="determinate", progress_color=COLOR_ACENTO_VERDE)
        self.progress_bar.set(0)
        self.progress_bar.pack(padx=20, pady=5, fill="x")
        
        self.txt_log = ctk.CTkTextbox(self, font=FUENTE_PEQUENA, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.txt_log.pack(fill="both", expand=True, padx=20, pady=(5, 15))
        self.log("Drag & Drop activo. Arrastra archivos o carpetas para procesar e ingresar.\n")

    def configurar_dnd(self):
        try:
            self.drop_card.drop_target_register(DND_FILES)
            self.drop_card.dnd_bind("<<Drop>>", self.on_drop_files)
        except Exception:
            try:
                self.drop_target_register(DND_FILES)
                self.dnd_bind("<<Drop>>", self.on_drop_files)
            except Exception:
                pass

    def on_drop_files(self, event):
        data = event.data
        rutas = [r1 or r2 for r1, r2 in re.findall(r'\{([^}]+)\}|(\S+)', data) if r1 or r2]
        if rutas: self.procesar_lote_ingresado(rutas)

    def abrir_config_itunes(self):
        ModalConfiguracioniTunes(self, lambda r: self.log(f"✓ Ruta iTunes configurada: {r}"))

    def abrir_config_pc(self):
        config = cargar_configuracion()
        r_act = config.get("ruta_biblioteca_pc") or ""
        r_sel = ctk.filedialog.askdirectory(title="Seleccionar Carpeta Raíz de la Biblioteca de Música PC", initialdir=r_act if os.path.exists(r_act) else None)
        if r_sel:
            guardar_configuracion("ruta_biblioteca_pc", r_sel)
            self.log(f"✓ Ruta Biblioteca PC configurada: {r_sel}")

    def seleccionar_archivos(self):
        archs = ctk.filedialog.askopenfilenames(title="Seleccionar Archivos de Música", filetypes=[("Audio", "*.m4a *.mp3 *.flac *.wav")])
        if archs: self.procesar_lote_ingresado(list(archs))

    def seleccionar_carpeta(self):
        carp = ctk.filedialog.askdirectory(title="Seleccionar Carpeta de Música")
        if carp: self.procesar_lote_ingresado([carp])

    def log(self, mensaje):
        self.after(0, lambda m=mensaje: (self.txt_log.insert("end", m + "\n"), self.txt_log.see("end")))

    def callback_progreso(self, actual, total, mensaje):
        self.after(0, lambda a=actual, t=total: self.progress_bar.set(a / max(t, 1)))

    def procesar_lote_ingresado(self, lista_rutas):
        tiene_flac = any(r.lower().endswith(('.flac', '.wav')) or (os.path.isdir(r) and any(f.lower().endswith(('.flac', '.wav')) for _, _, fs in os.walk(r) for f in fs)) for r in lista_rutas)
        if tiene_flac and not verificar_qaac_instalado():
            ModalConfiguracionQaac(self, lambda r: self.procesar_lote_ingresado(lista_rutas))
            return
            
        ModalSelectorDestino(self, lambda dest: self.iniciar_pipeline_con_destino(lista_rutas, dest))

    def iniciar_pipeline_con_destino(self, lista_rutas, destino_tipo):
        if destino_tipo == "pc":
            config = cargar_configuracion()
            if not config.get("ruta_biblioteca_pc") or not os.path.exists(config.get("ruta_biblioteca_pc", "")):
                ruta_pc = ctk.filedialog.askdirectory(title="Seleccionar Carpeta Raíz de la Biblioteca de Música PC")
                if not ruta_pc:
                    self.log("⚠ Proceso cancelado: Debe seleccionar una carpeta para la Biblioteca PC.")
                    return
                guardar_configuracion("ruta_biblioteca_pc", ruta_pc)

        self.progress_bar.set(0)
        self.log(f"\n🚀 Recibido lote ({len(lista_rutas)} elementos) -> Destino: {destino_tipo.upper()}...")
        threading.Thread(target=self._tarea_pipeline, args=(lista_rutas, destino_tipo), daemon=True).start()

    def _tarea_pipeline(self, lista_rutas, destino_tipo):
        try:
            exito, msg, cant = procesar_ingesta_lote(lista_rutas, destino_tipo, self.callback_progreso, self.log)
            self.log(f"\n{msg}\n")
            self.after(0, lambda e=exito: self.progress_bar.set(1.0 if e else 0.0))
            if exito and cant > 0:
                self.after(0, lambda c=cant, d=destino_tipo, m=msg: ModalResumenIngesta(self, c, d, m))
        except Exception as err:
            self.log(f"\n❌ Error durante la ingesta: {err}\n")
            self.after(0, lambda: self.progress_bar.set(0.0))
