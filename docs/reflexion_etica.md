# Reflexión Ética — FinBalance

**Proyecto:** Clasificador de Fragilidad Financiera — EDF 2022
**Fecha:** 16 de junio de 2026

---

## 1. Contexto del sistema

FinBalance es un clasificador de machine learning que predice el nivel de fragilidad financiera
de hogares colombianos (Alta / Media / Baja) usando datos de la Encuesta de Demanda
Financiera 2022. El sistema fue desarrollado con fines analíticos y académicos dentro del
Diplomado en Desarrollo Web para Analítica de Datos.

---

## 2. Riesgos identificados

### 2.1. Riesgos en el dataset

| Riesgo | Descripción | Nivel |
|---|---|---|
| Sesgo de respuesta en NS/NR | El 6,8 % de los encuestados no respondió P407 y fue excluido. Si este grupo tiene mayor vulnerabilidad (no sabe si podría sobrevivir sin ingresos), el modelo podría subestimar la fragilidad real en ese segmento. | Medio |
| Sesgo de deseabilidad social | Variables de autopercepción (T401, T402, T405) pueden estar sesgadas: las personas tienden a reportar una situación mejor de la real cuando responden encuestas. | Medio |
| Representación geográfica desigual | La muestra sobrerrepresenta ciudades grandes. El modelo puede no generalizar bien a zonas rurales remotas con dinámicas financieras distintas. | Medio |
| Datos de corte transversal | La encuesta es una fotografía del 2022. No captura cambios pospandemia, inflación de 2023-2024 ni políticas públicas posteriores. | Alto |

### 2.2. Riesgos del modelo

| Riesgo | Descripción | Nivel |
|---|---|---|
| Menor sensibilidad en clase Baja | La clase "Baja" (hogares más estables) representa solo el ~23 % del dataset. El modelo tiene menor recall en esta clase, lo que significa que puede clasificar hogares estables como fragilidad media o alta. | Alto |
| Variables con potencial discriminatorio | Variables como estrato, nivel educativo y género pueden amplificar desigualdades estructurales si el modelo se usa en decisiones de crédito o asignación de beneficios. | Alto |
| Retroalimentación negativa | Si el resultado del modelo se usa para negar crédito a hogares clasificados como frágiles, la fragilidad real puede aumentar como consecuencia directa del uso del modelo. | Alto |
| Falsa precisión numérica | Una probabilidad del "83,2 %" puede inducir a tomar decisiones con mayor certeza de la que el modelo realmente ofrece. | Medio |

---

## 3. Grupos potencialmente afectados por errores

- **Hogares en zona rural**: subrepresentados en el dataset. El modelo puede clasificarlos incorrectamente.
- **Mujeres jefas de hogar**: el género es una variable del modelo; si hay sesgo histórico en la encuesta, puede reproducirse.
- **Hogares de estrato 1 y 2**: mayor vulnerabilidad real; un falso negativo (clasificar como fragilidad "Baja") podría privarlos de atención prioritaria.
- **Personas mayores**: la encuesta no tiene sesgo explícito de edad, pero las dinámicas de pensiones y empleo estable pueden no estar bien capturadas.
- **Trabajadores informales**: el modelo usa `frec_ingresos` y `miembros_empleo_estable`; hogares con ingresos irregulares pueden ser clasificados de forma inconsistente.

---

## 4. Acciones de mitigación implementadas

| Acción | Descripción |
|---|---|
| Advertencia ética en la interfaz | La sección de Predicción muestra un mensaje explícito de que el resultado es un apoyo estadístico, no una decisión automática. |
| Presentación de probabilidades | El dashboard muestra las probabilidades de las tres clases, no solo la clase predicha, para que el usuario entienda la incertidumbre. |
| Métrica F1 macro | Se usó F1 macro en lugar de accuracy para no premiar al modelo por ignorar la clase minoritaria (Baja). |
| `class_weight='balanced_subsample'` | Se aplicó penalización de clase para reducir el sesgo hacia las clases mayoritarias durante el entrenamiento. |
| Variable objetivo basada en autopercepción | P407 proviene de la respuesta del propio hogar sobre su situación, no de un juicio externo. Esto reduce el riesgo de sesgo institucional. |
| Documentación de limitaciones | El dashboard incluye una sección de Conclusiones con las limitaciones conocidas del modelo. |
| Transparencia del pipeline | Los notebooks de preprocesamiento y modelado son públicos y reproducibles. |

---

## 5. Limitaciones conocidas del sistema

1. **El modelo no predice el futuro**: predice la fragilidad en un momento dado, no cómo evolucionará.
2. **No es un sistema de scoring crediticio**: no fue diseñado ni validado para tomar decisiones de crédito.
3. **No tiene auditorías de equidad formales**: no se realizaron pruebas formales de equidad por género, región o estrato más allá del análisis exploratorio.
4. **Dependencia de la calidad de los datos de entrada**: si el usuario ingresa valores poco realistas en el formulario, el resultado puede ser incorrecto.
5. **El modelo no se actualiza automáticamente**: los datos de entrenamiento son de 2022. Para mantener la vigencia del modelo se requiere reentrenamiento periódico.

---

## 6. Declaración de uso responsable

> El sistema FinBalance es una herramienta de apoyo analítico para la comprensión
> de patrones de fragilidad financiera en el contexto colombiano. **No debe usarse
> como único criterio para tomar decisiones sobre personas**, incluyendo:
>
> - Aprobación o rechazo de créditos
> - Asignación o negación de subsidios o beneficios sociales
> - Clasificación automática de riesgo para fines comerciales
> - Cualquier decisión que afecte los derechos o el bienestar de una persona
>
> Cualquier uso del sistema debe estar acompañado de la revisión de una persona
> responsable con conocimiento del contexto específico del caso.