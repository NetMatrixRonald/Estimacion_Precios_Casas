# Instrucciones de Despliegue en Render

## ✅ Problema solucionado

El error `metadata-generation-failed` que estabas experimentando se debía a que Render intentaba compilar pandas desde Cython en lugar de usar paquetes binarios precompilados.

## 🔧 Solución implementada

1. **Dockerfile renombrado**: `Dockerfile.conda` → `Dockerfile` para detección automática
2. **Base conda-forge**: Usa `mambaorg/micromamba` que instala binarios precompilados
3. **Python 3.11**: Versión estable con soporte completo de wheels
4. **Optimización**: `.dockerignore` para builds más rápidos

## 🚀 Pasos para desplegar

### 1. Subir a GitHub
```bash
git add .
git commit -m "Configuración lista para Render con Docker"
git push origin main
```

### 2. Configurar en Render
1. Ir a [render.com](https://render.com)
2. **New** → **Web Service**
3. Conectar tu repositorio de GitHub
4. **Settings**:
   - **Environment**: Docker
   - **Plan**: Free
   - **Health Check Path**: `/health`
5. **Deploy**

### 3. Verificar despliegue
- Render detectará automáticamente `render.yaml` y `Dockerfile`
- El build usará conda-forge (sin compilación C/Cython)
- La API estará disponible en la URL de Render

## 📊 Endpoints disponibles

- `GET /health` - Estado del servicio
- `POST /predict` - Predicción de precios

Ejemplo de predicción:
```json
{
  "superficie": "80m2",
  "habitaciones": "tres", 
  "antiguedad": "nueva",
  "ubicacion": "urbano"
}
```

## ⚡ Por qué funciona ahora

- **Conda-forge**: Instala binarios precompilados para Linux x86_64
- **Sin compilación**: Evita completamente C/Cython durante el build
- **Python 3.11**: Versión estable con wheels disponibles
- **Docker**: Entorno controlado y reproducible

El despliegue debería completarse en ~3-5 minutos sin errores de compilación.
