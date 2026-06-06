# Análisis Cualitativo del Dataset

## 1. Descripción general

El dataset utilizado corresponde a los microdatos de la **Encuesta de Demanda Financiera 2022**, una encuesta aplicada a personas adultas colombianas con el propósito de conocer sus comportamientos, percepciones y condiciones relacionadas con el acceso y uso de servicios financieros. Fue recopilada por el Centro Nacional de Consultoría por encargo de Banca de las Oportunidades — programa administrado por BANCOLDEX — durante el trabajo de campo realizado entre el 5 de abril y el 27 de mayo de 2022, mediante encuesta presencial en municipios de todas las regiones del país.

Para este proyecto se seleccionó un subconjunto de variables relacionadas con ingresos, gastos, ocupación, educación, productos financieros, ahorro, crédito, hábitos financieros y percepción de estabilidad económica. Estas variables permiten analizar la fragilidad financiera de una persona ante una posible pérdida de ingresos.

El fenómeno que captura el dataset es relevante porque permite observar qué tan preparada está una persona para enfrentar una emergencia económica. En particular, el proyecto busca clasificar el nivel de fragilidad financiera de una persona adulta colombiana en tres categorías: **alta, media o baja**.

El dataset fue puesto a disposición del estudiante por el docente del diplomado con fines exclusivamente académicos y no de distribución.

---

## 2. Estructura del dataset

Después de cargar y seleccionar las variables necesarias para el proyecto, el dataset quedó compuesto por:

- **5.610 registros**
- **45 columnas**
- **44 variables categóricas**
- **1 variable numérica**, correspondiente a la edad

La mayoría de las variables son de tipo categórico porque provienen de respuestas de encuesta, por ejemplo: nivel educativo, ocupación, rango de ingresos, rango de gastos, tenencia de productos financieros, solicitud de crédito y hábitos financieros.

La variable numérica principal es `edad`, con los siguientes valores generales:

- Edad mínima: **18 años**
- Edad máxima: **76 años**
- Edad promedio: **42,2 años**

Esto indica que la muestra incluye personas adultas en diferentes etapas de vida, lo cual es útil para analizar la fragilidad financiera en distintos perfiles poblacionales.

---

## 3. Variable objetivo

La variable objetivo del proyecto es:

**`fragilidad_financiera`**

Esta variable proviene de la pregunta `P407`, relacionada con el tiempo que una persona podría vivir con sus ahorros o vendiendo sus activos en caso de dejar de recibir ingresos regulares.

Originalmente, la variable tiene las siguientes categorías:

- Una semana
- Dos semanas
- Un mes
- Tres meses
- Seis meses
- Un año
- Más de un año
- NS/NR

Para efectos del modelo predictivo, esta variable se transformará en una clasificación de tres niveles:

| Categoría original | Nueva categoría |
|---|---|
| Una semana / Dos semanas | Fragilidad alta |
| Un mes / Tres meses | Fragilidad media |
| Seis meses / Un año / Más de un año | Fragilidad baja |
| NS/NR | Se excluirá antes del entrenamiento |

La distribución inicial de la variable objetivo es la siguiente:

- **Fragilidad alta:** 2.006 personas, equivalente al **35,8 %**
- **Fragilidad media:** 2.056 personas, equivalente al **36,6 %**
- **Fragilidad baja:** 1.165 personas, equivalente al **20,8 %**
- **NS/NR:** 383 personas, equivalente al **6,8 %**

Después de excluir los 383 registros NS/NR, el dataset de entrenamiento contará con **5.227 registros válidos**.

Esta distribución muestra que las clases alta y media tienen una presencia similar en el dataset, mientras que la fragilidad baja tiene menor representación. Por esta razón, será importante usar una métrica como **F1-score macro**, ya que permite evaluar mejor el desempeño del modelo cuando existen diferencias en la cantidad de registros por clase.

---

## 4. Variables de entrada relevantes

Las variables de entrada seleccionadas buscan describir el perfil económico, social y financiero de cada persona. Se agrupan en las siguientes dimensiones:

### 4.1. Variables sociodemográficas

Incluyen edad, género, ocupación principal, tipo de vinculación laboral, nivel educativo, estrato, región y ruralidad.

Estas variables son importantes porque la fragilidad financiera puede variar según el contexto de vida de la persona. Por ejemplo, no es igual la exposición económica de una persona empleada formalmente que la de una persona independiente, desempleada o dedicada a oficios del hogar.

Algunos resultados relevantes son:

- El **54,8 %** de la muestra corresponde a mujeres.
- El **68,7 %** tiene nivel educativo de secundaria o inferior.
- El **54,9 %** pertenece a ciudades y aglomeraciones urbanas.

