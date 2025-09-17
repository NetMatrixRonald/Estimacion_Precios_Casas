import os
import json
from datetime import datetime

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.tree import DecisionTreeRegressor
from sklearn.metrics import mean_absolute_error, r2_score


def load_data(path: str) -> pd.DataFrame:
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existee el dataset limpio en {path}. Ejecuta scripts/cleaning.py primero.")
    return pd.read_csv(path)


def build_pipeline() -> Pipeline:
    numeric_features = ["superficie", "habitaciones", "antiguedad"]
    categorical_features = ["ubicacion"]

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", "passthrough", numeric_features),
            ("cat", OneHotEncoder(handle_unknown="ignore"), categorical_features),
        ]
    )

    reg = DecisionTreeRegressor(random_state=42)

    pipe = Pipeline(steps=[
        ("prep", preprocessor),
        ("reg", reg),
    ])
    return pipe


def train_and_evaluate(df: pd.DataFrame, do_search: bool = True):
    X = df[["superficie", "habitaciones", "antiguedad", "ubicacion"]]
    y = df["precio"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    pipe = build_pipeline()

    if do_search:
        param_grid = {
            "reg__max_depth": [None, 5, 10, 20],
            "reg__min_samples_split": [2, 5, 10],
            "reg__min_samples_leaf": [1, 2, 5],
        }
        search = GridSearchCV(pipe, param_grid, cv=5, n_jobs=-1)
        search.fit(X_train, y_train)
        model = search.best_estimator_
        best_params = search.best_params_
    else:
        model = pipe.fit(X_train, y_train)
        best_params = model.get_params()

    preds = model.predict(X_test)
    mae = float(mean_absolute_error(y_test, preds))
    r2 = float(r2_score(y_test, preds))

    return model, {"MAE": mae, "R2": r2, "best_params": best_params}


def main():
    os.makedirs("artifacts", exist_ok=True)
    os.makedirs("outputs", exist_ok=True)

    df = load_data("data/casas_limpias.csv")
    model, metrics = train_and_evaluate(df, do_search=True)

    # guardar modelo
    model_path = os.path.join("artifacts", "model.pkl")
    joblib.dump(model, model_path)

    # guardar métricas
    metrics["model_saved_at"] = datetime.utcnow().isoformat() + "Z"
    with open(os.path.join("outputs", "metrics.json"), "w", encoding="utf-8") as f:
        json.dump(metrics, f, ensure_ascii=False, indent=2)

    print("Modelo guardado en:", model_path)
    print("Métricas:", json.dumps(metrics, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()


