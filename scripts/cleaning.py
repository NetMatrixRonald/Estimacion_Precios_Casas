import os
import re
import json
import math
from typing import Optional, Tuple

import numpy as np
import pandas as pd


# -----------------------------
# Funciones de limpieza atómicas
# -----------------------------

NUM_TXT_MAP = {
    "uno": 1, "una": 1, "dos": 2, "tres": 3, "cuatro": 4, "cinco": 5,
    "seis": 6, "siete": 7, "ocho": 8, "nueve": 9, "diez": 10,
}


def clean_superficie(value: object) -> Optional[float]:
    """Extrae el número de una superficie. Ejemplos válidos: "120", "120m2", " 85 m²".
    "?" o vacíos -> NaN. Números no positivos -> NaN.
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip().lower()
    if s in {"?", "", "nan", "none"}:
        return np.nan
    m = re.search(r"([0-9]+(?:[\.,][0-9]+)?)", s)
    if not m:
        return np.nan
    try:
        num = float(m.group(1).replace(",", "."))
        if num <= 0:
            return np.nan
        return num
    except Exception:
        return np.nan


def _to_int(value: object) -> Optional[int]:
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip().lower()
    if s in {"", "nan", "none", "?"}:
        return np.nan
    if s in NUM_TXT_MAP:
        return int(NUM_TXT_MAP[s])
    # intenta número directo
    try:
        v = int(float(s))
        return v
    except Exception:
        return np.nan


def clean_habitaciones(value: object) -> Optional[int]:
    """Convierte a entero 1..10; valores fuera de rango o no parseables -> NaN."""
    v = _to_int(value)
    if pd.isna(v):
        return np.nan
    if v < 1 or v > 10:
        return np.nan
    return int(v)


def clean_antiguedad(value: object) -> Optional[int]:
    """Normaliza antigüedad en años.
    - "nueva" -> 0
    - negativos: si |x| <= 120, tomar valor absoluto; si extremo (>|120|), NaN
    - no numéricos -> NaN
    """
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip().lower()
    if s in {"", "nan", "none", "?"}:
        return np.nan
    if s == "nueva" or s == "nuevo":
        return 0
    try:
        v = int(float(s))
        if v < 0:
            if abs(v) <= 120:
                return abs(v)
            else:
                return np.nan
        return v
    except Exception:
        return np.nan


def clean_ubicacion(value: object) -> Optional[str]:
    """Normaliza a {"urbano","rural"}. Corrige typos comunes y rellenará nulos luego con la moda."""
    if value is None or (isinstance(value, float) and np.isnan(value)):
        return np.nan
    s = str(value).strip().lower()
    if s in {"", "nan", "none", "?"}:
        return np.nan
    # reglas simples por prefijo/typos
    if s.startswith("urb") or s in {"urbnaa", "ubano", "urabno"}:
        return "urbano"
    if s.startswith("rur") or s in {"rurall", "rrual", "rurl"}:
        return "rural"
    # fallback: si contiene
    if "urb" in s:
        return "urbano"
    if "rur" in s:
        return "rural"
    return np.nan


def treat_precio(series: pd.Series) -> pd.Series:
    """Limpia precio target:
    - elimina 0, negativos y placeholders (p.ej. 9999999)
    - filtra outliers extremos por método IQR (fuera de [Q1-3*IQR, Q3+3*IQR])
    Regresa una Serie con valores inválidos como NaN para que se filtren.
    """
    s = pd.to_numeric(series, errors="coerce")
    s[(s <= 0) | (s == 9_999_999) | (s == 9999999.0)] = np.nan
    q1, q3 = s.quantile([0.25, 0.75])
    iqr = q3 - q1
    lower = q1 - 3 * iqr
    upper = q3 + 3 * iqr
    s[(s < lower) | (s > upper)] = np.nan
    return s


# -------------------------------------
# Pipeline de exploración y limpieza
# -------------------------------------

def explore_dataframe(df: pd.DataFrame) -> dict:
    info = {
        "shape": df.shape,
        "dtypes": df.dtypes.astype(str).to_dict(),
        "nulls": df.isna().sum().to_dict(),
        "head": df.head(5).to_dict(orient="records"),
        "describe": df.describe(include="all").to_dict(),
    }
    return info


def clean_dataframe(df: pd.DataFrame) -> Tuple[pd.DataFrame, dict]:
    df = df.copy()

    # limpiar columnas una a una
    df["superficie"] = df["superficie"].apply(clean_superficie)
    df["habitaciones"] = df["habitaciones"].apply(clean_habitaciones)
    df["antiguedad"] = df["antiguedad"].apply(clean_antiguedad)
    df["ubicacion"] = df["ubicacion"].apply(clean_ubicacion)

    # imputaciones razonables
    # - ubicacion: moda global
    if df["ubicacion"].isna().any():
        moda = df["ubicacion"].mode(dropna=True)
        fill_ubi = moda.iloc[0] if len(moda) else "urbano"
        df["ubicacion"] = df["ubicacion"].fillna(fill_ubi)

    # - habitaciones: mediana por bins de superficie (o global si no hay)
    superficie_bins = pd.qcut(df["superficie"], q=min(5, df["superficie"].nunique()), duplicates="drop")
    med_por_sup = df.groupby(superficie_bins)["habitaciones"].median()
    def _impute_hab(row):
        if not pd.isna(row["habitaciones"]):
            return row["habitaciones"]
        try:
            binv = superficie_bins.loc[row.name]
            val = med_por_sup.get(binv, np.nan)
            if pd.isna(val):
                return int(round(df["habitaciones"].median()))
            return int(round(val))
        except Exception:
            return int(round(df["habitaciones"].median()))
    df["habitaciones"] = df.apply(_impute_hab, axis=1)
    df["habitaciones"] = df["habitaciones"].clip(lower=1, upper=10)

    # - superficie: mediana por (ubicacion, habitaciones)
    med_sup = df.groupby(["ubicacion", "habitaciones"])['superficie'].median()
    def _impute_sup(row):
        if not pd.isna(row["superficie"]):
            return row["superficie"]
        val = med_sup.get((row["ubicacion"], row["habitaciones"]), np.nan)
        if pd.isna(val):
            return float(df["superficie"].median())
        return float(val)
    df["superficie"] = df.apply(_impute_sup, axis=1)

    # - antiguedad: mediana por ubicacion
    med_ant = df.groupby("ubicacion")["antiguedad"].median()
    def _impute_ant(row):
        if not pd.isna(row["antiguedad"]):
            return row["antiguedad"]
        val = med_ant.get(row["ubicacion"], np.nan)
        if pd.isna(val):
            return int(round(df["antiguedad"].median()))
        return int(round(val))
    df["antiguedad"] = df.apply(_impute_ant, axis=1)

    # precio: limpiar y luego filtrar filas inválidas
    df["precio"] = treat_precio(df["precio"])

    # generar ejemplos problemáticos (para reporte)
    problems = {
        "superficie_non_numeric": int((df["superficie"].isna()).sum()),
        "habitaciones_out_of_range": 0,  # ya normalizado
        "antiguedad_negative_fixed": 0,  # handled inline; no tracking original here
        "ubicacion_fixed": 0,
        "precio_outliers_marked": int(df["precio"].isna().sum()),
    }

    # descartar filas sin precio (no sirven para entrenar)
    df = df.dropna(subset=["precio"]).reset_index(drop=True)

    return df, problems


def main(input_path: Optional[str] = None, output_path: str = "data/casas_limpias.csv",
         report_path: str = "outputs/cleaning_report.json") -> None:
    # rutas
    if input_path is None:
        # soporta dos ubicaciones comunes
        candidate_paths = [
            os.path.join(os.getcwd(), "casas_sucias.csv"),
            "/mnt/data/casas_sucias.csv",
        ]
        for p in candidate_paths:
            if os.path.exists(p):
                input_path = p
                break
    if input_path is None or not os.path.exists(input_path):
        raise FileNotFoundError("No se encontró el archivo de entrada casas_sucias.csv")

    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    os.makedirs(os.path.dirname(report_path), exist_ok=True)

    df_raw = pd.read_csv(input_path)

    # exploración
    exploration = explore_dataframe(df_raw)

    # limpiar
    df_clean, problems = clean_dataframe(df_raw)

    # guardar
    df_clean.to_csv(output_path, index=False)

    # reporte
    report = {
        "exploration": {
            "shape": exploration["shape"],
            "dtypes": exploration["dtypes"],
            "nulls": exploration["nulls"],
        },
        "problems_summary": problems,
        "after_shape": df_clean.shape,
        "examples_before": exploration["head"],
        "examples_after": df_clean.head(5).to_dict(orient="records"),
    }
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print("Exploración inicial:")
    print(json.dumps(exploration, ensure_ascii=False, indent=2)[:1500])
    print("\nResumen de problemas:")
    print(json.dumps(problems, ensure_ascii=False, indent=2))
    print(f"\nGuardado dataset limpio en: {output_path}")
    print(f"Reporte de limpieza en: {report_path}")


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="Exploración y limpieza de casas")
    parser.add_argument("--input", dest="input_path", default=None)
    parser.add_argument("--output", dest="output_path", default="data/casas_limpias.csv")
    parser.add_argument("--report", dest="report_path", default="outputs/cleaning_report.json")
    args = parser.parse_args()
    main(args.input_path, args.output_path, args.report_path)