Estos datos muestran que el dataset incluye una población diversa, aunque con una alta participación de personas con educación básica y media.

### 4.2. Variables de ingresos

Se incluyen variables como ingresos por salario, pensión, arriendos, honorarios, ventas, subsidios, remesas, ayudas familiares, rango de ingresos del hogar y frecuencia de ingresos.

Estas variables son relevantes porque la estabilidad, frecuencia y fuente del ingreso influyen directamente en la capacidad de una persona para enfrentar una pérdida económica.

Un resultado importante es que el **58,9 %** de las personas pertenece a hogares con ingresos inferiores a $1.000.000 mensuales. Esto indica que una proporción considerable de la muestra puede tener una capacidad limitada para acumular ahorros o crear un fondo de emergencia.

### 4.3. Variables de gastos

Se incluyen variables relacionadas con el rango de gastos del hogar y pagos como arriendo, servicios públicos y seguridad social.

Estas variables permiten aproximar la presión económica mensual del hogar. Una persona puede tener ingresos, pero si sus gastos son altos o cercanos a sus ingresos, su capacidad para resistir una emergencia económica puede verse reducida.

### 4.4. Productos financieros

Se incluyen variables como cuenta de ahorro, tarjeta débito, monedero digital, CDT, fondos de inversión, fondo de empleados, subsidios y producto financiero más usado.

Estas variables permiten identificar el nivel de inclusión financiera formal de la persona. En el dataset se observa que:

- El **35,6 %** tiene cuenta de ahorro.
- El **39,5 %** tiene monedero digital.
- Solo el **1,7 %** tiene CDT.

Esto sugiere que, aunque existe uso de productos financieros básicos o digitales, el uso de productos de ahorro o inversión más estructurados es muy bajo.

### 4.5. Crédito y endeudamiento

Se incluye la variable sobre solicitud de crédito en el último año, así como variables de percepción sobre el nivel de deuda relativo a los activos y la manejabilidad de la deuda actual.

En la muestra:

- El **16,6 %** solicitó crédito en el último año.
- La mayoría indicó que no solicitó crédito y tampoco tiene otros créditos activos.

El crédito puede tener una doble interpretación. Por un lado, puede representar acceso financiero. Por otro lado, si se usa para cubrir gastos básicos o emergencias, puede ser una señal de vulnerabilidad económica.

### 4.6. Hábitos financieros

Se incluyen variables como tener un plan financiero, encargarse del presupuesto del hogar, usar aplicaciones bancarias y cumplir con el plan de ingresos y gastos.

Estas variables son importantes porque la fragilidad financiera no depende únicamente de los ingresos, sino también de la forma en que una persona administra su dinero.

Algunos resultados relevantes son:

- El **60,2 %** afirma tener un plan financiero.
- El **19,1 %** presenta atrasos frecuentes en pagos.
- El **60,0 %** nunca o casi nunca se atrasa en sus pagos.

Estos resultados muestran que existen comportamientos financieros positivos en una parte de la muestra, pero también señales de riesgo en personas con atrasos frecuentes.

---

## 5. Calidad de los datos

El dataset no presenta registros duplicados, lo cual es positivo para el análisis, ya que reduce el riesgo de sobrerrepresentar observaciones repetidas en el entrenamiento del modelo.

En cuanto a valores nulos, se identificaron cuatro variables con datos faltantes:

| Variable | Nulos | Porcentaje |
|---|---:|---:|
| tipo_vinculacion_laboral | 2.804 | 49,98 % |
| producto_financiero_mas_usado | 2.342 | 41,75 % |
| beneficiario_subsidio | 2.329 | 41,52 % |
| comp_frecuencia_cumple_plan | 2.231 | 39,77 % |

Estos nulos no necesariamente representan errores de calidad. En algunos casos pueden deberse a preguntas que no aplicaban para todas las personas. Por ejemplo, `tipo_vinculacion_laboral` puede estar vacío para personas que no estaban trabajando, y `comp_frecuencia_cumple_plan` puede estar vacío para personas que no tienen un plan financiero.

Por esta razón, se decidió imputar estos valores con categorías interpretables:

- `tipo_vinculacion_laboral`: No aplica
- `beneficiario_subsidio`: No informa
- `producto_financiero_mas_usado`: No informa
- `comp_frecuencia_cumple_plan`: No tiene plan

Después de aplicar estas imputaciones, el dataset quedó con **cero valores nulos en las 45 columnas**, lo que permite entrenar el modelo sin necesidad de eliminar registros adicionales.

---

## 6. Pertinencia del dataset

