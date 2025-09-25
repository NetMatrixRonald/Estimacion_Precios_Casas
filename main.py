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
try:
    from cleaning import clean_superficie, clean_habitaciones, clean_antiguedad, clean_ubicacion
except ImportError:
    # Funciones de limpieza básicas si no se puede importar
    def clean_superficie(x):
        if isinstance(x, str):
            import re
            nums = re.findall(r'\d+', x)
            return float(nums[0]) if nums else 70.0
        return float(x) if x else 70.0
    
    def clean_habitaciones(x):
        if isinstance(x, str):
            text_to_num = {'uno': 1, 'dos': 2, 'tres': 3, 'cuatro': 4, 'cinco': 5}
            return text_to_num.get(x.lower(), 3)
        return int(x) if x else 3
    
    def clean_antiguedad(x):
        if isinstance(x, str):
            if x.lower() == 'nueva':
                return 0
            import re
            nums = re.findall(r'\d+', x)
            return float(nums[0]) if nums else 10
        return int(x) if x else 10
    
    def clean_ubicacion(x):
        if isinstance(x, str):
            return x.lower() if x.lower() in ['urbano', 'rural'] else 'urbano'
        return 'urbano'

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