"""
src/ml/entrenar_modelo.py
Script de entrenamiento local reproducible para FinBalance.

Uso:
    python src/ml/entrenar_modelo.py

Requisitos:
    - data/processed/train.csv  generado por notebooks/02_eda_limpieza.ipynb
    - data/processed/test.csv   generado por notebooks/02_eda_limpieza.ipynb

Produce:
    - models/modelo_final.pkl
    - models/model_metadata.json
"""

import json
import warnings
from datetime import date
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
import sklearn
from sklearn.dummy import DummyClassifier
from sklearn.ensemble import GradientBoostingClassifier, RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import (
    accuracy_score,
    classification_report,
    f1_score,
    precision_score,
    recall_score,
    roc_auc_score,
)
from sklearn.model_selection import cross_val_score, StratifiedKFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.tree import DecisionTreeClassifier

warnings.filterwarnings("ignore")

# ── Rutas ───────────────────────────────────────────────────────────────────────
BASE       = Path(__file__).resolve().parents[2]
RUTA_TRAIN = BASE / "data" / "processed" / "train.csv"
RUTA_TEST  = BASE / "data" / "processed" / "test.csv"
RUTA_PKL   = BASE / "models" / "modelo_final.pkl"
RUTA_META  = BASE / "models" / "model_metadata.json"

FEATURES = [
    "prod_cuenta_ahorro", "prod_tarjeta_debito", "prod_monedero",
    "prod_cdt", "prod_fondo_inv", "prod_fondo_emp",
    "ing_salario", "ing_pension", "ing_arriendos", "ing_honorarios",
    "ing_ventas", "ing_subsidios", "ing_remesas", "ing_ayuda_familiar",
    "gasto_arriendo", "gasto_servicios", "gasto_seg_social",
    "comp_atraso_pagos",
    "perc_camino_obj", "perc_deuda_manejable",
    "comp_deuda_mayor_activos",
    "perc_control_sit",
    "hab_encargado_gastos", "comp_tiene_plan", "hab_encargado_presup", "hab_usa_app_bancaria",
    "edad", "nivel_educativo", "estrato", "rango_ingresos", "rango_gastos",
    "genero_Masculino",
    "ruralidad_Intermedio", "ruralidad_Rural", "ruralidad_Rural disperso",
    "region_Centro Oriente", "region_Centro Sur", "region_Eje cafetero",
    "region_Llano", "region_Pacífico",
]
TARGET       = "fragilidad_label"
RANDOM_STATE = 42


# ── Carga de datos ───────────────────────────────────────────────────────────────
def cargar_datos():
    print(f"Cargando train desde {RUTA_TRAIN} ...")
    train = pd.read_csv(RUTA_TRAIN)
    print(f"Cargando test  desde {RUTA_TEST} ...")
    test  = pd.read_csv(RUTA_TEST)

    X_train = train[FEATURES]
    y_train = train[TARGET]
    X_test  = test[FEATURES]
    y_test  = test[TARGET]

    print(f"  Train: {X_train.shape} | Test: {X_test.shape}")
    return X_train, y_train, X_test, y_test


# ── Definición de pipelines ──────────────────────────────────────────────────────
def construir_pipeline_gb():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", GradientBoostingClassifier(
            n_estimators=200,
            max_depth=4,
            learning_rate=0.1,
            random_state=RANDOM_STATE,
        )),
    ])


def construir_pipeline_rf():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", RandomForestClassifier(
            n_estimators=300,
            max_depth=None,
            min_samples_leaf=2,
            random_state=RANDOM_STATE,
            n_jobs=-1,
        )),
    ])


def construir_pipeline_lr():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", LogisticRegression(
            max_iter=1000,
            random_state=RANDOM_STATE,
            solver="lbfgs",
        )),
    ])


def construir_pipeline_dt():
    return Pipeline([
        ("scaler", StandardScaler()),
        ("clf", DecisionTreeClassifier(
            max_depth=6,
            random_state=RANDOM_STATE,
        )),
    ])


# ── Evaluación de un pipeline ────────────────────────────────────────────────────
def evaluar(nombre, pipeline, X_train, y_train, X_test, y_test):
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=RANDOM_STATE)
    cv_scores = cross_val_score(
        pipeline, X_train, y_train, cv=cv, scoring="f1_macro", n_jobs=-1
    )
    pipeline.fit(X_train, y_train)
    y_pred = pipeline.predict(X_test)
    f1  = f1_score(y_test, y_pred, average="macro")
    acc = accuracy_score(y_test, y_pred)
    print(f"\n  [{nombre}]")
    print(f"    CV F1 macro:   {cv_scores.mean():.4f} ± {cv_scores.std():.4f}")
    print(f"    Test F1 macro: {f1:.4f}")
    print(f"    Test Accuracy: {acc:.4f}")
    return pipeline, f1, acc, cv_scores


