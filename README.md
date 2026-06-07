# FinBalance — Clasificador de Fragilidad Financiera ante Pérdida de Ingresos

> Proyecto integrador — Diplomado en Desarrollo Web para Analítica de Datos  
> Tecnología en Desarrollo de Software

---

## Descripción del proyecto

FinBalance es una aplicación web analítica que clasifica el nivel de fragilidad financiera de una persona adulta colombiana ante una posible pérdida de ingresos, categorizándolo como **alto**, **medio** o **bajo**.

El resultado busca orientar al usuario hacia acciones preventivas relacionadas con ahorro, manejo de deuda y planeación financiera, antes de que ocurra una emergencia económica.

---

## Pregunta analítica

¿Es posible clasificar el nivel de fragilidad financiera (alta, media o baja) de una persona adulta colombiana ante la pérdida de ingresos, usando variables de ingresos, gastos, ocupación, educación, productos financieros, ahorro, crédito y hábitos financieros disponibles en los microdatos de la Encuesta de Demanda Financiera 2022, con el fin de orientarla hacia acciones preventivas concretas antes de que ocurra una emergencia económica?

---

## Dataset

- **Fuente:** Encuesta de Demanda Financiera 2022 — Banca de las Oportunidades / BANCOLDEX
- **Registros:** 5.610 (5.227 válidos para entrenamiento)
- **Variables seleccionadas:** 45 (1 objetivo + 44 de entrada)
- **Uso:** Exclusivamente académico

---

## Tipo de tarea y métrica

| Elemento | Detalle |
|---|---|
| Tipo de tarea | Clasificación multiclase |
| Variable objetivo | `fragilidad_financiera` (alta / media / baja) |
| Métrica principal | F1-score macro |

---

## Estructura del repositorio

```
FinBalance/
├── data/
│   └── raw/
│       └── Encuesta_demanda_2022_microdatos.xlsx
├── docs/
│   ├── ficha_proyecto.md
│   ├── analisis_dataset.md
│   └── wireframe_dashboard.png
├── notebooks/
│   └── 01_exploracion.ipynb
├── .gitignore
├── requirements.txt
└── README.md
```

---

## Instalación y uso

```bash
# Clonar el repositorio
git clone https://github.com/1531nana/FinBalance.git
cd FinBalance

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar el notebook de exploración
jupyter notebook notebooks/01_exploracion.ipynb
```

---

## Dependencias

Las librerías necesarias para el proyecto están listadas en `requirements.txt`:

```
pandas
openpyxl
numpy
scikit-learn
matplotlib
seaborn
jupyter
```

---

## Autor

**Luz Adriana Giraldo Gómez**  
Tecnología en Desarrollo de Software  
Diplomado en Desarrollo Web para Analítica de Datos — 2026

---