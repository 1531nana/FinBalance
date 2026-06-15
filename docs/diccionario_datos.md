# Diccionario de Datos — FinBalance

Dataset fuente: **Encuesta de Demanda Financiera 2022** (EDF 2022)
Fuente: **Banca de las Oportunidades** — programa del Gobierno Nacional de Colombia, administrado por **Bancoldex**
Registros originales: 5.610 | Registros para modelado (tras filtrar NS/NR en objetivo): 5.227
Features del modelo: 40 (tras codificación OHE de género, ruralidad y región)

---

## Variable objetivo

| Variable | Tipo | Valores | Descripción |
|---|---|---|---|
| `fragilidad_label` | Ordinal / Target | 1, 2, 3 | Nivel de fragilidad financiera del hogar. Derivada de **P407** (tiempo que el hogar podría sostenerse sin ingresos). |

**Mapeo de P407 a `fragilidad_label`:**

| Respuesta en encuesta | Descripción | Clase | Valor numérico |
|---|---|---|---|
| Una semana / Dos semanas | Menos de un mes sin ingresos | Alta | 3 |
| Un mes / Tres meses | Entre 1 y 5 meses sin ingresos | Media | 2 |
| Seis meses / Un año / Más de un año | Seis meses o más sin ingresos | Baja | 1 |
| NS/NR | No sabe / No responde | **Excluido** | — |

---

## Variables de entrada (features)

### Sociodemográficas

| Variable modelo | Variable EDF | Tipo | Rango / Valores | Codificación | Descripción |
|---|---|---|---|---|---|
| `edad` | EDAD | Numérica continua | 18–99 | Sin cambio | Edad del encuestado en años |
| `nivel_educativo` | P708 | Ordinal | 0–6 | Ordinal | Nivel educativo más alto alcanzado. 0=Ninguno, 1=Primaria, 2=Secundaria, 3=Técnico, 4=Tecnólogo, 5=Universitario, 6=Posgrado |
| `estrato` | ESTRATO | Ordinal | 1–6 | Sin cambio (numérico) | Estrato socioeconómico de la vivienda según recibo de servicios públicos. NS/NR imputado con mediana |
| `genero_Masculino` | GENERO | Binaria | 0–1 | OHE (baseline = Femenino) | 1 si el encuestado se identifica como masculino |
| `ruralidad_Intermedio` | RURALIDAD | Binaria | 0–1 | OHE (baseline = Ciudades y aglomeraciones) | 1 si la vivienda está en zona intermedia |
| `ruralidad_Rural` | RURALIDAD | Binaria | 0–1 | OHE | 1 si la vivienda está en zona rural |
| `ruralidad_Rural disperso` | RURALIDAD | Binaria | 0–1 | OHE | 1 si la vivienda está en zona rural dispersa |
| `region_Centro Oriente` | REGION | Binaria | 0–1 | OHE (baseline = Caribe) | 1 si el encuestado reside en la región Centro Oriente |
| `region_Centro Sur` | REGION | Binaria | 0–1 | OHE | 1 si el encuestado reside en la región Centro Sur |
| `region_Eje cafetero` | REGION | Binaria | 0–1 | OHE | 1 si el encuestado reside en el Eje Cafetero |
| `region_Llano` | REGION | Binaria | 0–1 | OHE | 1 si el encuestado reside en la región Llanos Orientales |
| `region_Pacifico` | REGION | Binaria | 0–1 | OHE | 1 si el encuestado reside en la región Pacífico |

> Las columnas de OHE para `genero`, `ruralidad` y `region` se generaron con `pd.get_dummies(drop_first=True)`.
> La categoría base (eliminada para evitar multicolinealidad) es: Femenino / Ciudades y aglomeraciones / Caribe.

---

### Ingresos

