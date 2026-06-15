"""
FinBalance — Dashboard de Predicción de Fragilidad Financiera
Diplomado en Desarrollo Web para Analítica de Datos — Entrega final
"""

import json
import joblib
import numpy as np
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
from pathlib import Path

# ── Configuración de página ─────────────────────────────────────────────────────
st.set_page_config(
    page_title="FinBalance",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Rutas ───────────────────────────────────────────────────────────────────────
BASE      = Path(__file__).parent
RUTA_PKL  = BASE / "models" / "modelo_final.pkl"
RUTA_META = BASE / "models" / "model_metadata.json"
RUTA_DS   = BASE / "data" / "processed" / "dataset_limpio.csv"
RUTA_TR   = BASE / "data" / "processed" / "train.csv"

# ── Paleta de colores ────────────────────────────────────────────────────────────
# Paleta inspirada en dashboards modernos: morado principal, acentos cálidos
# y colores semánticos para las clases de fragilidad.
C_PRIMARY        = "#6C63FF"   # Morado principal
C_PRIMARY_DARK   = "#5B4FE8"
C_PRIMARY_SOFT   = "#EEEAFE"

C_ACCENT         = "#F09C5E"   # Naranja cálido
C_ACCENT_CORAL   = "#E67A52"   # Coral
C_ACCENT_YELLOW  = "#F2C94C"   # Amarillo suave
C_ACCENT_CYAN    = "#4CC9F0"   # Cian de apoyo

C_SUCCESS        = "#39B98A"   # Baja
C_WARNING        = "#E9B949"   # Media
C_DANGER         = "#E16A5E"   # Alta

C_BG             = "#F7F7FB"   # Fondo general
C_CARD           = "#FFFFFF"   # Tarjetas
C_CARD_SOFT      = "#FBF8F4"   # Bloques suaves
C_BORDER         = "#ECEAF4"
C_TEXT           = "#26233A"
C_TEXT_SOFT      = "#6F6B86"
C_MUTED          = "#9B97B4"

# Alias para mantener compatibilidad con el resto del código.
C_VERDE = C_SUCCESS
C_AMBER = C_WARNING
C_ROJO  = C_DANGER
C_AZUL  = C_PRIMARY
C_TEAL  = C_ACCENT_CYAN

CLASES = {1: "Baja", 2: "Media", 3: "Alta"}

COLOR_CLASE = {
    1: C_SUCCESS,
    2: C_WARNING,
    3: C_DANGER,
}

BG_CLASE = {
    1: {"bg": "#EAF8F2", "borde": C_SUCCESS, "texto": "#1E6B52"},
    2: {"bg": "#FFF7E8", "borde": C_WARNING, "texto": "#8A6218"},
    3: {"bg": "#FDEEEB", "borde": C_DANGER,  "texto": "#9C453C"},
}

DESC_CLASE = {
    1: "El hogar podría sostenerse durante 6 meses o más sin ingresos. Es una situación financiera más sólida.",
    2: "El hogar podría cubrir sus gastos entre 1 y 5 meses. Es una situación que requiere atención.",
    3: "El hogar tiene reservas para menos de un mes. Presenta una alta vulnerabilidad financiera.",
}

LABEL_MAP = {1: "Baja", 2: "Media", 3: "Alta"}

PLOTLY_LAYOUT = dict(
    plot_bgcolor="white",
    paper_bgcolor="white",
    font=dict(color=C_TEXT, family="Arial"),
    margin=dict(t=50, b=20, l=20, r=20),
)

FEATURES = [
    # Productos financieros
    "prod_cuenta_ahorro", "prod_tarjeta_debito", "prod_monedero",
    "prod_cdt", "prod_fondo_inv", "prod_fondo_emp",
    # Fuentes de ingreso (binarias)
    "ing_salario", "ing_pension", "ing_arriendos", "ing_honorarios",
    "ing_ventas", "ing_subsidios", "ing_remesas", "ing_ayuda_familiar",
    # Gastos (binarias)
    "gasto_arriendo", "gasto_servicios", "gasto_seg_social",
    # Comportamiento y percepciones (orden de train.csv)
    "comp_atraso_pagos",
    "perc_camino_obj", "perc_deuda_manejable",
    "comp_deuda_mayor_activos",
    "perc_control_sit",
    "hab_encargado_gastos", "comp_tiene_plan", "hab_encargado_presup", "hab_usa_app_bancaria",
    # Sociodemograficas
    "edad", "nivel_educativo", "estrato", "rango_ingresos", "rango_gastos",
    "genero_Masculino",
    "ruralidad_Intermedio", "ruralidad_Rural", "ruralidad_Rural disperso",
    "region_Centro Oriente", "region_Centro Sur", "region_Eje cafetero",
    "region_Llano", "region_Pacífico",
]

MAPA_EDU     = {"Ninguno":0,"Primaria":1,"Secundaria":2,"Técnico":3,"Tecnólogo":4,"Universitarios":5,"Posgrado":6}
RANGOS_ING   = {
    "Menos de $250.000":1,"Entre $250.001 y $500.000":2,"Entre $500.001 y $750.000":3,
    "Entre $750.001 y $1.000.000":4,"Entre $1.000.001 y $1.500.000":5,
    "Entre $1.500.001 y $2.000.000":6,"Entre $2.000.001 y $3.000.000":7,
    "Entre $3.000.001 y $4.000.000":8,"Entre $4.000.001 y $5.000.000":9,"Más de $5.000.000":10,
}
RURALIDAD_OPTS = ["Ciudades y aglomeraciones", "Intermedio", "Rural", "Rural disperso"]
REGION_OPTS    = ["Caribe", "Centro Oriente", "Centro Sur", "Eje cafetero", "Llano", "Pacífico"]


# ── CSS global ──────────────────────────────────────────────────────────────────
st.markdown("""
<style>
:root {
    --primary: #6C63FF;
    --primary-dark: #5B4FE8;
    --primary-soft: #EEEAFE;
    --accent: #F09C5E;
    --accent-coral: #E67A52;
    --accent-yellow: #F2C94C;
    --accent-cyan: #4CC9F0;
    --success: #39B98A;
    --warning: #E9B949;
    --danger: #E16A5E;
    --bg: #F7F7FB;
    --card: #FFFFFF;
    --card-soft: #FBF8F4;
    --border: #ECEAF4;
    --text: #26233A;
    --text-soft: #6F6B86;
    --muted: #9B97B4;
}

/* ── Fondo principal ── */
[data-testid="stAppViewContainer"] > .main {
    background: var(--bg);
}

[data-testid="block-container"] {
    padding: 2rem 2rem 4rem 2rem !important;
    max-width: 1450px;
}

/* ── Sidebar ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #6C63FF 0%, #5B4FE8 50%, #4B3FD2 100%);
    border-right: 1px solid rgba(255,255,255,0.12);
}

[data-testid="stSidebar"] > div {
    padding-top: 1.5rem;
}

[data-testid="stSidebar"] h1,
[data-testid="stSidebar"] h2,
[data-testid="stSidebar"] h3,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] label {
    color: #F8F7FF !important;
}

[data-testid="stSidebar"] hr {
    border-color: rgba(255,255,255,0.10) !important;
}

/* ── Navegación ── */
[data-testid="stSidebar"] .stRadio > div {
    gap: 6px !important;
}

[data-testid="stSidebar"] .stRadio > div > label {
    color: #F0EEFF !important;
    font-size: 0.90rem !important;
    padding: 10px 14px !important;
    border-radius: 14px !important;
    margin: 2px 4px !important;
    cursor: pointer !important;
    background: rgba(255,255,255,0.08) !important;
    border: 1px solid rgba(255,255,255,0.12) !important;
    display: flex !important;
    align-items: center !important;
    width: calc(100% - 8px) !important;
    transition: all 0.2s ease;
}

[data-testid="stSidebar"] .stRadio > div > label:hover {
    background: rgba(255,255,255,0.16) !important;
    border-color: rgba(255,255,255,0.18) !important;
}

[data-testid="stSidebar"] .stRadio > div [data-baseweb="radio"] > div:first-child {
    background-color: transparent !important;
    border-color: rgba(255,255,255,0.30) !important;
}

[data-testid="stSidebar"] .stRadio > div input:checked + div [data-baseweb="radio"] > div:first-child,
[data-testid="stSidebar"] .stRadio > div label:has(input:checked) {
    background: rgba(255,255,255,0.18) !important;
    color: white !important;
    border-color: rgba(255,255,255,0.25) !important;
    box-shadow: 0 6px 18px rgba(40, 30, 120, 0.18);
}

[data-testid="stSidebar"] [data-testid="stMetricValue"] {
    color: #FFFFFF !important;
    font-size: 1.3rem !important;
}

[data-testid="stSidebar"] [data-testid="stMetricLabel"] {
    color: #E7E3FF !important;
}

[data-testid="stSidebar"] [data-testid="stCaptionContainer"] {
    color: #E7E3FF !important;
}

/* ── Header principal ── */
.page-header {
    background: linear-gradient(135deg, #6C63FF 0%, #7D6BFF 55%, #F09C5E 100%);
    border-radius: 22px;
    padding: 30px 34px;
    margin-bottom: 24px;
    box-shadow: 0 14px 30px rgba(108, 99, 255, 0.18);
}

.page-header h1 {
    color: white !important;
    font-size: 2rem !important;
    font-weight: 800 !important;
    margin: 0 !important;
    letter-spacing: -0.02em;
}

.page-header p {
    color: rgba(255,255,255,0.90) !important;
    font-size: 0.97rem !important;
    margin: 8px 0 0 0 !important;
    line-height: 1.5;
}

/* ── KPI Cards ── */
.kpi-card {
    background: var(--card);
    border-radius: 20px;
    padding: 20px 22px;
    box-shadow: 0 10px 24px rgba(21, 18, 55, 0.06);
    border: 1px solid var(--border);
    border-top: 4px solid;
    height: 100%;
    margin-bottom: 0;
}

.kpi-label {
    font-size: 0.72rem;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-soft);
    font-weight: 700;
    margin-bottom: 8px;
}

.kpi-value {
    font-size: 1.95rem;
    font-weight: 800;
    line-height: 1;
    margin: 0;
    color: var(--text);
}

.kpi-sub {
    font-size: 0.80rem;
    color: var(--muted);
    margin-top: 8px;
}

.kpi-icon {
    font-size: 1.35rem;
    float: right;
    opacity: 0.35;
}

/* ── Tarjetas de contenido ── */
.card {
    background: var(--card);
    border-radius: 20px;
    padding: 22px 24px;
    border: 1px solid var(--border);
    box-shadow: 0 8px 24px rgba(22, 19, 60, 0.05);
    margin-bottom: 16px;
}

.card-title {
    font-size: 0.76rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--text-soft);
    margin-bottom: 16px;
    padding-bottom: 10px;
    border-bottom: 1px solid var(--border);
}

/* ── Etiquetas de sección ── */
.sec-label {
    font-size: 0.74rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary);
    border-left: 4px solid var(--primary);
    padding-left: 10px;
    margin: 22px 0 12px 0;
}

/* ── Badges ── */
.badge {
    display: inline-block;
    padding: 6px 14px;
    border-radius: 999px;
    font-size: 0.78rem;
    font-weight: 700;
    border: 1px solid transparent;
}

.badge-alta  { background:#FDEEEB; color:#9C453C; border-color:#F4C0B8; }
.badge-media { background:#FFF7E8; color:#8A6218; border-color:#F1D388; }
.badge-baja  { background:#EAF8F2; color:#1E6B52; border-color:#9EDBC2; }

/* ── Resultado de predicción ── */
.res-card {
    border-radius: 22px;
    padding: 28px 32px;
    border-left: 8px solid;
    box-shadow: 0 12px 24px rgba(22, 19, 60, 0.07);
    margin: 16px 0;
}

.res-eyebrow {
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    opacity: 0.7;
    margin-bottom: 6px;
}

.res-class {
    font-size: 3rem;
    font-weight: 900;
    line-height: 1;
    margin: 0;
}

.res-desc {
    font-size: 0.96rem;
    margin-top: 10px;
    opacity: 0.86;
    line-height: 1.6;
}

/* ── Formularios ── */
.form-sec {
    font-size: 0.72rem;
    font-weight: 800;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--primary-dark);
    background: var(--primary-soft);
    border-left: 4px solid var(--primary);
    padding: 8px 12px;
    border-radius: 0 10px 10px 0;
    margin: 20px 0 12px 0;
}

/* ── Caja ética ── */
.ethical-box {
    background: #FFF8EC;
    border: 1px solid #F3D7A0;
    border-left: 5px solid var(--accent);
    border-radius: 16px;
    padding: 15px 18px;
    margin: 12px 0;
    font-size: 0.88rem;
    color: #7B5A1D;
    line-height: 1.6;
}

.ethical-box b {
    color: #8A6218;
}

/* ── Pipeline steps ── */
.pipeline-step {
    display: flex;
    align-items: flex-start;
    gap: 16px;
    background: var(--card);
    border-radius: 18px;
    padding: 16px 20px;
    border: 1px solid var(--border);
    box-shadow: 0 6px 16px rgba(22, 19, 60, 0.05);
    margin-bottom: 10px;
}

.step-num {
    background: linear-gradient(135deg, var(--primary) 0%, var(--primary-dark) 100%);
    color: white;
    border-radius: 50%;
    width: 30px;
    height: 30px;
    min-width: 30px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 0.80rem;
    font-weight: 700;
    box-shadow: 0 6px 14px rgba(108, 99, 255, 0.25);
}

.step-title {
    font-weight: 700;
    font-size: 0.92rem;
    color: var(--text);
    margin-bottom: 2px;
}

.step-desc {
    font-size: 0.83rem;
    color: var(--text-soft);
    line-height: 1.55;
}

/* ── Hallazgos ── */
.finding-card {
    background: var(--card);
    border-radius: 18px;
    padding: 16px 20px;
    border-left: 4px solid var(--primary);
    margin-bottom: 10px;
    border: 1px solid var(--border);
    box-shadow: 0 6px 16px rgba(22, 19, 60, 0.05);
    font-size: 0.9rem;
    color: #4A465F;
    line-height: 1.6;
}

.finding-card b {
    color: var(--primary-dark);
}

/* ── Métricas ── */
div[data-testid="stMetricValue"] {
    font-size: 1.5rem !important;
}

/* ── Dataframes ── */
div[data-testid="stDataFrame"] {
    border-radius: 16px;
    overflow: hidden;
    border: 1px solid var(--border);
}

/* ── Botones ── */
.stButton > button,
div[data-testid="stFormSubmitButton"] button {
    border-radius: 14px !important;
    border: none !important;
    background: linear-gradient(135deg, #6C63FF 0%, #5B4FE8 100%) !important;
    color: white !important;
    font-weight: 700 !important;
    box-shadow: 0 10px 18px rgba(108, 99, 255, 0.20) !important;
}

.stButton > button:hover,
div[data-testid="stFormSubmitButton"] button:hover {
    filter: brightness(1.03);
}
</style>
""", unsafe_allow_html=True)



# ── Recursos ─────────────────────────────────────────────────────────────────────
@st.cache_resource
def cargar_modelo():
    try:
        modelo = joblib.load(RUTA_PKL)
        with open(RUTA_META, "r", encoding="utf-8") as f:
            meta = json.load(f)
        return modelo, meta
    except FileNotFoundError:
        st.error("Modelo no encontrado. Ejecuta notebooks/03_modelado.ipynb o src/ml/entrenar_modelo.py")
        st.stop()


@st.cache_data
def cargar_datos():
    ruta = RUTA_DS if RUTA_DS.exists() else RUTA_TR
    try:
        return pd.read_csv(ruta)
    except FileNotFoundError:
        st.error(f"Dataset no encontrado: {ruta}")
        st.stop()


# ── Helpers HTML ─────────────────────────────────────────────────────────────────
def kpi(label, value, color, icon="", sub=""):
    sub_h = f'<p class="kpi-sub">{sub}</p>' if sub else ""
    return (
        f'<div class="kpi-card" style="border-top-color:{color}">'
        f'<span class="kpi-icon">{icon}</span>'
        f'<p class="kpi-label">{label}</p>'
        f'<p class="kpi-value" style="color:{color}">{value}</p>'
        f'{sub_h}</div>'
    )


def page_header(titulo, subtitulo=""):
    st.markdown(
        f'<div class="page-header"><h1>{titulo}</h1><p>{subtitulo}</p></div>',
        unsafe_allow_html=True,
    )


def sec_label(texto):
    st.markdown(f'<p class="sec-label">{texto}</p>', unsafe_allow_html=True)


def card_html(contenido, titulo=""):
    t = f'<p class="card-title">{titulo}</p>' if titulo else ""
    st.markdown(f'<div class="card">{t}{contenido}</div>', unsafe_allow_html=True)


# ── SECCIONES ────────────────────────────────────────────────────────────────────

def sec_inicio(meta):
    page_header(
        "FinBalance",
        "Clasificador de fragilidad financiera — Encuesta de Demanda Financiera 2022",
    )

    n_modelado = meta.get("n_train", 0) + meta.get("n_test", 0)
    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Registros para modelado", f"{n_modelado:,}", C_PRIMARY, "🗂️", f"EDF 2022 · {5610 - n_modelado} NS/NR excluidos"), unsafe_allow_html=True)
    c2.markdown(kpi("Variables del modelo", str(meta.get("n_features", 40)), C_ACCENT_CYAN, "📐", "Pipeline de EDA y codificación"), unsafe_allow_html=True)
    c3.markdown(kpi("Clases a predecir", "3", C_ACCENT, "🎯", "Baja · Media · Alta"), unsafe_allow_html=True)
    c4.markdown(kpi("F1 macro (test)", f"{meta.get('valor_metrica',0):.3f}", C_PRIMARY, "📊", f"Accuracy {meta.get('accuracy',0):.3f}"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_a, col_b = st.columns([3, 2])

    with col_a:
        st.markdown("""
        <div class="card">
        <p class="card-title">Sobre el proyecto</p>
        <p style="font-size:0.92rem;color:#4A465F;line-height:1.7">
        <b>FinBalance</b> predice el nivel de fragilidad financiera de un hogar colombiano
        a partir de características socioeconómicas, hábitos financieros y variables de percepción personal.
        El modelo fue entrenado sobre los <b>microdatos de la EDF 2022</b> de
        Banca de las Oportunidades (programa del Gobierno Nacional, administrado por Bancóldex).
        <br><br>
        La <b>variable objetivo</b> proviene de la pregunta P407 de la encuesta:
        <em>¿Cuánto tiempo podría sostenerse su hogar sin recibir ingresos?</em>
        Las respuestas se agruparon en tres niveles de fragilidad:
        </p>
        <div style="display:flex;gap:10px;flex-wrap:wrap;margin-top:12px">
          <span class="badge badge-alta">Alta — menos de 1 mes</span>
          <span class="badge badge-media">Media — 1 a 5 meses</span>
          <span class="badge badge-baja">Baja — 6 meses o más</span>
        </div>
        </div>
        """, unsafe_allow_html=True)

    with col_b:
        st.markdown("""
        <div class="card">
        <p class="card-title">Guía de navegación</p>
        """, unsafe_allow_html=True)

        items = [
            ("📊", "Dataset", "Estadísticas y muestra del conjunto de datos"),
            ("🔍", "Análisis exploratorio", "Visualizaciones interactivas con filtros"),
            ("🤖", "Modelo", "Pipeline y variables del modelo final"),
            ("📈", "Métricas", "F1, accuracy, AUC y reporte por clase"),
            ("🎯", "Predicción", "Formulario para clasificar un hogar"),
            ("✅", "Conclusiones", "Hallazgos, limitaciones y ética"),
        ]
        html_items = "".join(
            f'<div style="display:flex;align-items:center;gap:10px;padding:7px 0;border-bottom:1px solid #ECEAF4">'
            f'<span style="font-size:1.1rem">{ic}</span>'
            f'<div><b style="font-size:0.85rem;color:#26233A">{nm}</b>'
            f'<span style="font-size:0.78rem;color:#9B97B4;display:block">{desc}</span></div></div>'
            for ic, nm, desc in items
        )
        st.markdown(html_items + "</div>", unsafe_allow_html=True)


def sec_dataset(df):
    page_header("Dataset", "Encuesta de Demanda Financiera 2022 — Banca de las Oportunidades / Bancóldex")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("Filas totales", f"{len(df):,}", C_AZUL, "📋"), unsafe_allow_html=True)
    c2.markdown(kpi("Columnas", str(df.shape[1]), C_TEAL, "📐"), unsafe_allow_html=True)
    c3.markdown(kpi("Valores nulos", str(df.isnull().sum().sum()), C_SUCCESS, "✓", "Tras el preprocesamiento"), unsafe_allow_html=True)
    c4.markdown(kpi("Registros excluidos", str(5610 - len(df)), C_ACCENT, "⚠️", "NS/NR en la variable objetivo"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns([3, 2])

    with col_l:
        sec_label("Muestra del dataset procesado")
        st.dataframe(df.head(15), use_container_width=True, height=360)

    with col_r:
        sec_label("Estadísticas descriptivas")
        st.dataframe(df.describe().round(2), use_container_width=True, height=360)


def sec_eda(df):
    page_header("Análisis exploratorio", "Visualizaciones interactivas del conjunto de entrenamiento")

    # Filtro
    col_f1, col_f2, _ = st.columns([1, 1, 3])
    filtro_genero  = col_f1.selectbox("Filtrar por género",  ["Todos", "Femenino", "Masculino"])
    filtro_estrato = col_f2.selectbox("Filtrar por estrato", ["Todos", 1, 2, 3, 4, 5, 6])

    dfe = df.copy()
    if "fragilidad_label" in dfe.columns:
        dfe["fragilidad"] = dfe["fragilidad_label"].map(LABEL_MAP)
    if filtro_genero == "Masculino":
        dfe = dfe[dfe["genero_Masculino"] == 1]
    elif filtro_genero == "Femenino":
        dfe = dfe[dfe["genero_Masculino"] == 0]
    if filtro_estrato != "Todos":
        dfe = dfe[dfe["estrato"] == filtro_estrato]

    st.caption(f"Registros seleccionados: **{len(dfe):,}** de {len(df):,}")
    st.markdown("<br>", unsafe_allow_html=True)

    # ── Fila 1: distribución + ingresos ─────────────────────────────────────────
    col1, col2 = st.columns(2)

    with col1:
        conteo = dfe["fragilidad"].value_counts().reindex(["Alta", "Media", "Baja"]).fillna(0)
        fig = go.Figure(go.Bar(
            x=conteo.index.tolist(), y=conteo.values.tolist(),
            marker=dict(
                color=[C_ROJO, C_AMBER, C_VERDE],
                cornerradius=8,
                line=dict(width=0),
            ),
            text=[f"{int(v):,}<br>({v/len(dfe)*100:.1f}%)" if len(dfe) > 0 else "0" for v in conteo.values],
            textposition="outside",
        ))
        fig.update_layout(
            title=dict(text="Distribución de fragilidad financiera", font=dict(size=13, color=C_TEXT)),
            xaxis=dict(title="", showgrid=False),
            yaxis=dict(title="Hogares", gridcolor="#ECEAF4"),
            height=300, margin=dict(t=45, b=10, l=10, r=10),
            plot_bgcolor="white", paper_bgcolor="white",
            showlegend=False,
        )
        st.plotly_chart(fig, use_container_width=True)

    with col2:
        fig2 = go.Figure()
        for clase, color in [("Alta", C_ROJO), ("Media", C_AMBER), ("Baja", C_VERDE)]:
            s = dfe[dfe["fragilidad"] == clase]["rango_ingresos"].dropna()
            fig2.add_trace(go.Box(
                y=s, name=clase, marker_color=color,
                boxmean="sd", line=dict(width=1.5),
            ))
        fig2.update_layout(
            title=dict(text="Ingresos por nivel de fragilidad", font=dict(size=13, color=C_TEXT)),
            yaxis=dict(title="Rango de ingresos (1 = mínimo · 10 = máximo)", gridcolor="#ECEAF4", dtick=1),
            height=300, margin=dict(t=45, b=10, l=10, r=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(title="Fragilidad", orientation="h", y=1.12),
        )
        st.plotly_chart(fig2, use_container_width=True)

    # ── Fila 2: percepciones + hábitos ──────────────────────────────────────────
    col3, col4 = st.columns(2)

    with col3:
        cols_p = ["perc_camino_obj","perc_deuda_manejable","perc_control_sit"]
        labs_p = ["Camino a objetivos","Deuda manejable","Control de la situación"]
        fig3 = go.Figure()
        for clase, color in [("Alta", C_ROJO), ("Media", C_AMBER), ("Baja", C_VERDE)]:
            sub = dfe[dfe["fragilidad"] == clase]
            if len(sub):
                fig3.add_trace(go.Bar(
                    name=clase, x=labs_p,
                    y=[sub[c].mean() for c in cols_p],
                    marker_color=color, opacity=0.85,
                ))
        fig3.update_layout(
            barmode="group",
            title=dict(text="Percepciones financieras promedio (1–5)", font=dict(size=13, color=C_TEXT)),
            yaxis=dict(title="Promedio", range=[0, 5.5], gridcolor="#ECEAF4"),
            height=300, margin=dict(t=45, b=10, l=10, r=10),
            plot_bgcolor="white", paper_bgcolor="white",
            legend=dict(title="Fragilidad", orientation="h", y=1.12),
        )
        st.plotly_chart(fig3, use_container_width=True)

    with col4:
        if len(dfe):
            hab_cols = ["comp_tiene_plan", "prod_cuenta_ahorro"]
            hab_pct = dfe.groupby("fragilidad")[hab_cols].mean().reindex(["Alta","Media","Baja"]) * 100
            fig4 = go.Figure()
            for col_h, label, opacity, pattern in [
                ("comp_tiene_plan",    "Tiene plan financiero",  0.85, ""),
                ("prod_cuenta_ahorro", "Tiene cuenta de ahorro", 0.4,  "/"),
            ]:
                fig4.add_trace(go.Bar(
                    name=label,
                    x=hab_pct.index.tolist(),
                    y=hab_pct[col_h].tolist(),
                    marker=dict(
                        color=[C_ROJO, C_AMBER, C_VERDE],
                        opacity=opacity,
                        pattern=dict(shape=pattern, size=5, fgcolor="rgba(0,0,0,0.25)"),
                        line=dict(width=0),
                    ),
                    text=[f"{v:.0f}%" for v in hab_pct[col_h]],
                    textposition="outside",
                ))
            fig4.update_layout(
                barmode="group",
                title=dict(text="% con plan financiero y cuenta de ahorro", font=dict(size=13, color=C_TEXT)),
                yaxis=dict(title="%", range=[0, 110], gridcolor="#ECEAF4"),
                height=300, margin=dict(t=45, b=10, l=10, r=10),
                plot_bgcolor="white", paper_bgcolor="white",
                legend=dict(orientation="h", y=1.12),
            )
            st.plotly_chart(fig4, use_container_width=True)


def sec_modelo(meta):
    page_header("Modelo de machine learning", "Gradient Boosting Classifier — pipeline de scikit-learn")

    col_a, col_b = st.columns([3, 2])

    with col_a:
        sec_label("Pipeline de entrenamiento")

        def _paso(num, titulo, desc):
            st.markdown(
                f'<div class="pipeline-step">'
                f'<div class="step-num">{num}</div>'
                f'<div><p class="step-title">{titulo}</p><p class="step-desc">{desc}</p></div>'
                f'</div>',
                unsafe_allow_html=True,
            )

        def _resultado_inline(texto, color):
            st.markdown(
                f'<p style="font-size:0.79rem;font-weight:700;color:{color};'
                f'margin:-6px 0 8px 46px">▶ {texto}</p>',
                unsafe_allow_html=True,
            )

        # ── Paso 1 ───────────────────────────────────────────────────────────
        _paso("1", "Selección de variables",
              f"{meta.get('n_features', 40)} features resultantes del pipeline de limpieza, "
              "codificación ordinal, binaria y one-hot encoding (notebook 02).")
        with st.expander("Ver las 40 variables de entrada"):
            vars_entrada = meta.get("variables_entrada", [])
            grupos = {
                "Productos financieros": [v for v in vars_entrada if v.startswith("prod_")],
                "Fuentes de ingreso":    [v for v in vars_entrada if v.startswith("ing_")],
                "Gastos":                [v for v in vars_entrada if v.startswith("gasto_")],
                "Comportamiento":        [v for v in vars_entrada if v.startswith("comp_") or v.startswith("hab_")],
                "Percepciones":          [v for v in vars_entrada if v.startswith("perc_")],
                "Sociodemográficas":     [v for v in vars_entrada if not any(
                    v.startswith(p) for p in ("prod_","ing_","gasto_","comp_","hab_","perc_"))],
            }
            for grupo, vs in grupos.items():
                if vs:
                    tags = " ".join(
                        f'<span style="background:#EEEAFE;color:#5B4FE8;font-size:0.72rem;'
                        f'padding:2px 8px;border-radius:999px;margin:2px;display:inline-block">{v}</span>'
                        for v in vs
                    )
                    st.markdown(
                        f'<p style="font-size:0.75rem;font-weight:700;color:#6F6B86;'
                        f'margin:8px 0 4px">{grupo}</p>{tags}',
                        unsafe_allow_html=True,
                    )

        # ── Paso 2 ───────────────────────────────────────────────────────────
        _paso("2", "Codificación",
              "Ordinal (nivel educativo 0–6, estrato 1–6), binaria (ingresos/gastos) "
              "y one-hot encoding (región, ruralidad).")
        with st.expander("Ver ejemplo de codificación por tipo"):
            st.code(
                "# Ordinal — nivel educativo\n"
                "mapa_edu = {'Ninguno':0,'Primaria':1,'Secundaria':2,\n"
                "            'Técnico':3,'Tecnólogo':4,'Universitarios':5,'Posgrado':6}\n"
                "df['nivel_educativo'] = df['P204'].map(mapa_edu)\n\n"
                "# Binaria — fuentes de ingreso\n"
                "df['ing_salario'] = (df['P301_1'] == 1).astype(int)\n\n"
                "# One-hot — región geográfica\n"
                "region_dummies = pd.get_dummies(df['region'], prefix='region')\n"
                "df = pd.concat([df, region_dummies], axis=1)",
                language="python",
            )

        # ── Paso 3 ───────────────────────────────────────────────────────────
        _paso("3", "StandardScaler",
              "Escalado media=0, std=1. Ajustado solo sobre train para evitar data leakage.")
        with st.expander("Ver aplicación del scaler"):
            st.code(
                "from sklearn.preprocessing import StandardScaler\n\n"
                "scaler = StandardScaler()\n"
                "X_train_sc = scaler.fit_transform(X_train)  # fit + transform\n"
                "X_test_sc  = scaler.transform(X_test)       # solo transform\n\n"
                "# ⚠ Nunca scaler.fit_transform(X_test)\n"
                "# — contamina el modelo con información del test set.",
                language="python",
            )

        # ── Paso 4 ───────────────────────────────────────────────────────────
        _paso("4", "GradientBoostingClassifier",
              f"n_estimators=200, max_depth=4, learning_rate=0.1, "
              f"random_state=42, sklearn {meta.get('sklearn_version', '—')}")
        with st.expander("Ver parámetros del modelo"):
            st.code(
                "from sklearn.ensemble import GradientBoostingClassifier\n\n"
                "modelo = GradientBoostingClassifier(\n"
                "    n_estimators  = 200,\n"
                "    max_depth     = 4,\n"
                "    learning_rate = 0.1,\n"
                "    random_state  = 42,\n"
                ")\n\n"
                f"# sklearn version: {meta.get('sklearn_version', '—')}\n"
                f"# Semilla fija: {meta.get('semilla', 42)}",
                language="python",
            )

        # ── Paso 5 ───────────────────────────────────────────────────────────
        cv_m = meta.get("cv_f1_macro_mean", 0)
        cv_s = meta.get("cv_f1_macro_std", 0)
        _paso("5", "Validación cruzada",
              "StratifiedKFold de 5 folds sobre train para la selección de hiperparámetros.")
        _resultado_inline(f"CV F1 macro (5 folds): {cv_m:.3f} ± {cv_s:.3f}", C_SUCCESS)

        # ── Paso 6 ───────────────────────────────────────────────────────────
        _paso("6", "GridSearchCV",
              "Grilla de 3×3×3 = 27 combinaciones × 5 folds = 135 entrenamientos.")
        with st.expander("Ver grilla de hiperparámetros"):
            st.code(
                "param_grid = {\n"
                "    'n_estimators':  [100, 200, 300],\n"
                "    'max_depth':     [3, 4, 5],\n"
                "    'learning_rate': [0.05, 0.1, 0.2],\n"
                "}\n"
                "# 3 × 3 × 3 = 27 combinaciones\n"
                "# × 5 folds = 135 entrenamientos en total\n\n"
                "gs = GridSearchCV(modelo, param_grid,\n"
                "                  scoring='f1_macro', cv=5)\n"
                "gs.fit(X_train, y_train)",
                language="python",
            )

        # ── Paso 7 ───────────────────────────────────────────────────────────
        _paso("7", "Balanceo de clases",
              "Se evaluaron 5 estrategias: class_weight, SMOTE y Balanced Random Forest.")
        _resultado_inline(
            "Ninguna estrategia mejoró el F1 macro global → se mantiene el modelo base sin ajuste",
            C_WARNING,
        )

        # ── Paso 8 ───────────────────────────────────────────────────────────
        _paso("8", "Evaluación final",
              "Una sola vez sobre test (holdout del 20 %), nunca visto durante el ajuste.")
        _resultado_inline(
            f"F1 macro = {meta.get('valor_metrica', 0):.3f}  ·  "
            f"Accuracy = {meta.get('accuracy', 0):.3f}  ·  "
            f"AUC OvR = {meta.get('auc_macro_ovr', 0):.3f}",
            C_PRIMARY,
        )

    with col_b:
        sec_label("Modelos comparados")
        modelos_comp = [
            ("DummyClassifier", "Baseline trivial", C_MUTED),
            ("Logistic Regression", "Referencia lineal", C_TEAL),
            ("Decision Tree", "Árbol simple", C_ACCENT),
            ("Random Forest", "F1=0.507 (comparado)", C_MUTED),
            ("Gradient Boosting", f"✓ Modelo final  F1={meta.get('valor_metrica', 0):.3f}", C_PRIMARY),
        ]
        for nombre, rol, color in modelos_comp:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;align-items:center;'
                f'padding:10px 14px;background:white;border-radius:10px;margin-bottom:8px;'
                f'box-shadow:0 1px 4px rgba(0,0,0,0.05);border-left:4px solid {color}">'
                f'<span style="font-size:0.88rem;font-weight:600;color:#26233A">{nombre}</span>'
                f'<span style="font-size:0.75rem;color:{color};font-weight:600">{rol}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )

        # ── Gráfica dentro de col_b ──────────────────────────────────────────
        comp = meta.get("comparacion_modelos", [])
        if comp:
            sec_label("Comparación sobre el conjunto de test")

            nombres = [m["nombre"]  for m in comp]
            f1s     = [m["f1_macro"] for m in comp]
            accs    = [m["accuracy"] for m in comp]
            baseline_f1 = meta.get("classification_report", {}).get("macro avg", {}).get("f1-score", 0)
            _rep_c = meta.get("classification_report", {})
            _nte   = meta.get("n_test", 1)
            baseline_acc = max(
                _rep_c.get("1", {}).get("support", 0),
                _rep_c.get("2", {}).get("support", 0),
                _rep_c.get("3", {}).get("support", 0),
            ) / _nte
            ganador = nombres[-1]
            colores = [C_PRIMARY if n == ganador else "#D1CEEF" for n in nombres]

            fig_comp = make_subplots(
                rows=2, cols=1,
                subplot_titles=("F1 macro", "Accuracy"),
                vertical_spacing=0.18,
            )
            for row_i, (vals, tip, bl) in enumerate([
                (f1s,  "F1 macro",  baseline_f1),
                (accs, "Accuracy",  baseline_acc),
            ], start=1):
                fig_comp.add_trace(
                    go.Bar(
                        y=nombres, x=vals, orientation="h",
                        marker=dict(color=colores, line=dict(width=0)),
                        text=[f"{v:.3f}" for v in vals],
                        textposition="outside",
                        showlegend=False,
                        hovertemplate=f"<b>%{{y}}</b><br>{tip}: %{{x:.3f}}<extra></extra>",
                    ),
                    row=row_i, col=1,
                )
                fig_comp.add_vline(
                    x=bl, line_dash="dash", line_color="#9B97B4", line_width=1.2,
                    annotation_text=f"Baseline ({bl:.3f})",
                    annotation_position="top right",
                    annotation_font=dict(size=9, color="#9B97B4"),
                    row=row_i, col=1,
                )
                fig_comp.update_xaxes(range=[0, 0.75], gridcolor="#ECEAF4", row=row_i, col=1)
                fig_comp.update_yaxes(showgrid=False, row=row_i, col=1)

            fig_comp.update_layout(
                height=420,
                plot_bgcolor="white", paper_bgcolor="white",
                font=dict(color=C_TEXT, family="Arial", size=11),
                margin=dict(t=30, b=10, l=10, r=55),
            )
            st.plotly_chart(fig_comp, use_container_width=True)

    # ── Variable objetivo + Experimento ─────────────────────────────────────────
    col_c, col_d = st.columns(2)

    with col_c:
        sec_label("Variable objetivo")
        _report = meta.get("classification_report", {})
        _n_test = meta.get("n_test", 1)
        _pct_alta  = _report.get("3", {}).get("support", 0) / _n_test * 100
        _pct_media = _report.get("2", {}).get("support", 0) / _n_test * 100
        _pct_baja  = _report.get("1", {}).get("support", 0) / _n_test * 100
        st.markdown(
            f'<div class="card" style="padding:16px">'
            f'<p style="font-size:0.82rem;color:#6F6B86;line-height:1.6">'
            f'<b>P407</b> — ¿Cuánto tiempo podría sostenerse su hogar sin recibir ingresos?'
            f'<br><br>'
            f'<span class="badge badge-alta">Alta</span> &lt; 1 mes ({_pct_alta:.1f}%)<br>'
            f'<span class="badge badge-media">Media</span> 1–5 meses ({_pct_media:.1f}%)<br>'
            f'<span class="badge badge-baja">Baja</span> ≥ 6 meses ({_pct_baja:.1f}%)'
            f'</p></div>',
            unsafe_allow_html=True,
        )

    with col_d:
        sec_label("Experimento con otras variables")
        exp = meta.get("experimento_20_variables", {})
        f1_exp  = exp.get("f1_macro", 0.497)
        n_exp   = exp.get("n_features", 20)
        f1_full = meta.get("valor_metrica", 0)
        n_full  = meta.get("n_features", 40)
        baseline_f1 = meta.get("classification_report", {}).get("macro avg", {}).get("f1-score", 0)

        etiquetas = [
            f"Selección alternativa\n({n_exp} variables)",
            f"Pipeline completo\n({n_full} variables)",
        ]
        valores_f1 = [f1_exp, f1_full]
        col_exp = ["#D1CEEF", C_PRIMARY]

        fig_exp = go.Figure(go.Bar(
            y=etiquetas,
            x=valores_f1,
            orientation="h",
            marker=dict(color=col_exp, line=dict(width=0)),
            text=[f"{v:.3f}" for v in valores_f1],
            textposition="outside",
            hovertemplate="<b>%{y}</b><br>F1 macro: %{x:.3f}<extra></extra>",
        ))
        fig_exp.add_vline(
            x=baseline_f1, line_dash="dash", line_color="#9B97B4", line_width=1.5,
            annotation_text=f"Baseline ({baseline_f1:.3f})",
            annotation_position="top right",
            annotation_font=dict(size=10, color="#9B97B4"),
        )
        fig_exp.update_layout(
            title=dict(text="F1 macro — comparación de selección de variables",
                       font=dict(size=12, color=C_TEXT)),
            xaxis=dict(range=[0, 0.7], gridcolor="#ECEAF4", title="F1 macro"),
            yaxis=dict(showgrid=False),
            height=210,
            plot_bgcolor="white",
            paper_bgcolor="white",
            font=dict(color=C_TEXT, family="Arial"),
            margin=dict(t=45, b=20, l=10, r=60),
        )
        st.plotly_chart(fig_exp, use_container_width=True)
        st.caption(
            f"El pipeline de {n_full} features supera la selección de {n_exp} variables "
            f"en {(f1_full - f1_exp):.3f} puntos de F1 macro."
        )


def sec_metricas(meta):
    page_header("Métricas del modelo", f"{meta.get('modelo','—')} · Evaluado sobre test (holdout del 20 %)")

    c1, c2, c3, c4 = st.columns(4)
    c1.markdown(kpi("F1 macro", f"{meta.get('valor_metrica',0):.3f}", C_PRIMARY, "🎯", "Métrica principal"), unsafe_allow_html=True)
    c2.markdown(kpi("Accuracy", f"{meta.get('accuracy',0):.3f}", C_ACCENT_CYAN, "✓"), unsafe_allow_html=True)
    c3.markdown(kpi("Precisión macro", f"{meta.get('precision_macro',0):.3f}", C_ACCENT, "📌"), unsafe_allow_html=True)
    c4.markdown(kpi("Recall macro", f"{meta.get('recall_macro',0):.3f}", C_SUCCESS, "📡"), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)
    col_l, col_r = st.columns(2)

    with col_l:
        sec_label("Reporte por clase")
        report = meta.get("classification_report", {})
        filas = []
        for kid, knm in [(1,"Baja"),(2,"Media"),(3,"Alta")]:
            d = report.get(str(kid), report.get(knm.lower(), {}))
            if d:
                filas.append({
                    "Clase": knm,
                    "Precision": round(d.get("precision",0), 3),
                    "Recall":    round(d.get("recall",0), 3),
                    "F1-score":  round(d.get("f1-score",0), 3),
                    "Soporte":   int(d.get("support",0)),
                })
        if filas:
            df_rep = pd.DataFrame(filas)
            st.dataframe(df_rep, use_container_width=True, hide_index=True, height=175)
        else:
            st.info("Reporte por clase no disponible.")

        cv_m = meta.get("cv_f1_macro_mean")
        cv_s = meta.get("cv_f1_macro_std")
        n_tr = meta.get("n_train","—")
        n_te = meta.get("n_test","—")
        if cv_m:
            st.markdown(
                f'<div class="card" style="padding:14px 18px">'
                f'<p style="font-size:0.82rem;color:#6F6B86;line-height:1.8;margin:0">'
                f'CV F1 macro (5 folds): <b>{cv_m:.3f} ± {cv_s:.3f}</b><br>'
                f'Train: <b>{n_tr:,}</b> registros &nbsp;|&nbsp; Test: <b>{n_te:,}</b> registros<br>'
                f'AUC macro OvR: <b>{meta.get("auc_macro_ovr", "—")}</b>'
                f'</p></div>',
                unsafe_allow_html=True,
            )

    with col_r:
        sec_label("Interpretación de la métrica")
        f1  = meta.get("valor_metrica", 0)
        auc = meta.get("auc_macro_ovr", 0)
        _rep   = meta.get("classification_report", {})
        _n_te  = meta.get("n_test", 1)
        _sup_baja  = int(_rep.get("1", {}).get("support", 0))
        _sup_media = int(_rep.get("2", {}).get("support", 0))
        _pct_baja_m  = _sup_baja  / _n_te * 100
        _pct_media_m = _sup_media / _n_te * 100
        # F1 macro baseline: siempre predice la clase más frecuente
        _p_med = _sup_media / _n_te
        _f1_base = (2 * _p_med / (_p_med + 1)) / 3
        st.markdown(
            f'<div class="card" style="padding:18px 20px">'
            f'<p style="font-size:0.88rem;color:#4A465F;line-height:1.7">'
            f'El <b>F1-score macro = {f1:.3f}</b> indica que el modelo promedia precisión y recall '
            f'en las tres clases con igual peso. Un clasificador aleatorio obtendría '
            f'F1 macro ≈ 0.33 en tres clases equiprobables; el modelo supera ese piso '
            f'(F1 baseline = {_f1_base:.3f} prediciendo siempre la clase más frecuente).'
            f'<br><br>'
            f'Se usa F1 macro porque la clase <b>Baja</b> representa solo el {_pct_baja_m:.1f}% del conjunto de prueba. '
            f'La accuracy sola sería engañosa: un modelo que prediga siempre "Media" alcanzaría '
            f'{_pct_media_m:.1f}% de accuracy pero tendría F1 macro = {_f1_base:.3f}.'
            f'<br><br>'
            f'El <b>AUC macro OvR = {auc:.3f}</b> indica que el modelo discrimina razonablemente '
            f'entre las clases en términos de probabilidades.'
            f'</p></div>',
            unsafe_allow_html=True,
        )

        sec_label("Balanceo de clases evaluado")
        estrategias = [
            ("Baseline (sin ajuste)", "✓ Seleccionado", C_PRIMARY),
            ("class_weight='balanced'", "Mejora Baja, reduce macro", C_MUTED),
            ("class_weight='balanced_subsample'", "Resultado similar", C_MUTED),
            ("SMOTE", "Sin mejora significativa", C_MUTED),
            ("Balanced Random Forest", "Sin mejora significativa", C_MUTED),
        ]
        for nombre, resultado, color in estrategias:
            st.markdown(
                f'<div style="display:flex;justify-content:space-between;padding:8px 12px;'
                f'background:white;border-radius:8px;margin-bottom:6px;'
                f'box-shadow:0 1px 3px rgba(0,0,0,0.05);border-left:3px solid {color}">'
                f'<span style="font-size:0.8rem;color:#4A465F">{nombre}</span>'
                f'<span style="font-size:0.75rem;color:{color};font-weight:600">{resultado}</span>'
                f'</div>',
                unsafe_allow_html=True,
            )


def _form() -> dict:
    vals = {}

    st.markdown('<p class="form-sec">Características sociodemográficas</p>', unsafe_allow_html=True)
    c1, c2, c3, c4 = st.columns(4)
    vals["edad"]             = c1.number_input("Edad", 18, 99, 35)
    vals["nivel_educativo"]  = MAPA_EDU[c2.selectbox("Nivel educativo", list(MAPA_EDU), index=2)]
    vals["estrato"]          = c3.selectbox("Estrato", [1,2,3,4,5,6], index=1)
    vals["genero_Masculino"] = int(c4.selectbox("Género", ["Femenino","Masculino"]) == "Masculino")

    c5, c6 = st.columns(2)
    ruralidad_sel = c5.selectbox("Tipo de zona", RURALIDAD_OPTS)
    region_sel    = c6.selectbox("Region", REGION_OPTS)
    vals["ruralidad_Intermedio"]     = int(ruralidad_sel == "Intermedio")
    vals["ruralidad_Rural"]          = int(ruralidad_sel == "Rural")
    vals["ruralidad_Rural disperso"] = int(ruralidad_sel == "Rural disperso")
    vals["region_Centro Oriente"]    = int(region_sel == "Centro Oriente")
    vals["region_Centro Sur"]        = int(region_sel == "Centro Sur")
    vals["region_Eje cafetero"]      = int(region_sel == "Eje cafetero")
    vals["region_Llano"]             = int(region_sel == "Llano")
    vals["region_Pacífico"]          = int(region_sel == "Pacífico")

    st.markdown('<p class="form-sec">Ingresos y gastos del hogar</p>', unsafe_allow_html=True)
    c7, c8 = st.columns(2)
    vals["rango_ingresos"] = RANGOS_ING[c7.selectbox("Rango de ingresos mensuales", list(RANGOS_ING), index=3)]
    vals["rango_gastos"]   = RANGOS_ING[c8.selectbox("Rango de gastos mensuales", list(RANGOS_ING), index=3)]

    st.markdown('<p class="form-sec">Fuentes de ingreso del hogar</p>', unsafe_allow_html=True)
    c9, c10, c11, c12 = st.columns(4)
    vals["ing_salario"]        = int(c9.checkbox("Salario / sueldo"))
    vals["ing_pension"]        = int(c10.checkbox("Pension / jubilacion"))
    vals["ing_arriendos"]      = int(c11.checkbox("Arriendos"))
    vals["ing_honorarios"]     = int(c12.checkbox("Honorarios / consultoria"))
    c13, c14, c15, c16 = st.columns(4)
    vals["ing_ventas"]         = int(c13.checkbox("Ventas / negocio propio"))
    vals["ing_subsidios"]      = int(c14.checkbox("Subsidios del Estado"))
    vals["ing_remesas"]        = int(c15.checkbox("Remesas del exterior"))
    vals["ing_ayuda_familiar"] = int(c16.checkbox("Ayuda de familiares"))

    st.markdown('<p class="form-sec">Gastos del hogar</p>', unsafe_allow_html=True)
    c17, c18, c19 = st.columns(3)
    vals["gasto_arriendo"]   = int(c17.checkbox("Paga arriendo / vivienda"))
    vals["gasto_servicios"]  = int(c18.checkbox("Paga servicios públicos"))
    vals["gasto_seg_social"] = int(c19.checkbox("Paga seguridad social / salud"))

    st.markdown('<p class="form-sec">Productos financieros</p>', unsafe_allow_html=True)
    c20, c21, c22, c23, c24, c25 = st.columns(6)
    vals["prod_cuenta_ahorro"]  = int(c20.checkbox("Cuenta de ahorro"))
    vals["prod_tarjeta_debito"] = int(c21.checkbox("Tarjeta débito"))
    vals["prod_monedero"]       = int(c22.checkbox("Monedero digital"))
    vals["prod_cdt"]            = int(c23.checkbox("CDT"))
    vals["prod_fondo_inv"]      = int(c24.checkbox("Fondo de inversión"))
    vals["prod_fondo_emp"]      = int(c25.checkbox("Fondo de empleados"))

    st.markdown('<p class="form-sec">Comportamiento financiero</p>', unsafe_allow_html=True)
    c26, c27 = st.columns(2)
    vals["comp_atraso_pagos"]        = c26.slider("Frecuencia de atrasos en pagos (1=Nunca · 5=Siempre)", 1, 5, 1)
    vals["comp_deuda_mayor_activos"] = c27.slider("Las deudas superan los activos (1=Desacuerdo · 5=Acuerdo)", 1, 5, 1)
    c28, c29, c30, c31 = st.columns(4)
    vals["comp_tiene_plan"]      = int(c28.checkbox("Tiene plan financiero formal"))
    vals["hab_encargado_gastos"] = int(c29.checkbox("Responsable de gastos del hogar"))
    vals["hab_encargado_presup"] = int(c30.checkbox("Responsable del presupuesto"))
    vals["hab_usa_app_bancaria"] = int(c31.checkbox("Usa app bancaria o medios de pago digitales"))

    st.markdown('<p class="form-sec">Percepciones financieras (1 = Totalmente en desacuerdo · 5 = Totalmente de acuerdo)</p>', unsafe_allow_html=True)
    c32, c33, c34 = st.columns(3)
    vals["perc_camino_obj"]      = c32.slider("Va por buen camino hacia sus objetivos", 1, 5, 3)
    vals["perc_deuda_manejable"] = c33.slider("Sus deudas actuales son manejables", 1, 5, 3)
    vals["perc_control_sit"]     = c34.slider("Control sobre su situación financiera", 1, 5, 4)

    return vals


def _resultado(pred: int, proba: np.ndarray):
    c = BG_CLASE[pred]
    st.markdown(
        f'<div class="res-card" style="background:{c["bg"]};border-color:{c["borde"]}">'
        f'<p class="res-eyebrow" style="color:{c["texto"]}">Nivel de fragilidad predicho</p>'
        f'<p class="res-class"  style="color:{c["borde"]}">{CLASES[pred]}</p>'
        f'<p class="res-desc"   style="color:{c["texto"]}">{DESC_CLASE[pred]}</p>'
        f'</div>',
        unsafe_allow_html=True,
    )
    labels = [CLASES[k] for k in sorted(CLASES)]
    valores = [round(float(p) * 100, 1) for p in proba]
    colors  = [COLOR_CLASE[k] for k in sorted(CLASES)]

    fig = go.Figure(go.Bar(
        x=valores, y=labels, orientation="h",
        marker=dict(color=colors, cornerradius=6, line=dict(width=0)),
        text=[f"{v:.1f}%" for v in valores], textposition="outside",
    ))
    fig.update_layout(
        title=dict(text="Probabilidad por clase", font=dict(size=12, color=C_TEXT)),
        xaxis=dict(title="Probabilidad (%)", range=[0, 118], showgrid=False),
        yaxis=dict(autorange="reversed"),
        height=200, margin=dict(l=10, r=10, t=35, b=10),
        plot_bgcolor="white", paper_bgcolor="white",
    )
    st.plotly_chart(fig, use_container_width=True)


def sec_prediccion(modelo, meta):
    page_header("Predicción de fragilidad", f"Modelo: {meta.get('modelo','—')} · F1 macro {meta.get('valor_metrica',0):.3f} · Accuracy {meta.get('accuracy',0):.3f}")

    st.markdown(
        '<div class="ethical-box">'
        '<b>Aviso ético:</b> El resultado es una estimación estadística generada por el modelo. '
        'Debe ser revisado por una persona responsable antes de tomar decisiones financieras, '
        'crediticias o de política pública. No reemplaza la asesoría de un experto.'
        '</div>',
        unsafe_allow_html=True,
    )

    with st.form("form_pred"):
        valores = _form()
        st.markdown("<br>", unsafe_allow_html=True)
        sub = st.form_submit_button("Predecir fragilidad financiera", type="primary", use_container_width=True)

    if sub:
        X = pd.DataFrame([{f: valores[f] for f in FEATURES}])
        pred  = int(modelo.predict(X)[0])
        proba = modelo.predict_proba(X)[0]
        st.markdown("### Resultado")
        _resultado(pred, proba)
        with st.expander("Vector de variables enviado al modelo"):
            st.dataframe(X.T.rename(columns={0:"valor"}), use_container_width=True)


def sec_conclusiones(meta):
    page_header("Conclusiones", "Hallazgos, limitaciones y reflexión ética del proyecto")

    col_a, col_b = st.columns(2)

    with col_a:
        sec_label("Hallazgos principales")
        hallazgos = [
            ("Percepciones subjetivas predicen fragilidad real",
             "Variables como la capacidad autopercibida de atender imprevistos (T401_1) tienen poder predictivo comparable al ingreso objetivo."),
            ("Ingreso y educación son determinantes estructurales",
             "El rango de ingresos y el nivel educativo aparecen consistentemente entre las features más importantes del modelo."),
            ("El balanceo de clases no es la raíz del problema",
             "5 estrategias de balanceo (SMOTE, class_weight, Balanced Random Forest) no mejoraron el F1 macro global. La limitación es la separabilidad de las features, no la cantidad de datos."),
            ("Gradient Boosting superó a los demás algoritmos",
             f"En comparación con Logistic Regression, Decision Tree y Random Forest, el Gradient Boosting obtuvo el mayor F1 macro en test (F1={meta.get('valor_metrica', 0):.3f} vs 0.507 RF). Un experimento adicional con 20 variables alternativas confirmó el resultado (GB F1=0.497 con esas variables vs {meta.get('valor_metrica', 0):.3f} con el pipeline de {meta.get('n_features', 40)} features)."),
        ]
        for titulo, desc in hallazgos:
            st.markdown(
                f'<div class="finding-card"><b>{titulo}</b><br><span style="color:#6F6B86">{desc}</span></div>',
                unsafe_allow_html=True,
            )

    with col_b:
        sec_label("Limitaciones conocidas")
        limitaciones = [
            "Los datos son de corte transversal (2022). No capturan cambios económicos posteriores.",
            f"La clase Baja ({meta.get('classification_report', {}).get('1', {}).get('support', 0) / meta.get('n_test', 1) * 100:.1f}% del test) tiene menor recall ({meta.get('classification_report', {}).get('1', {}).get('recall', 0):.2f}). El modelo puede sobrestimar la fragilidad.",
            "Las variables de percepción son autorreportadas y pueden tener sesgo de deseabilidad social.",
            "La muestra sobrerepresenta ciudades grandes; puede no generalizar bien a zonas rurales.",
            "El modelo no fue auditado formalmente por equidad (fairness) por subgrupos.",
        ]
        for lim in limitaciones:
            st.markdown(
                f'<div style="display:flex;gap:10px;align-items:flex-start;padding:10px 0;border-bottom:1px solid #ECEAF4">'
                f'<span style="color:{C_AMBER};font-size:1rem;margin-top:1px">⚠</span>'
                f'<span style="font-size:0.88rem;color:#6F6B86;line-height:1.55">{lim}</span></div>',
                unsafe_allow_html=True,
            )

        sec_label("Declaración ética")
        st.markdown(
            '<div class="ethical-box" style="margin-top:8px">'
            '<b>Este sistema es una herramienta de apoyo analítico.</b> El resultado '
            'no debe usarse como único criterio para negar servicios financieros, '
            'excluir personas de programas sociales ni tomar decisiones automáticas '
            'sobre el bienestar de un hogar. Siempre requiere revisión humana.'
            '</div>',
            unsafe_allow_html=True,
        )

        sec_label("Proyecto")
        st.markdown(
            '<div class="card" style="padding:14px 18px">'
            '<p style="font-size:0.82rem;color:#6F6B86;line-height:1.7;margin:0">'
            '<b>Luz Adriana Giraldo Gómez</b><br>'
            'Diplomado en Desarrollo Web para Analítica de Datos<br>'
            'Tecnología en Desarrollo de Software · 2025/2026'
            '</p></div>',
            unsafe_allow_html=True,
        )


# ── App principal ────────────────────────────────────────────────────────────────
def main():
    modelo, meta = cargar_modelo()
    df = cargar_datos()

    SECCIONES = {
        "🏠  Inicio":               lambda: sec_inicio(meta),
        "📊  Dataset":              lambda: sec_dataset(df),
        "🔍  Análisis exploratorio": lambda: sec_eda(df),
        "🤖  Modelo":               lambda: sec_modelo(meta),
        "📈  Métricas":             lambda: sec_metricas(meta),
        "🎯  Predicción":           lambda: sec_prediccion(modelo, meta),
        "✅  Conclusiones":         lambda: sec_conclusiones(meta),
    }

    with st.sidebar:
        st.markdown(
            '<div style="padding:0 8px 16px 8px">'
            '<p style="font-size:1.3rem;font-weight:800;color:white;margin:0;letter-spacing:-0.02em">FinBalance</p>'
            '<p style="font-size:0.75rem;color:#9B97B4;margin:2px 0 0 0">Fragilidad Financiera · EDF 2022</p>'
            '</div>',
            unsafe_allow_html=True,
        )
        st.divider()

        seccion = st.radio("", options=list(SECCIONES.keys()), label_visibility="collapsed")

        st.divider()
        st.markdown('<p style="font-size:0.65rem;color:#6F6B86;text-transform:uppercase;letter-spacing:0.08em;margin:0 0 8px 0">Métricas activas</p>', unsafe_allow_html=True)
        c1, c2 = st.columns(2)
        c1.metric("F1 macro", f"{meta.get('valor_metrica',0):.3f}")
        c2.metric("Accuracy", f"{meta.get('accuracy',0):.3f}")
        n_train = meta.get("n_train","—")
        n_test  = meta.get("n_test","—")
        st.caption(
            f"Train: {n_train:,} | Test: {n_test:,}"
            if isinstance(n_train, int) else f"Train: {n_train} | Test: {n_test}"
        )

        st.divider()
        st.caption("Diplomado Desarrollo Web · Entrega final")

    SECCIONES[seccion]()


if __name__ == "__main__":
    main()
