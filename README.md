# PdfConverter - PDF to Text Converter with OCR

Una aplicación web moderna que permite extraer texto de PDFs escaneados e imágenes manteniendo el formato original, utilizando tecnologías de OCR (Optical Character Recognition).

## 🌟 Características

- **Soporte múltiples formatos**: PDF, JPG, PNG, GIF, BMP, TIFF
- **OCR**: Utiliza Tesseract con preprocesamiento de imágenes
- **Preservación de formato**: Mantiene espaciado, párrafos y estructura original
- **Interfaz moderna**: Drag & drop, barra de progreso, descarga automática
- **Procesamiento inteligente**: Detecta PDFs con texto vs. PDFs escaneados
- **Multiidioma**: Soporte para español e inglés

## 🚀 Instalación

> **⚠️ IMPORTANTE**: Esta instalación es solo para **desarrollo local**. 
> Cuando la aplicación esté en producción (servidor online), los usuarios finales solo necesitarán un navegador web.

> **🖥️ USUARIOS DE WINDOWS**: Ver guía detallada → [WINDOWS_SETUP.md](WINDOWS_SETUP.md)

### Para Desarrollo Local

#### Prerequisitos

1. **Python 3.8+** instalado en tu sistema  
2. **Tesseract OCR** instalado en tu máquina de desarrollo:

   **Windows:**
   ```bash
   # Descargar desde: https://github.com/UB-Mannheim/tesseract/wiki
   # O usar chocolatey:
   choco install tesseract
   ```

   **macOS:**
   ```bash
   brew install tesseract
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install tesseract-ocr tesseract-ocr-spa
   ```

3. **Poppler** (para conversión PDF a imagen):

   **Windows:**
   ```bash
   # Opción 1 (Recomendada): Descargar binarios pre-compilados
   # Ir a: https://github.com/oschwartz10612/poppler-windows/releases/
   # Descargar la última versión (Release-24.08.0-0.zip)
   # Extraer y agregar la carpeta bin/ al PATH del sistema
   
   # Opción 2: Usando conda
   conda install poppler
   
   # Opción 3: Chocolatey
   choco install poppler
   ```

   **macOS:**
   ```bash
   brew install poppler
   ```

   **Ubuntu/Debian:**
   ```bash
   sudo apt-get install poppler-utils
   ```

#### Pasos de Instalación Local

1. **Clonar/Descargar el proyecto**
   ```bash
   git clone https://github.com/mathip94/PdfConverter.git
   cd PdfConverter
   ```

2. **Crear entorno virtual (recomendado)**
   ```bash
   python -m venv venv
   # Windows:
   venv\Scripts\activate
   # macOS/Linux:
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```

5. **Abrir en navegador**
   ```
   http://localhost:5000
   ```

### Para Producción (Deployment)

#### Opción 1: Servidor VPS/Cloud con Docker

Crear `Dockerfile`:
```dockerfile
FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    poppler-utils \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 5000

CMD ["python", "app.py"]
```

#### Opción 2: Railway/Render (más fácil)

Simplemente conectar el repositorio Git y la plataforma instalará automáticamente las dependencias.

#### Opción 3: Azure/AWS/GCP

Usar servicios de OCR en la nube para evitar instalar Tesseract:
- **Azure Computer Vision API**
- **AWS Textract**  
- **Google Cloud Vision API**

## 📱 Uso

1. **Subir archivo**: Arrastra un PDF o imagen a la zona de carga o haz clic para seleccionar
2. **Procesar**: Haz clic en "Procesar Archivo" y espera el resultado
3. **Descargar**: Una vez extraído el texto, puedes descargarlo como archivo .txt

### Formatos Soportados

- **PDFs**: Tanto con texto extraíble como escaneados
- **Imágenes**: JPG, PNG, GIF, BMP, TIFF
- **Tamaño máximo**: 16MB por archivo

## 🔧 Configuración Avanzada

### Configurar idiomas adicionales en Tesseract

```bash
# Instalar paquetes de idioma adicionales
# Ubuntu/Debian:
sudo apt install tesseract-ocr-fra tesseract-ocr-deu tesseract-ocr-ita

# Verificar idiomas instalados:
tesseract --list-langs
```

### Modificar configuración OCR

En `app.py`, línea ~140, puedes modificar:
```python
custom_config = r'--oem 3 --psm 6 -l eng+spa+fra'  # Agregar más idiomas
```

## 🏗️ Estructura del Proyecto

```
PdfConverter/
├── app.py              # Aplicación Flask principal
├── requirements.txt    # Dependencias Python
├── README.md          # Este archivo
├── todo.md           # Plan de desarrollo
├── templates/
│   └── index.html    # Interfaz web
├── uploads/          # Archivos subidos (temporal)
├── temp/            # Archivos temporales
└── static/          # Archivos estáticos (CSS, JS, imágenes)
```

## 🐛 Solución de Problemas

### Error: "Tesseract not found"
- Verificar que Tesseract esté instalado y en el PATH
- Windows: Agregar `C:\Program Files\Tesseract-OCR` al PATH

### Error: "pdf2image requires poppler"
- **Windows**: Descargar desde https://github.com/oschwartz10612/poppler-windows/releases/
- Extraer el archivo ZIP y agregar la carpeta `bin/` al PATH del sistema
- Reiniciar el terminal después de agregar al PATH
- Verificar instalación: `pdftoppm -h` en terminal

### Error de memoria con archivos grandes
- Reducir el tamaño del archivo
- Ajustar la configuración DPI en `pdf2image.convert_from_path(pdf_path, dpi=200)`

### Calidad OCR baja
- Asegurar que la imagen tenga buena resolución
- La imagen debe tener buen contraste entre texto y fondo
- Evitar imágenes con mucho ruido o distorsión

