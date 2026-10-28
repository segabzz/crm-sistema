# 🎙️ Guion de Demostración para Presentación de Clase (5 a 7 Minutos)

**Proyecto:** CRM Gastronómico con IA Local & Wilson Score  
**Audiencia:** Profesor y compañeros de clase  
**Objetivo:** Demostrar una arquitectura de software completa, decisiones de ingeniería justificadas (costo $0, privacidad, estadística rigurosa) y fluidez visual en vivo.

---

## ⏱️ Cronograma Minuto a Minuto

```
[0:00 - 1:00]  Introducción al problema y propuesta de valor
[1:00 - 2:30]  Demo en Vivo: Ingesta Multimodal (Texto + Audio WebM)
[2:30 - 3:30]  Decisión de Negocio: Resiliencia ante audio sin voz (FALLIDO)
[3:30 - 5:00]  Demo en Vivo: Dashboard, Recharts y Explicación del Wilson Score
[5:00 - 6:00]  Demo en Vivo: Catálogo con Filtros y Reset Administrativo
[6:00 - 7:00]  Conclusiones de Arquitectura y Preguntas
```

---

## 📋 Preparación Previa (1 minuto antes de exponer)

1. Verifica que Ollama esté activo en tu máquina:
   ```bash
   ollama list   # Debe mostrar llama3.2:latest
   ```
2. Inicia los dos servidores en terminales separadas:
   * **Terminal 1 (Backend):**
     ```pwsh
     python -m uvicorn app.main:app --host 127.0.0.1 --port 8000 --app-dir backend --reload
     ```
   * **Terminal 2 (Frontend):**
     ```pwsh
     cd frontend
     npm run dev
     ```
3. Abre en el navegador: `http://localhost:5173`
4. Ve a la pestaña **"Catálogo & Admin"** y haz clic en **"Reiniciar Base de Datos"** -> Confirmar.  
   *(Esto asegura que inicias la demo con el sistema completamente limpio para mostrar la ingesta en vivo).*

---

## 🎬 Guion de Exposición

### 1. El Problema y la Propuesta de Valor (0:00 - 1:00)
> *"Buenos días/tardes. En la industria restaurantera, el 70% del feedback de los comensales se da de forma verbal al mesero o se pierde en reseñas caóticas de Google Maps. Los sistemas tradicionales usan promedios de estrellas ingenuos que engañan al negocio y dependen de APIs en la nube que cobran por token y vulneran la privacidad del cliente.*
> 
> *Para resolver esto, diseñamos un CRM Gastronómico con **IA 100% Local y Privada** (usando Faster-Whisper para transcripción y Llama 3.2 vía Ollama para extracción estructurada) y un algoritmo de reputación basado en **Wilson Score Interval** que previene sesgos estadísticos. Todo corre en hardware estándar con **costo operativo cero**."*

---

### 2. Demo en Vivo: Ingesta Multimodal (1:00 - 2:30)
*(Haz clic en la pestaña **"Ingesta de Reseñas"**).*

> *"Veamos cómo capturamos la información. El sistema soporta texto manual y notas de voz directamente desde el micrófono de la mesa."*

* **Prueba de Texto Mixto:**
  1. Haz clic en el preset rápido:  
     `"La Sopa Azteca estuvo deliciosa y muy caliente, pero el Ribeye a la Parrilla llegó frío y un poco salado."`
  2. Asigna calificación de 3 estrellas y presiona **"Procesar Reseña de Texto"**.
  3. **Qué señalar en pantalla:**
     > *"En menos de 2 segundos, Llama 3.2 aisló dos platillos independientes en el mismo texto: la Sopa Azteca con polaridad POSITIVA (+1.0) y atributo `temperatura: caliente`, y el Ribeye con polaridad NEGATIVA (-1.0) detectando dos problemas operativos: `temperatura: frío` y `sabor: un poco salado`. Todo anclado automáticamente al catálogo oficial del restaurante."*

* **Prueba de Audio / Micrófono:**
  1. Cambia a la pestaña **"Audio / Voz"**.
  2. Presiona **"Iniciar Grabación"**, habla 3 segundos:  
     *"Los tacos de res braseada estuvieron increíbles y el agua de horchata artesanal súper fresca."*
  3. Detén la grabación y presiona **"Transcribir y Procesar Audio"**.
  4. **Qué señalar en pantalla:**
     > *"El navegador capturó audio nativo WebM/Opus, Faster-Whisper lo transcribió localmente con una confianza superior al 85% —utilizando un sesgo de vocabulario dinámico inyectado desde el menú— y Llama 3.2 extrajo los sentimientos en tiempo real."*

---

### 3. Decisión Técnica: Resiliencia ante Audio Silencioso (2:30 - 3:30)
> *"Un reto crítico en sistemas con IA de voz es: ¿qué pasa si el comensal no habla o se graba puro ruido de fondo?"*

