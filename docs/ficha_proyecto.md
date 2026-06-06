# Ficha de Formulación del Proyecto Integrador

## 1. Datos del estudiante

- **Nombre completo:** Luz Adriana Giraldo Gómez
- **Programa:** Tecnología en Desarrollo de Software — Diplomado en Desarrollo Web
- **Fecha:** 6 de junio de 2026

---

## 2. Nombre del proyecto

**FinBalance — Clasificador de Fragilidad Financiera ante Pérdida de Ingresos**

---

## 3. Planteamiento del problema

En el contexto de la estabilidad económica de los hogares colombianos, muchas personas adultas no tienen claridad sobre qué tan expuestas están ante un choque económico inesperado, como la pérdida del empleo, una enfermedad o una emergencia del hogar. Esta incertidumbre es relevante porque, cuando ocurre una emergencia, las personas pueden verse obligadas a recurrir a créditos informales costosos, endeudarse o vender activos, afectando aún más su bienestar financiero. Esta situación puede analizarse a partir de los microdatos de la Encuesta de Demanda Financiera 2022, que recoge información sobre ingresos, gastos, ahorro, crédito, productos financieros y hábitos financieros de más de 5.500 personas adultas colombianas.

Por ello, se propone desarrollar una aplicación web analítica dirigida a cualquier persona adulta colombiana que desee conocer su nivel de exposición financiera, que permita clasificar su nivel de fragilidad financiera ante la pérdida de ingresos como alto, medio o bajo. El resultado busca orientar al usuario hacia acciones preventivas relacionadas con ahorro, manejo de deuda y planeación financiera antes de que ocurra una emergencia económica.

---

## 4. Pregunta analítica

¿Es posible clasificar el nivel de fragilidad financiera (alta, media o baja) de una persona adulta colombiana ante la pérdida de ingresos, usando variables de ingresos, gastos, ocupación, educación, productos financieros, ahorro, crédito y hábitos financieros disponibles en los microdatos de la Encuesta de Demanda Financiera 2022, con el fin de orientarla hacia acciones preventivas concretas antes de que ocurra una emergencia económica, evaluando el desempeño con F1-score macro dado el posible desbalance entre clases?

---

## 5. Tipo de tarea y métrica de evaluación

- **Tipo de tarea:** [x] Clasificación &nbsp;&nbsp; [ ] Regresión &nbsp;&nbsp; [ ] Clustering
- **Métrica principal:** F1-score macro
- **Justificación de la métrica:** Se elige F1-score macro porque las tres clases de fragilidad (alta, media y baja) presentan un desbalance moderado — la clase baja representa solo el 20,8 % de los registros válidos frente al 35,8 % y 36,6 % de las clases alta y media respectivamente. El F1-score macro pondera por igual el desempeño en cada clase, independientemente de su tamaño, lo que evita que el modelo optimice para las clases mayoritarias a costa de ignorar la clase menos frecuente. Adicionalmente, el costo de clasificar erróneamente a una persona de fragilidad alta como fragilidad baja es significativo: esa persona no recibiría la orientación preventiva que necesita.

---

## 6. Descripción del dataset

- **Nombre:** Encuesta de Demanda Financiera 2022 — Microdatos
- **Fuente:** Banca de las Oportunidades — BANCOLDEX. Dataset facilitado por el docente del diplomado con fines académicos.
- **Fuente (URL):** https://www.bancadelasoportunidades.gov.co/sites/default/files/2022-10/Encuesta_demanda_2022_microdatos.xlsx
- **Licencia:** Uso académico exclusivo, no apto para distribución.
- **Número de filas:** 5.610 registros (5.227 válidos para entrenamiento tras excluir NS/NR).
- **Número de columnas:** 45 columnas seleccionadas para el proyecto (1 variable objetivo + 44 variables de entrada).
- **Descripción general:** Encuesta presencial aplicada entre el 5 de abril y el 27 de mayo de 2022 a personas adultas colombianas mayores de 18 años en todos los municipios del país. Captura comportamientos, percepciones y condiciones relacionadas con el acceso y uso de servicios financieros en cuatro dimensiones: acceso, uso, calidad y bienestar financiero. Para este proyecto se seleccionaron variables de ingresos, gastos, productos financieros, crédito, hábitos financieros y percepción de estabilidad económica, junto con la variable objetivo que mide cuánto tiempo podría sobrevivir la persona sin ingresos.

