# API de Predicción de Precios de Casas

API simple de FastAPI para predecir precios de casas en Colombia usando un modelo de Árbol de Regresión.

## 🚀 Despliegue en Render

### Pasos:
1. Subir este repositorio a GitHub
2. En Render.com:
   - New → Web Service
   - Conectar repositorio de GitHub
   - **Environment**: Python 3
   - **Build Command**: (dejar vacío)
   - **Start Command**: `uvicorn main:app --host 0.0.0.0 --port $PORT`
3. Deploy

### Archivos importantes:
- `main.py` - Aplicación FastAPI completa
- `requirements.txt` - Dependencias con versiones estables
- `Procfile` - Comando de inicio para Render
- `runtime.txt` - Python 3.11.7
- `artifacts/model.pkl` - Modelo entrenado
- `scripts/cleaning.py` - Funciones de limpieza de datos

## 📊 Endpoints

- `GET /` - Información de la API
- `GET /health` - Estado del servicio
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
# Instalar dependencias
pip install -r requirements.txt

# Ejecutar API
python main.py

# O con uvicorn
uvicorn main:app --reload --port 8000
```

## ✅ Características

- ✅ Versiones estables de pandas/numpy (sin compilación Cython)
- ✅ Python 3.11 (compatible con wheels precompilados)
- ✅ Estructura simple y minimalista
- ✅ Modelo ya entrenado y listo
- ✅ API probada y funcionando