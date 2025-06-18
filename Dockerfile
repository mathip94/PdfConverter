FROM python:3.9-slim

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    tesseract-ocr-spa \
    tesseract-ocr-eng \
    poppler-utils \
    libgl1-mesa-glx \
    libglib2.0-0 \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar requirements y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código de la aplicación
COPY . .

# Crear directorios necesarios
RUN mkdir -p uploads temp templates static

# Exponer puerto
EXPOSE 5000

# Configurar variables de entorno
ENV FLASK_APP=app.py
ENV FLASK_ENV=production
ENV PYTHONPATH=/app

# Comando para ejecutar la aplicación
CMD ["python", "app.py"] 