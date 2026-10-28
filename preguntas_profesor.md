# Preguntas Adicionales del Profesor — CRM Gastronómico

Estas complementan la tabla que ya está en `demo_script.md`. Agrupadas por el tipo de cosa que probablemente le interese evaluar a un profesor de Tratamiento de la Información.

---

## Sobre el pipeline de IA (lo más probable que pregunten)

**¿Por qué un modelo de 3B y no uno más grande?**
> "Porque validamos empíricamente antes de construir: corrimos 6+ casos de prueba contra `llama3.2:3b` con extracción estructurada (JSON Schema vía Ollama), incluyendo casos difíciles de sinónimos y ambigüedad contra un catálogo cerrado. Obtuvimos 100% de JSON válido y 100% de consistencia entre repeticiones con `temperature: 0`. Un modelo más grande habría sido más robusto, pero más lento en CPU — para este volumen de reseñas, el 3B es suficiente y la validación lo demuestra."

**¿Cómo midieron que el sistema realmente funciona, más allá de "se ve bien"?**
> "En cada fase del desarrollo corrimos pruebas de consistencia (misma entrada, múltiples corridas, comparando resultados), pruebas de caso límite (ambigüedad, negación, audio sin voz) y una base de datos de benchmark reseteable para poder repetir el mismo experimento con números limpios y verificables."

**¿Qué pasa si el modelo de Ollama se equivoca y asigna mal un platillo?**
> "Hay una capa de guardrail determinista en Python después del LLM: valida que el platillo sugerido pertenezca al catálogo oficial (si no, cae a 'Sin Clasificar'), y detecta cláusulas de negación/exclusión ('no venían', 'no era') para evitar falsos positivos. El LLM propone, Python decide — no confiamos ciegamente en la salida del modelo."

**¿Por qué Whisper 'base' y no un modelo más preciso?**
> "Con el `initial_prompt` dinámico (inyectando el vocabulario del menú), el modelo 'base' subió su confianza de ~73% a ~85-90% en nuestras pruebas, corrigiendo deformaciones fonéticas como 'sopasteca' → 'Sopa Azteca'. A <1 segundo de latencia en CPU, es suficiente para este caso de uso; si el restaurante creciera o el vocabulario fuera más complejo, subir a 'small' es un cambio de una línea de configuración."

---

## Sobre la arquitectura y diseño de datos

**¿Por qué separaron Reseña, TranscripciónAudio, SentimientoPlatillo y AtributoMencionado en vez de una sola tabla?**
> "Normalización relacional estándar: una reseña puede mencionar varios platillos (uno a uno con Transcripción si vino de audio, uno a muchos con Sentimiento), y cada mención de un platillo puede tener varios atributos. Esto nos permite consultas analíticas eficientes (ej. 'dame todos los atributos negativos de temperatura en los últimos 7 días') sin tener que parsear texto libre cada vez."

**¿Por qué SQLite y no una base de datos más robusta?**
> "Para un MVP de validación de concepto, SQLite no requiere configuración ni servidor adicional, y SQLAlchemy nos permite migrar a PostgreSQL cambiando solo la cadena de conexión si el proyecto escalara a producción real."

**¿Qué pasa si dos reseñas llegan al mismo tiempo (concurrencia)?**
> *(Pregunta trampa típica — sé honesto si no lo probaron)*: "No hicimos pruebas de carga concurrente explícitas; para el alcance de este proyecto (demo de clase, no producción), no era prioridad. En un entorno real, SQLite tiene limitaciones de escritura concurrente conocidas y sería de las primeras cosas a resolver migrando a PostgreSQL."

---

## Sobre los resultados y la fórmula de ranking

**¿Por qué el Wilson Score y no un promedio ponderado simple?**
> "Porque el promedio simple deja que una sola reseña de 5 estrellas supere a un platillo con 50 reseñas positivas y 2 negativas. El Wilson Score Interval calcula un límite inferior de confianza estadística: con pocas muestras es conservador, y con más evidencia converge a la satisfacción real. De hecho, descartamos una primera fórmula (media bayesiana × factor de penalización) porque penalizaba las reseñas negativas dos veces — lo detectamos probando con datos reales antes de quedarnos con la versión final."

**¿Qué tan confiable es el Wilson Score con muestras tan chicas (1-2 reseñas)?**
> "Es precisamente para eso que existe: con `n` bajo, el intervalo de confianza es amplio y el límite inferior es bajo — por diseño, no deja que un platillo con una sola reseña se dispare al top. Con más datos reales, el ranking se vuelve más confiable de forma natural, sin tener que ajustar nada manualmente."

---

## Sobre las limitaciones (ser honesto aquí da mejor impresión que inventar perfección)

**¿Cuáles son las limitaciones conocidas del sistema?**
> "Tres principales: (1) el guardrail de negación usa una lista de palabras clave, así que frases muy indirectas pueden escapársele; (2) un modelo de 3B puede sobre-asociar menciones genéricas con el único platillo que comparte una palabra clave, aunque el contexto lo contradiga — lo mitigamos con el guardrail, no lo eliminamos del todo; (3) no probamos con volumen alto de datos simultáneos ni con acentos/dialectos distintos al usado en las pruebas."

**¿Cómo escalarían esto a un restaurante real con cientos de reseñas diarias?**
> "Lo primero sería migrar de SQLite a PostgreSQL por concurrencia. Después, evaluar si el modelo de 3B sigue siendo preciso con mayor diversidad de lenguaje, o si conviene subir de tamaño. Y añadir un job asíncrono para el pipeline de IA en vez de procesarlo síncronamente en el request, para no bloquear al usuario mientras Whisper/Ollama corren."

---

## Preguntas de proceso (puede que pregunten cómo trabajaste, no solo qué construiste)

**¿Usaste IA para construir esto? ¿Cómo garantizas que entiendes lo que hiciste?**
> Sé directo y sin pena: "Sí, usé Gravity (Google Antigravity) como agente de codificación, y Claude como revisor de cada entrega antes de aprobar que avanzara. No acepté nada a ciegas — varias veces rechacé planes o reportes porque los datos no cuadraban (por ejemplo, un ranking con números que no correspondían al dataset de prueba, o un plan que decía 'ejecutado' pero no tenía evidencia real), y pedí que corrigieran antes de seguir.
