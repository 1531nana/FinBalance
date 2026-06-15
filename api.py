"""
api.py — API FastAPI para FinBalance
Componente opcional de la entrega final.

Endpoints:
    GET  /health   → estado de la API y del modelo
    GET  /metrics  → métricas del modelo desde model_metadata.json
    POST /predict  → predicción de fragilidad financiera

Uso:
    uvicorn api:app --reload
    uvicorn api:app --host 0.0.0.0 --port 8000

Documentación interactiva (Swagger):
    http://127.0.0.1:8000/docs
"""

import json
from contextlib import asynccontextmanager
from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# ── Rutas ────────────────────────────────────────────────────────────────────────
BASE      = Path(__file__).parent
RUTA_PKL  = BASE / "models" / "modelo_final.pkl"
RUTA_META = BASE / "models" / "model_metadata.json"

# ── Estado global ────────────────────────────────────────────────────────────────
estado = {"modelo": None, "metadata": None}

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

LABEL_MAP = {1: "Baja", 2: "Media", 3: "Alta"}
DESC_MAP = {
    1: "El hogar podría sostenerse 6 meses o más sin ingresos.",
    2: "El hogar cubriría gastos entre 1 y 5 meses.",
    3: "El hogar tiene reservas para menos de un mes. Alta vulnerabilidad financiera.",
}


# ── Lifespan: carga del modelo al arranque ───────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Verificar que los archivos existen antes de arrancar
    if not RUTA_PKL.exists():
        raise RuntimeError(
            f"Modelo no encontrado en {RUTA_PKL}. "
            "Ejecuta primero: python src/ml/entrenar_modelo.py"
        )
    if not RUTA_META.exists():
        raise RuntimeError(f"Metadata no encontrada en {RUTA_META}.")

    estado["modelo"] = joblib.load(RUTA_PKL)
    with open(RUTA_META, encoding="utf-8") as f:
        estado["metadata"] = json.load(f)

    print(f"Modelo cargado: {type(estado['modelo'])}")
    print(f"Modelo: {estado['metadata'].get('modelo')} | "
          f"F1 macro: {estado['metadata'].get('valor_metrica')}")
    yield
    # Limpieza al apagar (opcional)
    estado["modelo"] = None
    estado["metadata"] = None


