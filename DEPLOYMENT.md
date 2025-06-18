# 🚀 Guía de Deployment - PDF to Plain Text

## 🎯 ¿Por qué Deployment?

**Para Usuarios Finales**: Una vez deployado, los usuarios solo necesitan un navegador web. **NO necesitan instalar nada**.

**Tesseract y dependencias se instalan automáticamente en el servidor**, no en las máquinas de los usuarios.

## ⚡ Deployment Rápido (Recomendado)

### 1. Railway (Más Fácil) 🌟

```bash
# 1. Crear cuenta en https://railway.app
# 2. Conectar repositorio GitHub
# 3. ¡Listo! Se deploya automáticamente
```

**Ventajas**: Gratis, automático, URL pública inmediata

### 2. Render (También Fácil)

```bash
# 1. Crear cuenta en https://render.com
# 2. Conectar repositorio GitHub  
# 3. Seleccionar "Web Service"
# 4. ¡Automático!
```

### 3. Docker (Para Cualquier Servidor)

```bash
# Construir imagen
docker build -t pdf-to-text .

# Ejecutar
docker run -p 80:5000 pdf-to-text

# O usar docker-compose
docker-compose up
```

## 🌐 Deployment Avanzado

### Heroku

```bash
# Instalar Heroku CLI y login
heroku create mi-pdf-to-text-app

# Configurar buildpacks
heroku buildpacks:clear
heroku buildpacks:add https://github.com/heroku/heroku-buildpack-apt
heroku buildpacks:add heroku/python

# Crear Aptfile
echo "tesseract-ocr" > Aptfile
echo "tesseract-ocr-spa" >> Aptfile  
echo "poppler-utils" >> Aptfile

# Deploy
git push heroku main
```

### AWS/Azure/GCP

Usar los archivos Docker incluidos o servicios de OCR en la nube:

**AWS**: ECR + ECS / Lambda con Textract
**Azure**: Container Instances + Computer Vision API  
**GCP**: Cloud Run + Vision API

## 🔧 Variables de Entorno

Para producción, configurar:

```bash
FLASK_ENV=production
FLASK_DEBUG=0
PORT=5000  # O el puerto que asigne la plataforma
```

## 📝 URLs de Ejemplo

Después del deployment tendrás una URL como:

- Railway: `https://tu-app.railway.app`
- Render: `https://tu-app.onrender.com`  
- Heroku: `https://tu-app.herokuapp.com`

## ✅ Verificar Deployment

1. Abrir la URL en navegador
2. Subir una imagen de prueba con texto
3. Verificar que extrae el texto correctamente
4. ¡Compartir la URL con usuarios!

## 🆘 Troubleshooting

### Error: "Tesseract not found"
- Verificar que el Dockerfile instale tesseract-ocr
- Para Heroku: verificar Aptfile

### Error: "poppler not found"  
- **Windows**: Descargar desde https://github.com/oschwartz10612/poppler-windows/releases/
- **Linux**: `sudo apt install poppler-utils`
- **macOS**: `brew install poppler`
- Verificar instalación: `pdftoppm -h`

### Error de memoria/timeout
- Ajustar DPI en pdf2image: `dpi=200` en lugar de 300
- Configurar límites de memoria en la plataforma

## 💡 Tips

- **Railway/Render**: Más fácil para empezar
- **Docker**: Más control, funciona en cualquier lugar
- **Heroku**: Más configuración pero muy estable
- **AWS/Azure/GCP**: Para apps empresariales

¡Con cualquiera de estas opciones, tus usuarios solo necesitarán un navegador web! 🎉 