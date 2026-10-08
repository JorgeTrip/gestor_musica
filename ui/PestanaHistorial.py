"""
Componente UI de Pestaña: Historial de Novedades e Ingestas Agrupadas por Fecha.
GestorBibliotecaMusical v4.0.
"""

import customtkinter as ctk
from configuracionEstetica import (
    COLOR_TARJETA_OSCURO,
    COLOR_ACENTO_AZUL,
    FUENTE_SUBTITULO,
    FUENTE_NORMAL,
    FUENTE_PEQUENA
)
from baseDatosEscaneo import obtener_historial_agrupado
from ui.ModalDetalleEtiquetas import ModalDetalleEtiquetas

class PestanaHistorial(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.crear_interfaz()
        
    def crear_interfaz(self):
        card = ctk.CTkFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=12)
        card.pack(fill="x", padx=20, pady=15)
        
        lbl_tit = ctk.CTkLabel(card, text="📜 Historial y Resumen de Novedades Ingresadas", font=FUENTE_SUBTITULO, text_color="#FFFFFF")
        lbl_tit.pack(anchor="w", padx=20, pady=(15, 5))
        
        desc = ("Muestra las canciones recién agregadas a tu biblioteca (Celular vs. PC) agrupadas por fecha.\n"
                "Haz clic en cualquier canción de la lista para abrir el Visor Interactivo de Etiquetas y examinar la portada, letras LRC y géneros.")
        lbl_desc = ctk.CTkLabel(card, text=desc, font=FUENTE_NORMAL, text_color="#8E8E93", justify="left")
        lbl_desc.pack(anchor="w", padx=20, pady=(0, 15))
        
        btn_refrescar = ctk.CTkButton(self, text="🔄 Actualizar Historial", font=FUENTE_NORMAL, width=160, command=self.cargar_historial)
        btn_refrescar.pack(anchor="w", padx=20, pady=(0, 10))
        
        self.scroll_hist = ctk.CTkScrollableFrame(self, fg_color=COLOR_TARJETA_OSCURO, corner_radius=10)
        self.scroll_hist.pack(fill="both", expand=True, padx=20, pady=(0, 15))
        
        self.cargar_historial()
        
    def cargar_historial(self):
        for widget in self.scroll_hist.winfo_children():
            widget.destroy()
            
        historial_data = obtener_historial_agrupado()
        if not historial_data:
            lbl_empty = ctk.CTkLabel(self.scroll_hist, text="No hay registros de ingesta recientes en el historial.", font=FUENTE_NORMAL, text_color="#8E8E93")
            lbl_empty.pack(pady=30)
            return
            
        for fecha_str, items in historial_data.items():
            hdr_f = ctk.CTkFrame(self.scroll_hist, fg_color="#1C1C1E", corner_radius=6)
            hdr_f.pack(fill="x", pady=(10, 5), padx=5)
            
            lbl_f = ctk.CTkLabel(hdr_f, text=f"📅 Fecha: {fecha_str} ({len(items)} canciones)", font=FUENTE_SUBTITULO, text_color=COLOR_ACENTO_AZUL)
            lbl_f.pack(anchor="w", padx=10, pady=5)
            
            for item in items:
                row_f = ctk.CTkFrame(self.scroll_hist, fg_color="#3A3A3C", corner_radius=6)
                row_f.pack(fill="x", pady=2, padx=5)
                
                txt_item = f"[{item['destino']}] {item['artista']} - {item['titulo']} ({item['album']})"
                lbl_item = ctk.CTkLabel(row_f, text=txt_item, font=FUENTE_NORMAL, text_color="#FFFFFF", anchor="w")
                lbl_item.pack(side="left", padx=10, pady=6, fill="x", expand=True)
                
                btn_ver = ctk.CTkButton(
                    row_f, text="🔍 Ver Etiquetas", font=FUENTE_PEQUENA, width=100, height=26,
                    fg_color=COLOR_ACENTO_AZUL, command=lambda it=item: ModalDetalleEtiquetas(self, it)
                )
                btn_ver.pack(side="right", padx=10)