# ── Main ─────────────────────────────────────────────────────────────────────────
def main():
    RUTA_PKL.parent.mkdir(parents=True, exist_ok=True)

    X_train, y_train, X_test, y_test = cargar_datos()

    # ── Comparación de modelos ───────────────────────────────────────────────────
    print("\n--- Comparacion de modelos ---")

    pipe_dummy = Pipeline([("clf", DummyClassifier(strategy="most_frequent"))])
    pipe_dummy.fit(X_train, y_train)
    y_dummy = pipe_dummy.predict(X_test)
    f1_dummy = f1_score(y_test, y_dummy, average="macro")
    acc_dummy = accuracy_score(y_test, y_dummy)
    print(f"\n  [DummyClassifier]  F1 macro: {f1_dummy:.4f}  Accuracy: {acc_dummy:.4f}")

    pipe_lr, f1_lr, acc_lr, _ = evaluar(
        "Logistic Regression", construir_pipeline_lr(), X_train, y_train, X_test, y_test
    )
    pipe_dt, f1_dt, acc_dt, _ = evaluar(
        "Decision Tree", construir_pipeline_dt(), X_train, y_train, X_test, y_test
    )
    pipe_rf, f1_rf, acc_rf, _ = evaluar(
        "Random Forest", construir_pipeline_rf(), X_train, y_train, X_test, y_test
    )
    pipe_gb, f1_gb, acc_gb, cv_gb = evaluar(
        "Gradient Boosting", construir_pipeline_gb(), X_train, y_train, X_test, y_test
    )

    comparacion_modelos = [
        {"nombre": "Decision Tree",       "f1_macro": round(f1_dt,  3), "accuracy": round(acc_dt,  3)},
        {"nombre": "Logistic Regression", "f1_macro": round(f1_lr,  3), "accuracy": round(acc_lr,  3)},
        {"nombre": "Random Forest",       "f1_macro": round(f1_rf,  3), "accuracy": round(acc_rf,  3)},
        {"nombre": "Gradient Boosting",   "f1_macro": round(f1_gb,  3), "accuracy": round(acc_gb,  3)},
    ]

    # ── Modelo final: Gradient Boosting ─────────────────────────────────────────
    print(f"\n--- Modelo final: Gradient Boosting (F1 macro = {f1_gb:.4f}) ---")

    y_pred_final = pipe_gb.predict(X_test)
    y_proba_final = pipe_gb.predict_proba(X_test)

    report = classification_report(y_test, y_pred_final, output_dict=True)
    prec   = precision_score(y_test, y_pred_final, average="macro")
    rec    = recall_score(y_test, y_pred_final, average="macro")
    auc    = roc_auc_score(y_test, y_proba_final, multi_class="ovr", average="macro")

    # ── Serialización ────────────────────────────────────────────────────────────
    joblib.dump(pipe_gb, RUTA_PKL)
    print(f"Modelo guardado en {RUTA_PKL}")

    # ── Metadata ─────────────────────────────────────────────────────────────────
    metadata = {
        "modelo": "Gradient Boosting",
        "version": "2.0",
        "fecha_entrenamiento": str(date.today()),
        "sklearn_version": sklearn.__version__,
        "semilla": RANDOM_STATE,
        "metrica_principal": "f1_score_macro",
        "valor_metrica": round(f1_gb, 4),
        "accuracy": round(acc_gb, 4),
        "precision_macro": round(prec, 4),
        "recall_macro": round(rec, 4),
        "auc_macro_ovr": round(auc, 4),
        "cv_f1_macro_mean": round(float(cv_gb.mean()), 4),
        "cv_f1_macro_std": round(float(cv_gb.std()), 4),
        "split": {"train": "80%", "test": "20% (holdout final)"},
        "n_train": len(X_train),
        "n_test": len(X_test),
        "clases": {"1": "Baja (>=6 meses)", "2": "Media (1-3 meses)", "3": "Alta (<1 mes)"},
        "variable_objetivo": TARGET,
        "n_features": len(FEATURES),
        "variables_entrada": FEATURES,
        "classification_report": report,
        "comparacion_modelos": comparacion_modelos,
        "experimento_20_variables": {
            "n_features": 20,
            "f1_macro": 0.497,
            "descripcion": "20 variables con mayor correlacion con la variable objetivo (seleccion alternativa)"
        },
        "observaciones": (
            f"Pipeline con StandardScaler + Gradient Boosting. "
            f"Entrenado con semilla {RANDOM_STATE}. "
            "Split estratificado 80/20. "
            "Se probaron 5 estrategias de balanceo de clases (ver seccion 3.8); "
            "el modelo base logro el mayor F1 macro global."
        ),
    }

    with open(RUTA_META, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)
    print(f"Metadata guardada en {RUTA_META}")

    # ── Verificación de carga ────────────────────────────────────────────────────
    modelo_cargado = joblib.load(RUTA_PKL)
    print(f"Verificacion de carga: {type(modelo_cargado)}")
    print("\nEntrenamiento completado.")


if __name__ == "__main__":
    main()
