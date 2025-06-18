# 🖥️ Guía de Instalación para Windows

Esta guía te ayudará a instalar todas las dependencias necesarias en Windows para que la aplicación PDF to Plain Text funcione correctamente.

## 📋 Requisitos Previos

- Windows 10 o superior
- Python 3.8+ instalado
- Conexión a internet

## 🚀 Instalación Paso a Paso

### 1. Instalar Python (si no lo tienes)

```bash
# Descargar desde: https://python.org/downloads/
# Asegúrate de marcar "Add Python to PATH" durante la instalación
```

### 2. Instalar Tesseract OCR

#### Opción A: Descarga directa (Recomendada)
1. Ir a: https://github.com/UB-Mannheim/tesseract/wiki
2. Descargar `tesseract-ocr-w64-setup-5.3.3.20231005.exe` (o la versión más reciente)
3. Ejecutar el instalador
4. **IMPORTANTE**: Durante la instalación, marcar "Add to PATH"
5. Si no marcaste "Add to PATH", agregar manualmente:
   - Abrir "Variables de entorno del sistema"
   - Agregar `C:\Program Files\Tesseract-OCR` al PATH

#### Opción B: Chocolatey
```powershell
# Instalar Chocolatey primero (si no lo tienes)
Set-ExecutionPolicy Bypass -Scope Process -Force; [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072; iex ((New-Object System.Net.WebClient).DownloadString('https://community.chocolatey.org/install.ps1'))

# Instalar Tesseract
choco install tesseract
```

### 3. Instalar Poppler

#### Opción A: Binarios pre-compilados (Recomendada)
1. Ir a: https://github.com/oschwartz10612/poppler-windows/releases/
2. Descargar el archivo ZIP más reciente (ej: `Release-24.08.0-0.zip`)
3. Extraer en una carpeta, por ejemplo: `C:\poppler`
4. Agregar al PATH del sistema:
   - Ir a "Variables de entorno del sistema"
   - En "Variables del sistema", seleccionar "Path" y hacer clic en "Editar"
   - Hacer clic en "Nuevo" y agregar: `C:\poppler\Library\bin`
   - Hacer clic en "Aceptar" para guardar

#### Opción B: Chocolatey
```powershell
choco install poppler
```

#### Opción C: Conda (si usas Anaconda/Miniconda)
```bash
conda install poppler
```

### 4. Verificar Instalaciones

Abrir una **nueva** ventana de PowerShell o CMD y ejecutar:

```bash
# Verificar Python
python --version

# Verificar Tesseract
tesseract --version

# Verificar Poppler
pdftoppm -h
```

Si todos los comandos funcionan, ¡estás listo!

### 5. Instalar la Aplicación

```bash
# Navegar a la carpeta del proyecto
cd C:\Users\TuUsuario\PdfToPlainText

# Crear entorno virtual (recomendado)
python -m venv venv

# Activar entorno virtual
venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar aplicación
python app.py
```

## 🆘 Solución de Problemas

### ❌ Error: "tesseract is not recognized as an internal or external command"

**Solución:**
1. Verificar que Tesseract esté instalado en `C:\Program Files\Tesseract-OCR`
2. Agregar al PATH:
   - Presionar `Win + R`, escribir `sysdm.cpl`
   - Ir a "Opciones avanzadas" → "Variables de entorno"
   - En "Variables del sistema", seleccionar "Path" → "Editar"
   - Agregar: `C:\Program Files\Tesseract-OCR`
   - Reiniciar terminal

### ❌ Error: "pdf2image.exceptions.PDFInfoNotInstalledError"

**Solución:**
1. Verificar descarga de Poppler desde GitHub releases
2. Extraer completamente el ZIP
3. Agregar la ruta `bin` al PATH del sistema
4. Reiniciar terminal y probar: `pdftoppm -h`

### ❌ Error: "Microsoft Visual C++ 14.0 is required"

**Solución:**
```bash
# Descargar e instalar Microsoft C++ Build Tools
# https://visualstudio.microsoft.com/visual-cpp-build-tools/
```

### ❌ La aplicación se ejecuta pero no extrae texto

**Verificar:**
1. El archivo subido no esté corrupto
2. Tesseract detecte el idioma: `tesseract --list-langs`
3. Probar con una imagen simple con texto claro

## 🎯 Comandos de Verificación Rápida

```powershell
# Verificar todas las dependencias de una vez
echo "=== Python ===" && python --version
echo "=== Tesseract ===" && tesseract --version
echo "=== Poppler ===" && pdftoppm -h | findstr "pdftoppm version"
echo "=== Pip packages ===" && pip list | findstr -i "flask pillow opencv"
```

## 📝 Notas Adicionales

- **Reinicia el terminal** después de instalar Tesseract y Poppler
- Si usas **PowerShell**, asegúrate de que la política de ejecución permita scripts
- Para **mejor rendimiento OCR**, usa imágenes con buena resolución y contraste
- El primer procesamiento puede ser más lento debido a la inicialización de Tesseract

## ✅ Todo Funcionando

Una vez completados todos los pasos:

```bash
python app.py
```

Abrir navegador en: `http://localhost:5000`

¡Tu aplicación PDF to Plain Text debería estar funcionando perfectamente! 🎉 