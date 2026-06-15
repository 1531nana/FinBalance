# Arquitectura del Sistema — FinBalance

## Descripción general

FinBalance es un sistema de análisis y predicción de fragilidad financiera compuesto por
cuatro capas: **datos**, **modelado ML**, **dashboard web** y **API REST**.
El flujo va desde el archivo fuente crudo hasta el resultado de predicción,
accesible tanto por el dashboard interactivo como por la API programática.

---

## Diagrama de componentes

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          CAPA DE DATOS                                  │
│                                                                         │
│  data/raw/                         data/processed/                      │
│  └── Encuesta_demanda_2022_        ├── dataset_limpio.csv               │
│      microdatos.xlsx               ├── train.csv  (80 %)                │
│      (archivo fuente, sin          └── test.csv   (20 %)                │
│       modificar)                                                        │
└────────────────────────────┬────────────────────────────────────────────┘
                             │
                    notebooks/02_eda_limpieza.ipynb
                    (limpieza, encoding, split estratificado)
                             │
┌────────────────────────────▼────────────────────────────────────────────┐
│                     CAPA DE MODELADO ML                                 │
│                                                                         │
│  notebooks/03_modelado.ipynb        src/ml/entrenar_modelo.py           │
│  (experimentación, tuning,          (script reproducible local)         │
│   comparación de modelos)                                               │
│                    │                                                    │
│                    ▼                                                    │
│  models/                                                                │
│  ├── modelo_final.pkl     ← Gradient Boosting serializado (joblib)      │
│  └── model_metadata.json  ← métricas, versión, variables de entrada     │
└──────────────┬─────────────────────────────┬────────────────────────────┘
               │                             │
       joblib.load()                 joblib.load()
               │                             │
┌──────────────▼──────────────┐   ┌──────────▼──────────────────────────┐
│   CAPA DE PRESENTACIÓN      │   │   CAPA DE API REST                  │
│                             │   │                                     │
│   app_final.py (Streamlit)  │   │   api.py (FastAPI + uvicorn)        │
│   ├── Inicio                │   │   ├── GET  /health                  │
│   ├── Dataset               │   │   │       estado de la API          │
│   ├── Análisis exploratorio │   │   ├── GET  /metrics                 │
│   ├── Modelo                │   │   │       métricas del modelo       │
│   ├── Métricas              │   │   └── POST /predict                 │
│   ├── Predicción            │   │           predicción + probabilidad │
│   └── Conclusiones          │   │                                     │
│                             │   │   Docs: /docs (Swagger UI)          │
│   streamlit run app_final.py│   │   uvicorn api:app --reload          │
└─────────────────────────────┘   └─────────────────────────────────────┘
```

---

## Flujo de datos detallado

```
Encuesta_demanda_2022_microdatos.xlsx
        │
        │  pd.read_excel(usecols=cols_needed)
        │  → variables candidatas de la EDF 2022 + variable objetivo P407
        ▼
02_eda_limpieza.ipynb
        │  1. Mapeo P407 → fragilidad_label (1=Baja, 2=Media, 3=Alta)
        │  2. Imputación con mediana (variables ordinales)
        │  3. Codificación: ordinal, binaria, OHE
        │  4. train_test_split(test_size=0.20, stratify=y, random_state=42)
        ▼
data/processed/train.csv  |  data/processed/test.csv
        │
        │  X_train, y_train, X_test, y_test
        ▼
03_modelado.ipynb / src/ml/entrenar_modelo.py
        │  1. DummyClassifier (baseline — F1 macro: 0.188)
        │  2. Comparación: LR (0.495), DT (0.442), RF (0.507), GB (0.514)
        │  3. GridSearchCV sobre Gradient Boosting (27 combinaciones, 5 folds)
        │  4. Curva de aprendizaje + curva de validación
        │  5. 5 estrategias de balanceo de clases evaluadas
        │  6. Evaluación final sobre test (holdout, una sola vez)
        ▼
models/modelo_final.pkl        models/model_metadata.json
        │                               │
        ├───────────────────────────────┤
        │                               │
        ▼                               ▼