# ── Aplicación ───────────────────────────────────────────────────────────────────
app = FastAPI(
    title="FinBalance API",
    description=(
        "API de predicción de fragilidad financiera sobre la "
        "Encuesta de Demanda Financiera 2022 (Colombia). "
        "Proyecto integrador — Diplomado en Desarrollo Web para Analítica de Datos."
    ),
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ── Esquema Pydantic de entrada ──────────────────────────────────────────────────
class EntradaPrediccion(BaseModel):
    # Productos financieros
    prod_cuenta_ahorro:  int = Field(0, ge=0, le=1, description="Tiene cuenta de ahorro (0/1)")
    prod_tarjeta_debito: int = Field(0, ge=0, le=1, description="Tiene tarjeta débito (0/1)")
    prod_monedero:       int = Field(0, ge=0, le=1, description="Tiene monedero digital (0/1)")
    prod_cdt:            int = Field(0, ge=0, le=1, description="Tiene CDT (0/1)")
    prod_fondo_inv:      int = Field(0, ge=0, le=1, description="Tiene fondo de inversión (0/1)")
    prod_fondo_emp:      int = Field(0, ge=0, le=1, description="Tiene fondo de empleados (0/1)")
    # Fuentes de ingreso
    ing_salario:        int = Field(0, ge=0, le=1, description="Recibe salario (0/1)")
    ing_pension:        int = Field(0, ge=0, le=1, description="Recibe pensión (0/1)")
    ing_arriendos:      int = Field(0, ge=0, le=1, description="Recibe arriendos (0/1)")
    ing_honorarios:     int = Field(0, ge=0, le=1, description="Recibe honorarios (0/1)")
    ing_ventas:         int = Field(0, ge=0, le=1, description="Recibe ingresos por ventas (0/1)")
    ing_subsidios:      int = Field(0, ge=0, le=1, description="Recibe subsidios (0/1)")
    ing_remesas:        int = Field(0, ge=0, le=1, description="Recibe remesas (0/1)")
    ing_ayuda_familiar: int = Field(0, ge=0, le=1, description="Recibe ayuda familiar (0/1)")
    # Gastos
    gasto_arriendo:   int = Field(0, ge=0, le=1, description="Paga arriendo (0/1)")
    gasto_servicios:  int = Field(0, ge=0, le=1, description="Paga servicios públicos (0/1)")
    gasto_seg_social: int = Field(0, ge=0, le=1, description="Paga seguridad social (0/1)")
    # Comportamiento financiero
    comp_atraso_pagos:        int = Field(1, ge=1, le=5, description="Frecuencia de atrasos en pagos (1=Nunca · 5=Siempre)")
    comp_deuda_mayor_activos: int = Field(1, ge=1, le=5, description="Deudas superan activos (1=Desacuerdo · 5=Acuerdo)")
    comp_tiene_plan:          int = Field(0, ge=0, le=1, description="Tiene plan financiero formal (0/1)")
    # Hábitos
    hab_encargado_gastos: int = Field(0, ge=0, le=1, description="Responsable de gastos del hogar (0/1)")
    hab_encargado_presup: int = Field(0, ge=0, le=1, description="Responsable del presupuesto (0/1)")
    hab_usa_app_bancaria: int = Field(0, ge=0, le=1, description="Usa app bancaria (0/1)")
    # Percepciones financieras
    perc_camino_obj:      int = Field(3, ge=1, le=5, description="Va por buen camino a objetivos (1–5)")
    perc_deuda_manejable: int = Field(3, ge=1, le=5, description="Deudas son manejables (1–5)")
    perc_control_sit:     int = Field(3, ge=1, le=5, description="Control sobre situación financiera (1–5)")
    # Sociodemográficas
    edad:            int   = Field(35,  ge=18, le=99,  description="Edad en años")
    nivel_educativo: int   = Field(2,   ge=0,  le=6,   description="Nivel educativo (0=Ninguno · 6=Posgrado)")
    estrato:         int   = Field(2,   ge=1,  le=6,   description="Estrato socioeconómico (1–6)")
    rango_ingresos:  int   = Field(4,   ge=1,  le=10,  description="Rango de ingresos mensuales (1=mín · 10=máx)")
    rango_gastos:    int   = Field(4,   ge=1,  le=10,  description="Rango de gastos mensuales (1=mín · 10=máx)")
    genero_Masculino: int  = Field(0,   ge=0,  le=1,   description="Género masculino (1) o femenino (0)")
    # Ruralidad (one-hot — solo uno puede ser 1)
    ruralidad_Intermedio:    int = Field(0, ge=0, le=1)
    ruralidad_Rural:         int = Field(0, ge=0, le=1)
    ruralidad_Rural_disperso: int = Field(0, ge=0, le=1, alias="ruralidad_Rural disperso")
    # Región (one-hot — solo una puede ser 1)
    region_Centro_Oriente: int = Field(0, ge=0, le=1, alias="region_Centro Oriente")
    region_Centro_Sur:     int = Field(0, ge=0, le=1, alias="region_Centro Sur")
    region_Eje_cafetero:   int = Field(0, ge=0, le=1, alias="region_Eje cafetero")
    region_Llano:          int = Field(0, ge=0, le=1)
    region_Pacifico:       int = Field(0, ge=0, le=1, alias="region_Pacífico")

    model_config = {"populate_by_name": True}


# ── Endpoints ────────────────────────────────────────────────────────────────────

@app.get("/health", tags=["Estado"])
def health():
    """Estado de la API y verificación de carga del modelo."""
    modelo = estado.get("modelo")
    meta   = estado.get("metadata", {})
    return {
        "status": "ok",
        "modelo_cargado": modelo is not None,
        "modelo": meta.get("modelo", "—"),
        "version": meta.get("version", "—"),
        "fecha_entrenamiento": meta.get("fecha_entrenamiento", "—"),
        "sklearn_version": meta.get("sklearn_version", "—"),
    }


@app.get("/metrics", tags=["Modelo"])
def metrics():
    """Métricas del modelo leídas desde model_metadata.json."""
    meta = estado.get("metadata")
    if not meta:
        raise HTTPException(status_code=503, detail="Metadata no disponible.")
    return {
        "modelo": meta.get("modelo"),
        "version": meta.get("version"),
        "metrica_principal": meta.get("metrica_principal"),
        "valor_metrica": meta.get("valor_metrica"),
        "accuracy": meta.get("accuracy"),
        "precision_macro": meta.get("precision_macro"),
        "recall_macro": meta.get("recall_macro"),
        "auc_macro_ovr": meta.get("auc_macro_ovr"),
        "cv_f1_macro_mean": meta.get("cv_f1_macro_mean"),
        "cv_f1_macro_std": meta.get("cv_f1_macro_std"),
        "n_train": meta.get("n_train"),
        "n_test": meta.get("n_test"),
        "n_features": meta.get("n_features"),
        "classification_report": meta.get("classification_report"),
    }


@app.post("/predict", tags=["Predicción"])
def predict(entrada: EntradaPrediccion):
    """
    Predice el nivel de fragilidad financiera de un hogar.

    Retorna:
    - **prediccion**: clase predicha (1=Baja, 2=Media, 3=Alta)
    - **etiqueta**: nombre de la clase en español
    - **descripcion**: interpretación en lenguaje natural
    - **probabilidades**: probabilidad por clase
    - **advertencia_etica**: recordatorio de uso responsable
    """
    modelo = estado.get("modelo")
    if not modelo:
        raise HTTPException(status_code=503, detail="Modelo no cargado.")

    # Construir el DataFrame con los alias correctos (espacios en nombres)
    datos = entrada.model_dump(by_alias=True)
    X = pd.DataFrame([{f: datos.get(f, 0) for f in FEATURES}])

    pred  = int(modelo.predict(X)[0])
    proba = modelo.predict_proba(X)[0]

    return {
        "prediccion": pred,
        "etiqueta": LABEL_MAP.get(pred, "Desconocida"),
        "descripcion": DESC_MAP.get(pred, ""),
        "probabilidades": {
            LABEL_MAP[i + 1]: round(float(p), 4)
            for i, p in enumerate(proba)
        },
        "advertencia_etica": (
            "Este resultado es una estimación estadística generada por un modelo de machine learning. "
            "Debe ser revisado por una persona responsable antes de tomar decisiones financieras, "
            "crediticias o de política pública. No reemplaza la asesoría de un experto."
        ),
    }
