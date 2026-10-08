"""
Modal Emergente para Configuración / Descarga de qaac64.exe (Apple CoreAudio).
GestorBibliotecaMusical v4.0.
"""

import webbrowser
import customtkinter as ctk
from configuracionEstetica import (
    COLOR_FONDO_OSCURO,
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    FUENTE_TITULO,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA,
    cargar_configuracion,
    guardar_configuracion
)
from motores.motorQaac import verificar_qaac_instalado

class ModalConfiguracionQaac(ctk.CTkToplevel):
    def __init__(self, parent, callback_completado=None):
        super().__init__(parent)
        self.callback_completado = callback_completado
        self.title("Configuración del Codificador qaac (Apple CoreAudio)")
        self.geometry("540x380")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.transient(parent)
        self.grab_set()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_tit = ctk.CTkLabel(self, text="🎵 Codificador qaac64.exe Necesario", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(20, 5))
        
        desc = ("Para convertir archivos FLAC a AAC 320kbps de calidad audiófila, la aplicación requiere\n"
                "el ejecutable 'qaac64.exe' (Wrapper de Apple CoreAudio).\n"
                "Por favor selecciona el ejecutable en tu equipo o accede al sitio oficial de descargas.")
        lbl_desc = ctk.CTkLabel(self, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="center")
        lbl_desc.pack(padx=20, pady=(0, 15))
        
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=10)
        
        config = cargar_configuracion()
        self.entry_ruta = ctk.CTkEntry(card, placeholder_text="Seleccionar ubicación de qaac64.exe...", font=FUENTE_NORMAL, height=40)
        self.entry_ruta.pack(fill="x", padx=15, pady=(15, 10))
        if config.get("ruta_qaac"): self.entry_ruta.insert(0, config["ruta_qaac"])
            
        pnl_btn = ctk.CTkFrame(card, fg_color="transparent")
        pnl_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        btn_buscar = ctk.CTkButton(pnl_btn, text="📂 Seleccionar qaac64.exe", font=FUENTE_NORMAL, command=self.examinar_qaac)
        btn_buscar.pack(side="left", padx=(0, 10))
        
        btn_web = ctk.CTkButton(pnl_btn, text="🌐 Enlace Oficial de Descarga", font=FUENTE_NORMAL, fg_color="#3A3A3C", hover_color="#4A4A4C", command=self.abrir_web)
        btn_web.pack(side="right")
        
        btn_guardar = ctk.CTkButton(
            self, text="✓ Guardar y Continuar", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_AZUL, hover_color="#0066CC", height=45, corner_radius=10,
            command=self.guardar
        )
        btn_guardar.pack(fill="x", padx=20, pady=15)

    def examinar_qaac(self):
        ruta = ctk.filedialog.askopenfilename(title="Seleccionar ejecutable qaac64.exe", filetypes=[("Ejecutables qaac", "qaac64.exe qaac.exe"), ("Todos", "*.exe")])
        if ruta:
            self.entry_ruta.delete(0, "end"); self.entry_ruta.insert(0, ruta)

    def abrir_web(self):
        webbrowser.open("https://github.com/nu774/qaac/releases")

    def guardar(self):
        ruta = self.entry_ruta.get().strip()
        if verificar_qaac_instalado(ruta):
            guardar_configuracion("ruta_qaac", ruta); self.destroy()
            if self.callback_completado: self.callback_completado(ruta)
        else:
            lbl_err = ctk.CTkLabel(self, text="⚠ El archivo seleccionado no parece ser un ejecutable válido de qaac.", text_color="#FF453A", font=FUENTE_PEQUENA)
            lbl_err.pack(pady=5)