| Variable modelo | Variable EDF | Tipo | Rango / Valores | Codificación | Descripción |
|---|---|---|---|---|---|
| `rango_ingresos` | P714 | Ordinal | 1–10 | Ordinal | Rango del ingreso mensual total del hogar. 1=Menos de $250.000, 2=$250.001–$500.000, ..., 10=Más de $5.000.000. NS/NR imputado con mediana |
| `rango_gastos` | P715 | Ordinal | 1–10 | Ordinal (misma escala que rango_ingresos) | Rango del gasto mensual total del hogar. Misma escala de codificación que `rango_ingresos`. NS/NR imputado con mediana |
| `ing_salario` | T208_1 | Binaria | 0–1 | Binaria (Sí=1, No=0) | El hogar recibe ingresos por salario o sueldo |
| `ing_pension` | T208_2 | Binaria | 0–1 | Binaria | El hogar recibe ingresos por pensión o jubilación |
| `ing_arriendos` | T208_3 | Binaria | 0–1 | Binaria | El hogar recibe ingresos por arriendos |
| `ing_honorarios` | T208_5 | Binaria | 0–1 | Binaria | El hogar recibe ingresos por honorarios o consultoría |
| `ing_ventas` | T208_6 | Binaria | 0–1 | Binaria | El hogar recibe ingresos por ventas o negocio propio |
| `ing_subsidios` | T208_8 | Binaria | 0–1 | Binaria | El hogar recibe subsidios del Estado |
| `ing_remesas` | T208_9 | Binaria | 0–1 | Binaria | El hogar recibe remesas del exterior |
| `ing_ayuda_familiar` | T208_10 | Binaria | 0–1 | Binaria | El hogar recibe ayuda económica de familiares |

---

### Gastos

| Variable modelo | Variable EDF | Tipo | Rango / Valores | Codificación | Descripción |
|---|---|---|---|---|---|
| `gasto_arriendo` | T211_1 | Binaria | 0–1 | Binaria (Sí=1, No=0) | El hogar tiene gastos en arriendo o vivienda |
| `gasto_servicios` | T211_2 | Binaria | 0–1 | Binaria | El hogar tiene gastos en servicios públicos (agua, luz, gas, internet) |
| `gasto_seg_social` | T211_5 | Binaria | 0–1 | Binaria | El hogar tiene gastos en seguridad social o salud |

---

### Productos financieros

| Variable modelo | Variable EDF | Tipo | Rango / Valores | Codificación | Descripción |
|---|---|---|---|---|---|
| `prod_cuenta_ahorro` | T101_1 | Binaria | 0–1 | Binaria (Sí=1, No=0) | El encuestado tiene al menos una cuenta de ahorros activa |
| `prod_tarjeta_debito` | T101_2 | Binaria | 0–1 | Binaria | El encuestado tiene tarjeta débito activa |
| `prod_monedero` | T101_5 | Binaria | 0–1 | Binaria | El encuestado tiene monedero digital (ej. Daviplata, Nequi) |
| `prod_cdt` | T101_6 | Binaria | 0–1 | Binaria | El encuestado tiene un CDT (Certificado de Depósito a Término) |
| `prod_fondo_inv` | T101_7 | Binaria | 0–1 | Binaria | El encuestado tiene participación en fondo de inversión |
| `prod_fondo_emp` | T101_8 | Binaria | 0–1 | Binaria | El encuestado tiene fondo de empleados |

---

### Comportamiento financiero

| Variable modelo | Variable EDF | Tipo | Rango / Valores | Codificación | Descripción |
|---|---|---|---|---|---|
| `comp_atraso_pagos` | T402_3 | Ordinal | 1–5 | Escala de frecuencia | Con qué frecuencia el encuestado se atrasa en el pago de cuentas o deudas. 1=Nunca, 2=Casi nunca, 3=A veces, 4=Casi siempre, 5=Siempre |
| `comp_deuda_mayor_activos` | T405_4 | Ordinal | 1–5 | Escala de acuerdo | Percepción de que las deudas superan los activos del hogar. 1=Totalmente en desacuerdo … 5=Totalmente de acuerdo. NS/NR imputado con mediana (1) |
| `comp_tiene_plan` | T406_2 | Binaria | 0–1 | Binaria (Sí=1, No=0) | El encuestado tiene un plan financiero o presupuesto formal |
| `hab_encargado_gastos` | T406_1 | Binaria | 0–1 | Binaria | El encuestado es el responsable principal de los gastos del hogar |
| `hab_encargado_presup` | T406_3 | Binaria | 0–1 | Binaria | El encuestado es el responsable del presupuesto del hogar |
| `hab_usa_app_bancaria` | T406_4 | Binaria | 0–1 | Binaria | El encuestado usa aplicaciones bancarias o de pagos digitales |

