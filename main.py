"""
Punto de Entrada Principal de la Aplicación GestorBibliotecaMusical v4.0.
"""

import sys
import os

# Asegurar que el directorio del proyecto está en el sys.path
DIRECTORIO_ACTUAL = os.path.dirname(os.path.abspath(__file__))
if DIRECTORIO_ACTUAL not in sys.path:
    sys.path.insert(0, DIRECTORIO_ACTUAL)

from ui.VentanaPrincipal import VentanaPrincipal

def main():
    app = VentanaPrincipal()
    app.mainloop()

if __name__ == "__main__":
    main()
