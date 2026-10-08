# 🎵 Gestor de Biblioteca Musical Pro

[![GitHub Release](https://img.shields.io/github/v/release/JorgeTrip/gestor_musica?label=Última%20Versión&color=30D158)](https://github.com/JorgeTrip/gestor_musica/releases/latest)
[![Descargar Ejecutable .exe](https://img.shields.io/badge/Descargar%20Ejecutable-.exe-0A84FF?logo=windows)](https://github.com/JorgeTrip/gestor_musica/releases/latest)
[![Licencia](https://img.shields.io/badge/Licencia-MIT-informational)](LICENSE)

**Gestor de Biblioteca Musical Pro** es una suite de escritorio moderna para Windows diseñada para la gestión audiófila, organización, etiquetado y automatización de bibliotecas musicales (iTunes, Poweramp, foobar2000 y reproductores de alta fidelidad).

---

## 🚀 Descarga y Distribución

Para utilizar la versión ejecutable nativa sin necesidad de instalar Python:

👉 **[Descargar la última versión `GestorBibliotecaMusical.exe`](https://github.com/JorgeTrip/gestor_musica/releases/latest)**

---

## ✨ Características Principales

### 1. 📥 Auto-Ingesta Dual (Celular vs. PC)
- **Drag & Drop Integrado**: Arrastra archivos (`.flac`, `.m4a`, `.mp3`, `.wav`) o carpetas completas de descargas directamente sobre la interfaz.
- **📱 Destino Celular (iTunes / Poweramp)**:
  - Aplica trazabilidad del **álbum de estudio original** (año y portada de origen).
  - Envía las canciones a `iTunes Media/Automatically Add to iTunes`.
  - Si iTunes está cerrado, lo ejecuta minimizado para forzar la digestión automática en segundo plano.
- **🖥️ Destino Biblioteca PC (Alta Fidelidad)**:
  - Organiza carpetas con la estructura `[Artista]/[Año] - [Álbum]/[01. Pista.m4a]`.
  - Codifica archivos FLAC a AAC 320kbps de calidad audiófila usando el motor **Apple CoreAudio (`qaac64.exe`)**.
  - Empaqueta los archivos máster FLAC originales en un archivo `[Año] - [Álbum] (FLAC Master).zip` con la **máxima compresión posible (ZIP9)**.

### 2. 🏷️ Etiquetado Inteligente de Géneros Combinados
- Consulta en cadena **MusicBrainz + Last.fm + Deezer + iTunes API**.
- Asigna géneros combinados mediante el separador `/` (*Pop / Soft Rock / 80s*).
- **Escaneo Incremental SQLite**: Utiliza caché inteligente revisando únicamente archivos modificados recientemente.

### 3. 🎤 Auditoría y Corrector de Letras LRC
- Busca e incrusta letras LRC sincronizadas (o letras de texto plano en temas vocales) mediante **LRCLIB API**.
- **Variantes de Título**: Limpia automáticamente sufijos como `(album version)`, `[remastered 2016]`, `(deluxe)` para lograr máxima coincidencia.
- **Modal Inspector/Corrector Puntual**: Permite re-buscar, editar manualmente o eliminar letras de cualquier tema en vivo (ej: *Smooth Operator* de Sade).

### 4. 🖼️ Auditoría de Álbum Original y Carátulas HD
- Rastrea el álbum de estudio original para canciones pertenecientes a compilaciones o *Greatest Hits*.
- Asigna el año exacto de lanzamiento original en la etiqueta `©day` / `TDRC`.
- Incrusta portadas HD en alta resolución (1000x1000px+).

### 5. 📋 Exportación Relativa de Listas M3U desde iTunes XML
- Parsea `iTunes Music Library.xml` y exporta todas las listas personales a la raíz de la biblioteca musical en formato M3U relativo.
- Resuelve nombres con `#` (`.\#Música Clásica`) para evitar omisión de temas en iTunes y Poweramp.

### 6. 📜 Historial de Novedades y Visor de Etiquetas In-App
- Agrupa las canciones agregadas por fecha de ingesta.
- Incluye visor de metadatos con previsualización de carátula HD, letras LRC y detalles completos.
- **Modal Acerca de (`ℹ️`)**: Lee el archivo de cambios semántico y muestra los commits y actualizaciones de versión en tiempo real.

---

## 🛠️ Ejecución y Compilación Local

### Requisitos
- Windows 10 / 11.
- Python 3.11+ (opcional si usas el ejecutable `.exe`).

### Lanzamiento en 2 Clics
```cmd
GestorBibliotecaMusical.bat
```

### Compilación Local a Ejecutable
```cmd
python compilarEjecutable.py
```
El ejecutable se generará en `dist/GestorBibliotecaMusical/GestorBibliotecaMusical.exe`.

---

## 🔄 CI/CD & Versionado Semántico Automático

El proyecto cuenta con un workflow automatizado en **GitHub Actions** (`.github/workflows/cicd.yml`):
- **Incremento de Versión Semántica**:
  - `feat:` o `🚀` ➔ MINOR bump (ej. `v4.1.0`).
  - `fix:` o `🔧` ➔ PATCH bump (ej. `v4.0.1`).
  - `BREAKING:` ➔ MAJOR bump (ej. `v5.0.0`).
- **Publicación de Releases**: Compila el ejecutable en la nube de GitHub Actions en cada push a `main` y adjunta el ejecutable directamente a la sección de **Releases** para su distribución pública.

---

## 🛡️ Estándares de Código y Gobernanza

- **Límite de Líneas**: Ningún archivo supera las 200 líneas de código (Regla de Hierro).
- **Diseño**: Interfaz nativa CustomTkinter en Modo Oscuro estilo *Apple Grises Pro*.
- **Auditoría Centralizada**: Verificado mediante la suite de auditoría SAST y fronteras arquitectónicas limpias.