---

## 7. Variables

### Variable objetivo (y)

- **`fragilidad_financiera`:** variable construida a partir de la pregunta `P407`, relacionada con el tiempo que una persona podría vivir con sus ahorros o vendiendo sus activos en caso de dejar de recibir ingresos regulares.

La variable será transformada en tres categorías:

| Respuesta original | Categoría para el modelo |
|---|---|
| Una semana / Dos semanas | Fragilidad alta |
| Un mes / Tres meses | Fragilidad media |
| Seis meses / Un año / Más de un año | Fragilidad baja |
| NS/NR | Se excluye antes del entrenamiento |

Después de excluir los registros NS/NR, el dataset de entrenamiento contará con **5.227 registros válidos**.

### Variables de entrada (X)

#### Variables sociodemográficas

- **`edad`:** edad de la persona encuestada.
- **`genero`:** género de la persona encuestada.
- **`ocupacion_principal`:** actividad principal realizada por la persona durante el mes anterior.
- **`tipo_vinculacion_laboral`:** tipo de vinculación en el trabajo o negocio.
- **`nivel_educativo`:** nivel educativo más alto alcanzado.
- **`estrato`:** estrato de la vivienda.
- **`region`:** región del país.
- **`ruralidad`:** clasificación territorial de residencia.

#### Variables de ingresos

- **`ing_salario`:** indica si la persona recibió ingresos por salario.
- **`ing_pension`:** indica si la persona recibió ingresos por pensión.
- **`ing_arriendos`:** indica si recibió ingresos por arriendos o rentas.
- **`ing_honorarios`:** indica si recibió ingresos por honorarios.
- **`ing_ventas`:** indica si recibió ingresos por ventas.
- **`ing_subsidios_gobierno`:** indica si recibió ingresos por subsidios del gobierno.
- **`ing_remesas`:** indica si recibió remesas.
- **`ing_ayuda_familiar`:** indica si recibió ayuda familiar o donaciones.
- **`rango_ingresos_hogar`:** rango de ingresos mensuales del hogar.
- **`frecuencia_ingresos`:** frecuencia con que recibe ingresos.

#### Variables de gastos

- **`rango_gastos_hogar`:** rango de gastos mensuales del hogar.
- **`gasto_arriendo`:** indica si el hogar realiza pagos de arriendo.
- **`gasto_servicios_publicos`:** indica si el hogar paga servicios públicos.
- **`gasto_seguridad_social`:** indica si el hogar realiza pagos de seguridad social.

#### Productos financieros

- **`prod_cuenta_ahorro`:** indica si la persona tiene cuenta de ahorro.
- **`prod_tarjeta_debito`:** indica si tiene tarjeta débito.
- **`prod_monedero_digital`:** indica si usa monedero digital.
- **`prod_cdt`:** indica si tiene CDT.
- **`prod_fondo_inversion`:** indica si tiene fondos de inversión.
- **`prod_fondo_empleados`:** indica si tiene fondo de empleados.
- **`beneficiario_subsidio`:** indica si es beneficiario de subsidio del gobierno.
- **`producto_financiero_mas_usado`:** producto financiero que más utiliza.

#### Crédito y hábitos financieros

