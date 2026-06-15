# FinBalance — Clasificador de Fragilidad Financiera

> Proyecto integrador — Diplomado en Desarrollo Web para Analítica de Datos
> Tecnología en Desarrollo de Software

---

## Descripción

FinBalance es una aplicación web analítica que predice el nivel de **fragilidad financiera**
de un hogar colombiano (**Alta / Media / Baja**) a partir de sus características
socioeconómicas, de comportamiento y de percepción financiera.

El sistema está compuesto por un pipeline de machine learning entrenado sobre datos reales
y un dashboard interactivo que permite explorar los datos y obtener predicciones.

---

## Pregunta analítica

> ¿Es posible predecir el nivel de fragilidad financiera de un hogar colombiano
> (alta, media o baja) ante la pérdida de ingresos, usando variables socioeconómicas,
> de comportamiento y de percepción disponibles en la Encuesta de Demanda Financiera 2022,
> con el fin de orientar acciones preventivas de política pública y educación financiera?

---

## Dataset

| Campo | Detalle |
|---|---|
| Fuente | Encuesta de Demanda Financiera 2022 — Banca de las Oportunidades / Bancoldex |
| Archivo | `data/raw/Encuesta_demanda_2022_microdatos.xlsx` |
| Registros originales | 5.610 (total encuesta) |
| Registros para modelado | 5.227 (tras excluir 383 respuestas NS/NR en variable objetivo) |
| Features del modelo | 40 (resultado del pipeline de limpieza y codificación sobre EDF 2022) |
| Variable objetivo | P407 → `fragilidad_label` (1=Baja, 2=Media, 3=Alta) |
| Uso | Exclusivamente académico |

---

## Arquitectura de la solución

```
data/raw/  →  02_eda_limpieza.ipynb  →  data/processed/train+test
                                               │
                                    03_modelado.ipynb / entrenar_modelo.py
                                               │
                                    models/modelo_final.pkl + model_metadata.json
                                          │                   │
                                   app_final.py          api.py
                                   (Streamlit)           (FastAPI)
```

Ver descripción detallada en `docs/arquitectura.md`.

---

## Estructura del repositorio

```
FinBalance/
├── app_final.py               ← Dashboard Streamlit (punto de entrada principal)
├── api.py                     ← API REST FastAPI (componente opcional)
├── requirements.txt
├── .gitignore
├── README.md
├── CLAUDE.md
├── data/
│   ├── raw/                   ← Dataset original (sin modificar)
│   └── processed/             ← Splits y dataset limpio
├── models/
│   ├── modelo_final.pkl       ← Modelo serializado
│   └── model_metadata.json    ← Métricas y metadatos
├── notebooks/
│   ├── 01_exploracion.ipynb
│   ├── 02_eda_limpieza.ipynb
│   └── 03_modelado.ipynb
├── src/
│   └── ml/
│       └── entrenar_modelo.py ← Script de entrenamiento local
└── docs/
    ├── ficha_proyecto.md
    ├── analisis_dataset.md
    ├── diccionario_datos.md
    ├── arquitectura.md
    └── reflexion_etica.md
```

---

## Instalación y ejecución

```bash
# 1. Crear entorno virtual
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. (Si no existe models/modelo_final.pkl) Entrenar el modelo
python src/ml/entrenar_modelo.py

# 4. Lanzar el dashboard
streamlit run app_final.py

# 5. (Opcional) Lanzar la API REST
uvicorn api:app --reload
# Documentación interactiva: http://127.0.0.1:8000/docs
```

**Nota:** los notebooks deben ejecutarse en orden (02 antes de 03) para generar
los archivos en `data/processed/` y `models/`.

---

## Resultados del modelo

| Modelo | F1 macro (test) | Accuracy (test) |
|---|---|---|
| **Gradient Boosting (final)** | **0.514** | **0.550** |
| Random Forest | 0.507 | 0.544 |
| Logistic Regression | 0.495 | 0.532 |
| Decision Tree | 0.442 | 0.493 |
| DummyClassifier (baseline) | 0.188 | — |

Las métricas exactas se leen dinámicamente desde `model_metadata.json` en el dashboard.

**Variables más importantes:** percepciones financieras subjetivas (`perc_camino_obj`, `perc_control_sit`),
rango de ingresos y nivel educativo.

---

## Consideraciones éticas

- El resultado del modelo es una **estimación estadística**, no una decisión automática.
- No debe usarse como único criterio para negar créditos o beneficios sociales.
- La clase "Baja" (~23 % del dataset) tiene menor recall; el modelo puede sobrestimar fragilidad.
- Ver `docs/reflexion_etica.md` para el análisis completo de riesgos y mitigaciones.

---

## Autor

**Luz Adriana Giraldo Gómez**
Tecnología en Desarrollo de Software
Diplomado en Desarrollo Web para Analítica de Datos — 14 de junio de 2026