---

### Percepciones financieras

| Variable modelo | Variable EDF | Tipo | Rango / Valores | Codificación | Descripción |
|---|---|---|---|---|---|
| `perc_camino_obj` | T405_2 | Ordinal | 1–5 | Escala de acuerdo | El encuestado siente que va por buen camino para alcanzar sus objetivos financieros. 1=Totalmente en desacuerdo … 5=Totalmente de acuerdo. NS/NR imputado con mediana (3) |
| `perc_deuda_manejable` | T405_3 | Ordinal | 1–5 | Escala de acuerdo | El encuestado percibe que sus deudas actuales son manejables. 1=Totalmente en desacuerdo … 5=Totalmente de acuerdo. NS/NR imputado con mediana (4) |
| `perc_control_sit` | T405_8 | Ordinal | 1–5 | Escala de acuerdo | El encuestado siente que tiene control sobre su situación financiera. 1=Totalmente en desacuerdo … 5=Totalmente de acuerdo. NS/NR imputado con mediana (4) |

---

## Variables cargadas pero excluidas del modelo

Estas variables se cargaron en el EDA pero fueron eliminadas antes del entrenamiento:

| Variable | Variable EDF | Razón de exclusión |
|---|---|---|
| `ocupacion` | P704 | Alta cardinalidad de texto sin orden definido |
| `tipo_vinculacion` | P705 | 50 % de nulos estructurales (no aplica a quienes no trabajan); imputado como 'No aplica' pero sin valor predictivo adicional |
| `frec_ingresos` | P716 | Alta tasa de NS/NR (7,1 %) y baja variabilidad tras imputación |
| `solicito_credito` | P301 | Texto descriptivo de alta cardinalidad; OHE generaría columnas muy dispersas |
| `beneficiario_subsidio` | P103 | 41,5 % de nulos condicionales; imputado como 'No' pero captura poca variación útil |
| `prod_mas_usado` | P104 | 41,7 % de nulos; alta cardinalidad sin orden |
| `comp_frec_cumple_plan` | P406A | 40,7 % de nulos (pregunta condicional a quienes tienen plan); imputado como 'No tiene plan' |
| `perc_nunca_tendre` | T401_3 | Escala de percepción con NS/NR alto y baja correlación con el objetivo |
| `perc_disfruta_vida` | T401_4 | Escala de percepción con NS/NR alto y baja correlación con el objetivo |
| `perc_confianza_dec` | T401_8 | Escala de percepción con NS/NR alto y baja correlación con el objetivo |
| `nivel_fragilidad` | — | Variable auxiliar de EDA (texto: Alta/Media/Baja); reemplazada por `fragilidad_label` |

---

## Notas metodológicas

- **Selección de variables:** se cargaron todas las variables candidatas identificadas en el análisis previo. La selección final de las 40 features resultó de eliminar columnas con alta cardinalidad de texto, NS/NR estructural alto o que se transformaron mediante OHE en columnas binarias derivadas.
- **Imputación de NS/NR en escalas ordinales:** los valores NS/NR en `perc_camino_obj`, `perc_deuda_manejable`, `perc_control_sit` y `comp_deuda_mayor_activos` se imputaron con la mediana de cada columna calculada sobre el dataset completo (antes del split). Para el entrenamiento del modelo, el escalamiento se ajusta solo sobre train.
- **Imputación de rango_ingresos / rango_gastos / estrato:** nulos residuales imputados con la mediana columnar antes del split (celda 5.3 de `02_eda_limpieza.ipynb`).
- **Codificación binaria:** las variables con respuesta Sí/No se normalizaron a Sí=1, No=0. Las variantes en mayúsculas (SI, NO) fueron homologadas antes de la codificación.
- **One-Hot Encoding:** se aplicó `pd.get_dummies(drop_first=True)` sobre `genero`, `ruralidad` y `region`. La categoría de referencia eliminada es Femenino, Ciudades y aglomeraciones y Caribe respectivamente.
- **Split:** división estratificada 80 % entrenamiento (4.181 registros) / 20 % prueba (1.046 registros) con `random_state=42`.