- **`solicito_credito`:** indica si solicitó crédito durante el último año.
- **`comp_tiene_plan_financiero`:** indica si la persona tiene un plan financiero.
- **`comp_frecuencia_cumple_plan`:** frecuencia con que cumple su plan financiero.
- **`comp_atraso_pagos`:** frecuencia con la que presenta atraso en pagos.
- **`comp_deuda_mayor_activos`:** percepción sobre si debe más de lo que valen sus activos.
- **`hab_encargado_gastos_hogar`:** indica si se encarga de la mayor parte de los gastos del hogar.
- **`hab_encargado_presupuesto`:** indica si se encarga de que el presupuesto del hogar se cumpla.
- **`hab_usa_app_bancaria`:** indica si usa aplicaciones bancarias o herramientas digitales para el manejo del dinero.

#### Percepción financiera

- **`perc_nunca_tendre_lo_que_quiero`:** nivel en que la persona siente que nunca tendrá lo que desea por su situación financiera.
- **`perc_disfruta_vida_por_dinero`:** nivel en que puede disfrutar la vida por la manera en que maneja su dinero.
- **`perc_confianza_decisiones`:** nivel de confianza en su capacidad para tomar decisiones financieras.
- **`perc_camino_objetivos`:** nivel de acuerdo con estar en camino a cumplir sus objetivos financieros.
- **`perc_deuda_manejable`:** nivel de acuerdo con que su deuda actual es manejable.
- **`perc_control_situacion`:** nivel de acuerdo con tener un alto grado de control sobre su situación financiera.

---

## 8. Usuario final y decisión

- **Usuario final:** Persona adulta colombiana interesada en conocer su nivel de fragilidad financiera ante una posible pérdida de ingresos. También puede ser útil para docentes, orientadores o programas de educación financiera que deseen explicar la importancia del ahorro, la gestión de deudas y la planeación financiera.
- **Decisión que apoyará:** Con base en su clasificación, el usuario podrá identificar si con su situación financiera actual es necesario modificar sus hábitos, y así recibir orientación sobre acciones preventivas específicas para su perfil: construir un fondo de emergencia, reducir deudas, formalizar el ahorro o mejorar hábitos de planeación financiera, antes de que ocurra una emergencia económica.

---

## 9. Implicaciones éticas

**Riesgo 1 — Falsa seguridad o alarma injustificada**

El modelo clasifica a partir de patrones estadísticos de una encuesta de 2022. Una persona podría recibir una clasificación que no refleje con exactitud su situación actual, especialmente si sus condiciones económicas han cambiado. Esto podría generar falsa tranquilidad en personas vulnerables o alarma innecesaria en personas con buena salud financiera.

*Mitigación:* El resultado del dashboard se presentará como orientación informativa, no como diagnóstico financiero certificado. Se incluirá una advertencia explícita recomendando consultar un asesor financiero para decisiones importantes.

**Riesgo 2 — Sesgo por variables socioeconómicas**

El modelo aprende de datos que reflejan desigualdades estructurales del país. Variables como estrato, región y ruralidad pueden llevar al modelo a clasificar con mayor fragilidad a personas de zonas rurales o estratos bajos, no por sus hábitos sino por su contexto socioeconómico histórico.

*Mitigación:* El modelo se usará exclusivamente con fines orientativos e informativos. Los resultados no se utilizarán para negar servicios, discriminar usuarios ni tomar decisiones automatizadas. El dashboard comunicará el resultado como un perfil de riesgo asociado a características observables, no como un juicio sobre la persona.

**Riesgo 3 — Privacidad de los datos del usuario**

La aplicación solicita información financiera y personal al usuario para realizar la clasificación. Existe el riesgo de que esos datos sean almacenados, compartidos o usados con fines distintos al orientativo.

*Mitigación:* La aplicación no solicitará datos personales identificables como nombres, números de identificación, direcciones exactas o información bancaria. Las respuestas del usuario se procesarán únicamente en sesión, sin almacenamiento permanente. Las recomendaciones entregadas serán generales y estarán enfocadas en prevención y educación financiera.

---

## 10. URL del repositorio GitHub

[https://github.com/1531nana/FinBalance](https://github.com/1531nana/FinBalance)