# 🏠 API de Predicción de Precios de Casas

API simple y eficiente de FastAPI para predecir precios de casas en Colombia usando un modelo de Árbol de Regresión entrenado.

## 🚀 Despliegue en Render

### Pasos:
1. Subir este repositorio a GitHub
2. En Render.com:
   - New → Web Service
   - Conectar repositorio de GitHub
   - **Environment**: **Docker** ⚠️ (IMPORTANTE: Seleccionar Docker, NO Python 3)
   - Render detectará automáticamente el `Dockerfile`
   - Deploy

### Archivos del proyecto:
- `main.py` - Aplicación FastAPI completa
- `Dockerfile` - Imagen con Python 3.11 y Conda
- `requirements.txt` - Dependencias de FastAPI
- `render.yaml` - Configuración para Render
- `artifacts/model.pkl` - Modelo entrenado listo para usar

## 📊 Endpoints disponibles

- `GET /` - Información de la API
- `GET /health` - Estado del servicio y versión del modelo
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

### Respuesta:
```json
{
  "precio_estimado": 140394.57,
  "unidad": "COP",
  "model_version": "2025-09-25T03:18:56Z",
  "prediction_ms": 9.95
}
```

## 🔧 Desarrollo local

```bash
# Con Docker
docker build -t casas-api .
docker run -p 8000:8000 casas-api

# O directamente (si tienes las dependencias)
python main.py
```

## ✅ Características

- ✅ **Docker con Conda** - Entorno estable y reproducible
- ✅ **Modelo entrenado** - Listo para usar sin configuración adicional
- ✅ **API robusta** - Manejo de errores y funciones de limpieza integradas
- ✅ **Flexible** - Acepta texto ("tres") o números (3) en las entradas
- ✅ **Rápida** - Predicciones en menos de 10ms
- ✅ **Escalable** - Preparada para producción en Render

## 🎯 Casos de uso

- **Inmobiliarias**: Estimación rápida de precios
- **Aplicaciones web**: Integración fácil con frontend
- **Análisis de mercado**: Comparación de propiedades
- **Desarrollo**: Base para proyectos más complejos

## 📈 Métricas del modelo

- **R² Score**: 0.94 (94% de precisión)
- **MAE**: 20,711 COP (error promedio)
- **Tiempo de respuesta**: < 10ms
- **Entrenado con**: 982 muestras de datos reales

---

**¡Tu API está lista para predecir precios de casas en tiempo real!** 🎉