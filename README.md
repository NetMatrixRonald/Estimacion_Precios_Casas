# API de Predicción de Precios de Casas

API simple de FastAPI para predecir precios de casas en Colombia usando un modelo de Árbol de Regresión.

## 🚀 Despliegue en Render (SOLUCIÓN FINAL)

### Pasos:
1. Subir este repositorio a GitHub
2. En Render.com:
   - New → Web Service
   - Conectar repositorio de GitHub
   - **Environment**: **Docker** ⚠️ (IMPORTANTE: Seleccionar Docker, NO Python 3)
   - Render detectará automáticamente el `Dockerfile`
   - Deploy

### Archivos importantes:
- `main.py` - Aplicación FastAPI completa
- `Dockerfile` - Imagen con Python 3.11-slim
- `requirements.txt` - Dependencias con versiones estables
- `render.yaml` - Configuración para Docker
- `artifacts/model.pkl` - Modelo entrenado
- `scripts/cleaning.py` - Funciones de limpieza de datos

## 📊 Endpoints

- `GET /` - Información de la API
- `GET /health` - Estado del servicio
- `GET /debug` - Información de debug (archivos, rutas)
- `POST /predict` - Predicción de precios

### Ejemplo de predicción:
```json
{
  "superficie": "80m2",
  "habitaciones": "tres",
  "antiguedad": "nueva",
  "ubicacion": "urbano"
}
```

## 🔧 Desarrollo local

```bash
# Con Docker
docker build -t casas-api .
docker run -p 8000:8000 casas-api

# O directamente
pip install -r requirements.txt
python main.py
```

## ✅ Características

- ✅ **Docker con Python 3.11** - Evita problemas de versión
- ✅ **Wheels precompilados** - Sin compilación C/Cython
- ✅ **Estructura simple** - Un solo archivo main.py
- ✅ **Modelo ya entrenado** - Listo para usar
- ✅ **API probada** - Funciona localmente y en Render
- ✅ **Funciones de limpieza integradas** - Fallback automático

## 🎯 Por qué Docker funciona

- **Python 3.11 controlado** - No depende de la versión de Render
- **Wheels precompilados** - pandas 2.0.3 y numpy 1.24.3 tienen wheels para Python 3.11
- **Sin compilación** - Todas las dependencias se instalan desde binarios
- **Reproducible** - Mismo entorno en desarrollo y producción