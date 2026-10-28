# Guía para Presentar el Código — CRM Gastronómico

Si el profesor pide ver código (no solo la demo en vivo), no abras archivos al azar. Sigue este orden: cuenta una historia de "problema → decisión → solución", no un recorrido de carpetas.

---

## Orden sugerido para mostrar código (4-5 minutos si te lo piden)

### 1. `backend/app/models/` — el modelo de datos (1 min)
Abre `review.py` y `sentiment.py` juntos. Muestra las relaciones:

> "Una `Reseña` puede tener una `TranscripcionAudio` (si vino de voz) y varios `SentimientoPlatillo` (uno por cada platillo mencionado). Cada `SentimientoPlatillo` tiene sus propios `AtributoMencionado`. Esto es lo que nos permite hacer consultas como 'dame todas las quejas de temperatura del último mes' sin tener que re-procesar texto libre cada vez."

### 2. `backend/app/services/nlp_service.py` — el corazón del análisis (2 min)
Este es el archivo más defendible del proyecto porque pasó por más iteraciones de validación. Muestra, en este orden:

1. **El prompt** (`analyze_review`, la f-string con las reglas): explica que el catálogo se pasa como lista cerrada, no como texto libre, para forzar al LLM a no inventar nombres.
2. **`_apply_guardrails`**: explica los dos guardrails — pertenencia al catálogo, y detección de negación/exclusión. Si preguntan por qué no confiar solo en el LLM, este método es tu respuesta.
3. **`options={"temperature": 0.0}`**: menciona que esto fue clave para que el sistema fuera determinista — lo probaste corriendo la misma entrada 3 veces y comparando resultados idénticos.

> Si te preguntan "¿por qué Python y no todo en el prompt?": "Porque un modelo de 3B es bueno proponiendo, pero no 100% confiable decidiendo con reglas estrictas — delegamos la decisión binaria (¿pertenece al catálogo? ¿hay negación?) a código determinista, que nunca falla ni varía entre corridas."

### 3. `backend/app/services/stt_service.py` — transcripción con sesgo de vocabulario (1 min)
Muestra la construcción del `initial_prompt` a partir del catálogo:

> "Sin esto, Whisper transcribía 'Sopa Azteca' como 'sopasteca'. Inyectando el vocabulario esperado del menú como contexto previo, la confianza subió de ~73% a ~85-90% en nuestras pruebas."

También muestra el manejo de `segment_probs` vacío → `estado_procesamiento: "FALLIDO"`. Es un buen ejemplo de manejo de casos límite que no todos los compañeros van a tener en su proyecto.

### 4. `backend/app/services/ranking_service.py` — la fórmula de Wilson (1 min)
No necesitas explicar la derivación matemática completa, pero sí poder decir:

> "Usamos el límite inferior del intervalo de Wilson al 95% de confianza. Probamos antes una fórmula más simple (media bayesiana con factor de penalización) y la descartamos porque, con datos reales, penalizaba doblemente las reseñas negativas y producía un orden que no tenía sentido comercial — un platillo con una sola reseña superaba a uno con 8 reseñas y 75% de aprobación. El Wilson Score resolvió esa distorsión."

### 5. (Opcional, si hay tiempo) `frontend/src/components/ReviewResultCard.tsx`
Solo si preguntan por el frontend específicamente. Muestra el manejo de los 3 estados: éxito, `FALLIDO` persistido (banner ámbar), y error real de red (tarjeta roja) — es una buena demostración de pensar en casos límite de UX, no solo el camino feliz.

---

## Si te piden "explica esta función" en vivo, sin preparación

Prioriza explicar **qué problema resuelve**, no línea por línea. La estructura que funciona:

1. "Esto existe porque descubrimos que [problema concreto que encontraron en pruebas]."
2. "La solución fue [qué hace la función, en una frase]."
3. "Lo validamos corriendo [la prueba que hicieron] y confirmando [el resultado]."

Ejemplo con `_apply_guardrails`:
> "Esto existe porque el modelo, al ver la palabra 'tacos', a veces la asociaba al único platillo de tacos del catálogo aunque la frase dijera que esos tacos NO estaban en el menú. La solución fue una regla determinista en Python que revisa si el fragmento mencionado tiene palabras de negación/exclusión, y si las tiene, reasigna a 'Sin Clasificar' en vez de confiar en el LLM. Lo validamos con 6 corridas sobre 3 casos de ambigüedad, confirmando 0% de contaminación del catálogo."

---

## Lo que NO debes hacer

- **No improvises el código que no escribiste tú línea por línea** (lo construyó Gravity). Está bien decir "esto lo generó mi agente de codificación, pero yo definí el diseño, revisé cada entrega y rechacé varias versiones antes de aprobarlas" — es honesto y además demuestra criterio.
- **No abras archivos de frontend genéricos** (`App.tsx`, configuración de Vite) a menos que te lo pidan explícitamente — no aportan nada a la evaluación de "Tratamiento de la Información".
- **No te pierdas en la sintaxis de SQLAlchemy o Pydantic** si no te preguntan por eso — el valor está en el pipeline de IA y las decisiones de diseño, no en la mecánica del ORM.
