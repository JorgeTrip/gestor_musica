"""
Modal Emergente para la Selección de Destino del Lote (Celular vs. Biblioteca PC).
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
    FUENTE_NORMAL
)

class ModalSelectorDestino(ctk.CTkToplevel):
    def __init__(self, parent, callback_resultado):
        super().__init__(parent)
        self.callback_resultado = callback_resultado
        self.title("Seleccionar Destino de Ingesta")
        self.geometry("520x360")
        self.resizable(False, False)
        self.configure(fg_color=COLOR_FONDO_OSCURO)
        
        self.transient(parent)
        self.grab_set()
        self.crear_interfaz()
        
    def crear_interfaz(self):
        lbl_tit = ctk.CTkLabel(self, text="🎯 Seleccionar Destino del Lote", font=FUENTE_TITULO, text_color="#FFFFFF")
        lbl_tit.pack(pady=(20, 5))
        
        lbl_desc = ctk.CTkLabel(self, text="¿A dónde deseas enviar el lote de música ingresado?", font=FUENTE_NORMAL, text_color="#8E8E93")
        lbl_desc.pack(pady=(0, 20))
        
        card_cel = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card_cel.pack(fill="x", padx=25, pady=8)
        
        btn_cel = ctk.CTkButton(
            card_cel, text="📱 Destino Celular (iTunes / Poweramp)", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_AZUL, hover_color="#0066CC", height=45, corner_radius=8,
            command=self.elegir_celular
        )
        btn_cel.pack(fill="x", padx=15, pady=(12, 5))
        
        lbl_cel_info = ctk.CTkLabel(card_cel, text="Aplica Trazabilidad Original, envía a iTunes e inicia iTunes minimizado.", font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_cel_info.pack(anchor="w", padx=15, pady=(0, 12))
        
        card_pc = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card_pc.pack(fill="x", padx=25, pady=8)
        
        btn_pc = ctk.CTkButton(
            card_pc, text="🖥️ Destino Biblioteca PC (Alta Fidelidad)", font=FUENTE_SUBTITULO,
            fg_color=COLOR_ACENTO_VERDE, hover_color="#28B84D", height=45, corner_radius=8,
            command=self.elegir_pc
        )
        btn_pc.pack(fill="x", padx=15, pady=(12, 5))
        
        lbl_pc_info = ctk.CTkLabel(card_pc, text="Estructura [Artista]/[Año] - [Álbum]/[01. Tema.m4a] y comprime FLAC en ZIP9.", font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_pc_info.pack(anchor="w", padx=15, pady=(0, 12))

    def elegir_celular(self):
        self.destroy()
        if self.callback_resultado: self.callback_resultado("celular")

    def elegir_pc(self):
        self.destroy()
        if self.callback_resultado: self.callback_resultado("pc")
