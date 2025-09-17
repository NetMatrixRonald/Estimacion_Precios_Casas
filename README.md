# Predicción de precios de casas (Colombia)

Este proyecto limpia datos de viviendas, entrena un Árbol de Regresión y expone un endpoint de predicción con FastAPI.

## 1) Instalación

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

1. Subir el repo a GitHub.
2. En Render, crear un servicio "Web Service" de tipo Python.
3. Seleccionar el repo y usar `Procfile` con:

```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

4. Configurar `Build Command` (opcional): `pip install -r requirements.txt`.
5. Deploy.

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