El dataset es pertinente para responder la pregunta analítica porque contiene tanto la variable objetivo como variables explicativas relacionadas con la situación financiera de las personas.

La variable objetivo `fragilidad_financiera` permite medir la capacidad de una persona para sostenerse ante la pérdida de ingresos. Además, las variables de entrada permiten describir factores que pueden influir en esa fragilidad, como ingresos, gastos, empleo, educación, productos financieros, crédito y hábitos de manejo del dinero.

Por tanto, el dataset sí permite abordar una tarea de clasificación multiclase, en la cual el modelo buscará clasificar a una persona en una de tres categorías: fragilidad alta, media o baja.

La pregunta analítica y el dataset están alineados porque:

- Existe una variable objetivo identificada y disponible directamente en los datos.
- Las variables de entrada están disponibles en el dataset y son coherentes con la pregunta.
- La tarea es medible mediante F1-score macro.
- El resultado puede apoyar una decisión concreta: orientar acciones preventivas frente a emergencias económicas.

---

## 7. Limitaciones del dataset

Aunque el dataset es útil para el proyecto, presenta algunas limitaciones que deben tenerse en cuenta:

### 7.1. Información reportada por los encuestados

Una limitación del dataset es que las respuestas provienen directamente de lo que las personas encuestadas declararon. Esto significa que variables como ingresos, gastos, deudas, hábitos financieros o capacidad para sostenerse sin ingresos no fueron verificadas con documentos, extractos bancarios o registros oficiales. Por esta razón, pueden existir errores de memoria, diferencias de interpretación o respuestas influenciadas por la percepción personal de cada encuestado.

### 7.2. Variables en rangos

Los ingresos y gastos no se presentan como valores exactos, sino como rangos. Esto limita la posibilidad de calcular indicadores financieros precisos, como capacidad de ahorro exacta o relación ingreso-gasto.

### 7.3. Valores NS/NR en la variable objetivo

Algunas variables contienen respuestas como "No sabe" o "No responde". En particular, la variable objetivo tiene 383 registros con NS/NR, equivalentes al 6,8 % de la muestra. Estos registros se excluirán antes del entrenamiento, dejando 5.227 registros válidos para el modelo.

### 7.4. Datos del año 2022

La encuesta corresponde al año 2022. Aunque sigue siendo útil para el análisis, las condiciones económicas pueden haber cambiado por inflación, empleo, tasas de interés o cambios en el uso de productos financieros digitales.

### 7.5. Alta informalidad laboral

El 49,98 % de nulos en `tipo_vinculacion_laboral` refleja que casi la mitad de los encuestados no tiene vinculación laboral formal. Aunque se imputó como "No aplica", esta variable puede tener poder predictivo limitado en la población informal.

### 7.6. Posible sesgo de representación

Aunque el dataset tiene más de 5.500 registros, no necesariamente representa con igual fuerza a todos los grupos poblacionales. Por ejemplo, hay diferencias por región, ruralidad, nivel educativo y estrato que pueden influir en el modelo.

### 7.7. Desbalance moderado entre clases

La clase de fragilidad baja (20,8 %) tiene significativamente menos registros que las clases alta y media. Esto requerirá monitorear el desempeño por clase durante el entrenamiento y posiblemente aplicar técnicas de balanceo como pesos de clase en el modelo.

### 7.8. Riesgo ético

El modelo no debe usarse para excluir, negar servicios o tomar decisiones financieras automatizadas sobre personas. Su uso debe ser orientativo y educativo, mostrando alertas y recomendaciones generales, no juicios definitivos sobre la situación económica del usuario.

---

## 8. Conclusión del análisis cualitativo

El dataset seleccionado es adecuado para el proyecto porque contiene una variable objetivo clara y variables explicativas coherentes con la pregunta analítica. La estructura de 5.610 registros y 45 variables es manejable para el alcance del diplomado.

La variable `fragilidad_financiera` permite construir una clasificación en tres niveles: alta, media y baja. Además, la distribución de clases muestra que existe suficiente cantidad de registros para entrenar un modelo inicial, aunque será necesario revisar el desbalance de clases y justificar el uso de F1-score macro como métrica principal.

En términos de calidad, el dataset no tiene registros duplicados y los valores nulos se concentran en pocas columnas. Estos nulos fueron tratados mediante categorías como "No aplica", "No informa" o "No tiene plan", según el sentido de cada pregunta, dejando el dataset completamente limpio para el modelado.

En conclusión, el dataset permite responder la pregunta analítica formulada y es pertinente para desarrollar una aplicación web analítica que oriente a las personas sobre su nivel de fragilidad financiera ante una posible pérdida de ingresos.