# Predicción de precios de casas (Colombia)

Este proyecto limpia datos de viviendas, entrena un Árbol de Regresión y expone un endpoint de predicción con FastAPI.

## 1) Instalaciónn

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
pip install -r requirements.txt
```

## 2) Exploración y limpieza

```bash
# Usando la ruta local del repo
python scripts/cleaning.py --input casas_sucias.csv --output data/casas_limpias.csv --report outputs/cleaning_report.json

# (Alternativo) Usando /mnt/data/casas_sucias.csv si existe
python scripts/cleaning.py --input /mnt/data/casas_sucias.csv --output data/casas_limpias.csv --report outputs/cleaning_report.json
```

El script imprime un resumen y guarda ejemplos antes/después en `outputs/cleaning_report.json`.

## 3) Entrenamiento

```bash
python train/train_model.py
```

- Guarda el modelo en `artifacts/model.pkl`.
- Guarda métricas en `outputs/metrics.json`.

## 4) API FastAPI

```bash
uvicorn app.main:app --reload --port 8000
```

- GET `http://127.0.0.1:8000/health`
- POST `http://127.0.0.1:8000/predict`

Ejemplo de request:

```json
{
  "superficie": "80m2",
  "habitaciones": "tres",
  "antiguedad": "nueva",
  "ubicacion": "urbano"
}
```

## 5) Despliegue en Render

El proyecto está configurado para desplegarse en Render usando Docker con Conda para evitar problemas de compilación.

### Archivos de configuración:
- `render.yaml`: Configuración para Render con Docker
- `Dockerfile`: Imagen basada en conda-forge con paquetes precompilados (evita compilación C/Cython)
- `requirements.txt`: Dependencias con versiones fijas
- `.dockerignore`: Optimiza el build excluyendo archivos innecesarios

### Despliegue en Render:
1. Subir el repositorio a GitHub
2. En Render, crear un "Web Service" 
3. Conectar el repositorio de GitHub
4. Render detectará automáticamente el `render.yaml` y usará Docker
5. El servicio estará disponible en la URL proporcionada por Render

### Probar localmente:
```bash
# Construir la imagen
docker build -t casas-api .

# Ejecutar localmente
docker run --rm -p 8000:8000 -e PORT=8000 casas-api

# Probar endpoint
curl http://localhost:8000/health
```

### Endpoints disponibles:
- `GET /health`: Estado del servicio y versión del modelo
- `POST /predict`: Predicción de precio de casas

## 6) Tests

```bash
pytest -q
```

## 7) Notas de limpieza (resumen)

- superficie: extrae dígitos de entradas como "120m2"; `?` -> NaN; imputación mediana por (`ubicacion`,`habitaciones`).
- habitaciones: convierte textos ("tres"->3), fuerza rango 1-10; imputa mediana por bins de superficie.
- antiguedad: `"nueva"->0`; negativos moderados -> valor absoluto; extremos -> NaN; imputa mediana por `ubicacion`.
- ubicacion: normaliza typos a {"urbano","rural"}; nulos -> moda.
- precio: invalida 0, negativos y placeholders (9999999); outliers por IQR (±3*IQR) -> NaN; filas sin precio se descartan para entrenar.

## 8) Verificación del modelo

- El archivo `artifacts/model.pkl` se crea al ejecutar `python train/train_model.py`.
- Para verificar:

```python
import joblib
model = joblib.load('artifacts/model.pkl')
print(type(model))
```