app_final.py (Streamlit)         api.py (FastAPI)
@st.cache_resource               lifespan() al arranque
→ dashboard interactivo          → endpoints REST /health /metrics /predict
→ usuario final (navegador)      → integración programática (JSON)
```

---

## Tecnologías por capa

| Capa | Tecnología | Versión |
|---|---|---|
| Ingesta de datos | pandas / openpyxl | 2.2.3 / 3.1.5 |
| Preprocesamiento | pandas, scikit-learn | 2.2.3 / 1.9.0 |
| Modelado | scikit-learn, imbalanced-learn | 1.9.0 / 0.14.2 |
| Serialización | joblib | 1.5.3 |
| Dashboard | Streamlit | 1.58.0 |
| Visualizaciones | Plotly, Matplotlib, Seaborn | 6.8.0 / 3.10.9 / 0.13.2 |
| API REST | FastAPI + uvicorn | 0.115.6 / 0.34.0 |
| Validación de esquema | Pydantic | (incluida en FastAPI) |
| Control de versiones | Git / GitHub | — |
| Entorno | Python 3.11 | — |

---

## Estructura del repositorio

```
FinBalance/
├── app_final.py                  ← Dashboard Streamlit (punto de entrada)
├── api.py                        ← API REST FastAPI (componente opcional)
├── requirements.txt              ← Dependencias con versiones fijas
├── .gitignore
├── README.md
├── data/
│   ├── raw/                      ← Dataset original sin modificar
│   └── processed/                ← Splits y dataset limpio
│       ├── dataset_limpio.csv
│       ├── train.csv
│       └── test.csv
├── models/
│   ├── modelo_final.pkl          ← Gradient Boosting serializado
│   └── model_metadata.json       ← Métricas, variables y comparación de modelos
├── notebooks/
│   ├── 01_exploracion.ipynb      ← EDA inicial
│   ├── 02_eda_limpieza.ipynb     ← Pipeline de limpieza y split
│   └── 03_modelado.ipynb         ← Entrenamiento, tuning y evaluación
├── src/
│   └── ml/
│       └── entrenar_modelo.py    ← Script reproducible de entrenamiento local
└── docs/
    ├── ficha_proyecto.md
    ├── analisis_dataset.md
    ├── diccionario_datos.md
    ├── arquitectura.md           ← Este archivo
    └── reflexion_etica.md
```

---

## Decisiones de diseño clave

| Decisión | Justificación |
|---|---|
| Gradient Boosting como modelo final | Obtuvo el mayor F1 macro en test (0.514) al comparar DummyClassifier, LR, DT, RF y GB con los mismos datos y métrica |
| StandardScaler en el pipeline | Gradient Boosting no es sensible a escala, pero se incluye para consistencia con el pipeline general y compatibilidad con otros modelos comparados |
| Streamlit como dashboard | Integración directa con modelos sklearn sin necesidad de frontend separado; ideal para prototipado analítico |
| FastAPI como API REST | Framework moderno, documentación automática (Swagger), validación con Pydantic y alto rendimiento |
| joblib para serialización | Más eficiente que pickle para objetos numpy/sklearn |
| `@st.cache_resource` para el modelo | El modelo se carga una sola vez por sesión, reduciendo la latencia de cada predicción |
| `lifespan()` en FastAPI | Verifica que `.pkl` y `.json` existen antes de levantar la API; falla rápido con mensaje claro si faltan artefactos |
| Split 80/20 estratificado (una sola vez) | Ocurre en notebook 02 y se persiste en disco; los notebooks 03 y el script cargan los splits sin volver a dividir |
| F1 macro como métrica principal | Las tres clases tienen distribución desigual (38 % / 39 % / 23 %); F1 macro pondera igual cada clase sin premiar a la mayoritaria |
| Balanceo de clases no aplicado | Se evaluaron 5 estrategias; ninguna mejoró el F1 macro global, lo que indica que el límite es la separabilidad de las features, no el desbalance |