* **Muestra o explica el caso:**
  > *"Si un audio no contiene voz inteligible, no lanzamos un error 500 que colapse la aplicación o deseche el evento. El backend persiste la reseña con estado `FALLIDO` y confianza 0.0, y en el frontend mostramos un banner preventivo ámbar informando que el audio fue silencioso. Esto le da trazabilidad operativa al gerente para saber cuántas interacciones fallaron sin alterar el ranking de la cocina."*

---

### 4. Demo en Vivo: Dashboard & Explicación de Wilson Score (3:30 - 5:00)
*(Haz clic en la pestaña **"Dashboard & Ranking"**).*

> *"Ahora pasamos al centro de comando gerencial. Aquí vemos las métricas consolidadas en tiempo real."*

* **Explicación del Algoritmo (Punto fuerte de evaluación):**
  > *"Si usáramos un promedio clásico, un platillo con 1 sola reseña de 5 estrellas estaría en el puesto #1 del menú, superando a un platillo estrella con 100 reseñas y 95% de satisfacción. Esto es un error estadístico grave.*
  > 
  > *Por eso implementamos el **Wilson Score Interval (Lower Bound)** con un 95% de confianza ($z = 1.96$). Este algoritmo calcula el límite inferior de satisfacción binomial: castiga de forma conservadora a los platillos con pocas muestras y premia la consistencia a gran volumen."*

* **Visualización de Alertas y Gráficas Recharts:**
  > *"En la parte superior, el sistema activa automáticamente una alerta de **Platillos en Riesgo** señalando al Ribeye por acumulación de valoraciones negativas.*
  > 
  > *Más abajo, Recharts nos muestra dos gráficas reactivas: la comparativa del Wilson Score normalizado por platillo, y la distribución apilada de atributos, donde cocina puede ver exactamente que el 100% de las quejas son por **temperatura fría** y no por calidad del producto. Esto permite tomar decisiones operativas de inmediato."*

---

### 5. Catálogo Oficial & Reinicio Administrativo (5:00 - 6:00)
*(Haz clic en la pestaña **"Catálogo & Admin"**).*

* **Paso en Vivo — Filtrado por Categoría:**
  1. Haz clic en el botón de filtro **"Postres"**.
  2. **Qué señalar en pantalla:**
     > *"Miren cómo la grilla se filtra reactivamente para mostrar únicamente el 'Pastel Tres Leches' ($95.00 MXN) con su descripción y estado activo. Si pasamos a 'Cortes', aparece de inmediato el 'Ribeye a la Parrilla'. Este catálogo es consumido dinámicamente por Llama 3.2 y Faster-Whisper para anclaje de entidades."*
  3. Haz clic de nuevo en **"Todos los Platillos"** para restablecer la grilla completa de 7 platillos.

* **Paso en Vivo — Demostración del Reset Administrativo:**
  1. Presiona el botón rojo **"Reiniciar Base de Datos"**.
  2. Muestra el modal de confirmación y presiona **"Confirmar Reinicio"**.
  3. Cambia a la pestaña **"Dashboard & Ranking"** y señala:
     > *"Con un solo clic, el sistema ejecuta un reset relacional limpio: la base de datos vuelve a 0 menciones y 0 alertas en el Dashboard, mientras el catálogo de los 7 platillos permanece 100% intacto, permitiendo reiniciar pruebas y benchmarks sin alterar esquemas ni reiniciar servidores."*

---

### 6. Cierre y Preguntas (6:00 - 7:00)

> *"En resumen, logramos una arquitectura moderna (React 19 + Tailwind v4 en el frontend, FastAPI + SQLite en el backend) que resuelve un problema de negocio real combinando modelos de lenguaje locales, reconocimiento de voz y estadística inferencial con costo cero de operación y privacidad garantizada.*
> 
> *Quedamos a su disposición para cualquier pregunta. Muchas gracias."*

---

## 💡 Preguntas Típicas del Profesor y Cómo Responder

| Pregunta Esperada | Respuesta Sugerida |
| :--- | :--- |
| **¿Por qué no usaron OpenAI GPT-4o o Claude?** | *"Por dos razones: costo y privacidad. Un restaurante medio procesa cientos de interacciones al mes; un modelo de pago por token vuelve insostenible el margen. Además, los comensales no autorizan el envío de sus grabaciones a servidores corporativos externos."* |
| **¿Cómo aseguran que Whisper reconozca nombres difíciles como 'Ribeye'?** | *"Inyectamos dinámicamente los nombres del catálogo como `initial_prompt` a Faster-Whisper. Esto sesga el espacio de probabilidades del decodificador hacia el vocabulario gastronómico exacto."* |
| **¿Cómo manejan si el LLM se confunde con una negación como 'no estuvo malo'?** | *"Contamos con un Guardrail híbrido sintáctico previo a la persistencia. Si el comensal usó una estructura de doble negación o duda, el guardrail analiza la cláusula específica y corrige la polaridad con una justificación auditable."* |
