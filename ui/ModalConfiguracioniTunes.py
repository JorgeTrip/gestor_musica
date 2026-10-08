"""
Modal Emergente para Configurar / Confirmar la Carpeta de iTunes.
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
    cargar_configuracion,
    guardar_configuracion,
    obtener_ruta_itunes_activa
)
from detectoriTunes import es_directorio_itunes_valido, obtener_xml_itunes

class ModalConfiguracioniTunes(ctk.CTkToplevel):
    def __init__(self, parent, callback_guardado=None):
        super().__init__(parent)
        self.callback_guardado = callback_guardado
        self.title("Configuración de Biblioteca iTunes")
        self.geometry("560x360")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.transient(parent)
        self.grab_set()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_tit = ctk.CTkLabel(self, text="🍎 Carpeta de Biblioteca iTunes", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(20, 5))
        
        desc = ("La aplicación utiliza la carpeta de iTunes para exportar listas M3U y enviar\n"
                "canciones mediante 'Automatically Add to iTunes'.\n"
                "Asegúrate de que contenga el archivo 'iTunes Music Library.xml' o la carpeta 'iTunes Media'.")
        lbl_desc = ctk.CTkLabel(self, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="center")
        lbl_desc.pack(padx=20, pady=(0, 15))
        
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=10)
        
        ruta_actual = obtener_ruta_itunes_activa() or ""
        self.entry_ruta = ctk.CTkEntry(card, placeholder_text="Seleccionar ubicación de la carpeta iTunes...", font=FUENTE_NORMAL, height=40)
        self.entry_ruta.pack(fill="x", padx=15, pady=(15, 10))
        self.entry_ruta.insert(0, ruta_actual)
        
        pnl_btn = ctk.CTkFrame(card, fg_color="transparent")
        pnl_btn.pack(fill="x", padx=15, pady=(0, 15))
        
        btn_buscar = ctk.CTkButton(pnl_btn, text="📂 Examinar Carpeta", font=FUENTE_NORMAL, command=self.examinar_itunes)
        btn_buscar.pack(side="left")
        
        self.lbl_estado = ctk.CTkLabel(pnl_btn, text="", font=FUENTE_NORMAL)
        self.lbl_estado.pack(side="right")
        self.validar_y_mostrar_estado(ruta_actual)
        
        btn_guardar = ctk.CTkButton(
            self, text="✓ Confirmar y Guardar", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_AZUL, hover_color="#0066CC", height=45, corner_radius=10,
            command=self.guardar
        )
        btn_guardar.pack(fill="x", padx=20, pady=15)

    def examinar_itunes(self):
        carpeta = ctk.filedialog.askdirectory(title="Seleccionar Carpeta de iTunes")
        if carpeta:
            self.entry_ruta.delete(0, "end")
            self.entry_ruta.insert(0, carpeta)
            self.validar_y_mostrar_estado(carpeta)

    def validar_y_mostrar_estado(self, ruta):
        if es_directorio_itunes_valido(ruta):
            self.lbl_estado.configure(text="✓ Directorio Válido", text_color="#30D158")
        else:
            self.lbl_estado.configure(text="⚠ No se detectó XML de iTunes", text_color="#FF9F0A")

    def guardar(self):
        ruta = self.entry_ruta.get().strip()
        if es_directorio_itunes_valido(ruta):
            guardar_configuracion("ruta_itunes", ruta)
            self.destroy()
            if self.callback_guardado:
                self.callback_guardado(ruta)
        else:
            self.lbl_estado.configure(text="✗ Carpeta no válida", text_color="#FF453A")
