import os
import time
import joblib
import pandas as pd
import numpy as np
from datetime import datetime
from typing import Literal
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

# Importar funciones de limpieza
import sys
sys.path.append('scripts')
from cleaning import clean_superficie, clean_habitaciones, clean_antiguedad, clean_ubicacion

app = FastAPI(title="API Precio Casas", version="1.0.0")

class PredictRequest(BaseModel):
    superficie: str | float = Field(..., description="Tamaño en m2")
    habitaciones: int | str = Field(..., description="Número de habitaciones")
    antiguedad: int | str = Field(..., description="Años desde construcción")
    ubicacion: str = Field(..., description="'urbano' o 'rural'")

class PredictResponse(BaseModel):
    precio_estimado: float
    unidad: Literal["COP"] = "COP"
    model_version: str
    prediction_ms: float

# Cargar modelo
MODEL_PATH = "artifacts/model.pkl"
_model = None
_model_version = None

def load_model():
    global _model, _model_version
    if _model is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Modelo no encontrado")
        _model = joblib.load(MODEL_PATH)
        _model_version = datetime.utcfromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat() + "Z"
    return _model

@app.get("/")
def root():
    return {"message": "API de Predicción de Precios de Casas", "version": "1.0.0"}

@app.get("/health")
def health():
    ok = os.path.exists(MODEL_PATH)
    version = None
    if ok:
        version = datetime.utcfromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat() + "Z"
    return {"status": "ok" if ok else "model_missing", "model_version": version}

def transform_payload(payload: PredictRequest) -> pd.DataFrame:
    s = clean_superficie(payload.superficie)
    h = clean_habitaciones(payload.habitaciones)
    a = clean_antiguedad(payload.antiguedad)
    u = clean_ubicacion(payload.ubicacion)

    # Valores por defecto
    if u is None or (isinstance(u, float) and np.isnan(u)):
        u = "urbano"
    if h is None or (isinstance(h, float) and np.isnan(h)):
        h = 3
    if s is None or (isinstance(s, float) and np.isnan(s)):
        s = 70.0
    if a is None or (isinstance(a, float) and np.isnan(a)):
        a = 10

    df = pd.DataFrame([{
        "superficie": s,
        "habitaciones": h,
        "antiguedad": a,
        "ubicacion": u
    }])
    return df

@app.post("/predict", response_model=PredictResponse)
def predict(payload: PredictRequest):
    start = time.perf_counter()
    model = load_model()
    try:
        X = transform_payload(payload)
        pred = float(model.predict(X)[0])
        ms = (time.perf_counter() - start) * 1000
        return PredictResponse(
            precio_estimado=pred,
            unidad="COP",
            model_version=_model_version,
            prediction_ms=ms,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)