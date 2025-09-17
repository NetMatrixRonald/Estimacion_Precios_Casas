import os
import time
from datetime import datetime
from typing import Literal, Optional

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field, validator

# importar funciones de limpieza
from scripts.cleaning import (
    clean_superficie,
    clean_habitaciones,
    clean_antiguedad,
    clean_ubicacion,
)


class PredictRequest(BaseModel):
    superficie: str | float = Field(..., description="Tamaño en m2, puede ser texto como '120m2'")
    habitaciones: int | str = Field(..., description="Número de habitaciones (1-10)")
    antiguedad: int | str = Field(..., description="Años desde construcción o 'nueva'")
    ubicacion: str = Field(..., description="'urbano' o 'rural'")

    @validator("habitaciones")
    def _validate_hab(cls, v):
        return v


class PredictResponse(BaseModel):
    precio_estimado: float
    unidad: Literal["COP"] = "COP"
    model_version: str
    prediction_ms: float


app = FastAPI(title="API Precio Casas", version="1.0.0")

MODEL_PATH = os.path.join("artifacts", "model.pkl")
_MODEL = None
_MODEL_VERSION = None


def load_model():
    global _MODEL, _MODEL_VERSION
    if _MODEL is None:
        if not os.path.exists(MODEL_PATH):
            raise FileNotFoundError("Modelo no encontrado. Entrena primero con train/train_model.py")
        _MODEL = joblib.load(MODEL_PATH)
        _MODEL_VERSION = datetime.utcfromtimestamp(os.path.getmtime(MODEL_PATH)).isoformat() + "Z"
    return _MODEL


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

    # reglas de imputación consistentes con cleaning.py
    if u is None or (isinstance(u, float) and np.isnan(u)):
        u = "urbano"
    if h is None or (isinstance(h, float) and np.isnan(h)):
        h = 3
    if s is None or (isinstance(s, float) and np.isnan(s)):
        s = 70.0
    if a is None or (isinstance(a, float) and np.isnan(a)):
        a = 10

    df = pd.DataFrame([
        {"superficie": s, "habitaciones": h, "antiguedad": a, "ubicacion": u}
    ])
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
            model_version=_MODEL_VERSION,
            prediction_ms=ms,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


# Ejecutar con: uvicorn app.main:app --reload --port 8000


