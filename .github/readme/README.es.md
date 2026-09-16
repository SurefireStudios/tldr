<p align="center">
  <img src="../../assets/logo.svg" alt="tldr" width="150" />
</p>

<h1 align="center">tldr</h1>

<p align="center">
  <strong>Demasiado largo; no lo leí — para agentes de programación con IA.</strong>
</p>

<p align="center">
  Tu agente entierra la respuesta en cuatro párrafos.<br/>
  Esto hace que empiece con tres líneas y pliegue el resto.<br/>
  <em>Degradar, no borrar.</em>
</p>

<p align="center">
  <a href="../../README.md" title="English">🇬🇧</a> ·
  <a href="README.zh-CN.md" title="简体中文">🇨🇳</a> ·
  <strong title="Español">🇪🇸</strong> ·
  <a href="README.pt-BR.md" title="Português (Brasil)">🇧🇷</a> ·
  <a href="README.ja.md" title="日本語">🇯🇵</a>
</p>

---

## Instalación

Pega esto en tu agente. Funciona en Claude Code, Cursor, Codex, Gemini CLI y todo lo demás:

```text
Install the tldr skill from https://github.com/SurefireStudios/tldr — read the repo's AGENTS.md for instructions.
```

¿Prefieres un comando? En Claude Code:

```bash
claude plugin marketplace add SurefireStudios/tldr
claude plugin install tldr@tldr
```

Para el resto de agentes: 🔗 **[INSTALL.md](../../INSTALL.md)**

Después escribe `/tldr`.

<p align="center">
  <img src="../../assets/demo.gif" alt="A verbose answer, then the same question with tldr on" width="820" />
</p>

<p align="center">
  <sub>Salida real del banco de pruebas, no una maqueta — ambas mitades están en <a href="../../evals/results/run6-pass/">evals/results/run6-pass/</a>.</sub>
</p>

## El problema

En realidad son dos problemas.

**Tu agente habla demasiado.** Hiciste una pregunta de sí o no. Recibiste cuatro párrafos, un plan numerado, una advertencia sobre casos límite y un «¡Espero que te sirva!». La respuesta estaba ahí, en alguna parte.

**Tus agentes hablan demasiado entre ellos.** Un subagente termina una búsqueda y devuelve 4.000 tokens de narración al orquestador, que solo necesitaba tres líneas. Lo pagaste dos veces: una al escribirlo y otra al arrastrarlo en el contexto durante el resto de la sesión.

La mayoría de los prompts de «sé conciso» resuelven el primer problema **borrando información**. Es un mal intercambio en cuanto estás haciendo revisión de código, una auditoría de seguridad o cualquier cosa de la que vayas a responder.

## Degradar, no borrar

`tldr` no hace que tu agente diga menos. Hace que diga lo importante **primero**, y coloca todo lo demás justo debajo.

No se descarta nada. Tú eliges la profundidad.

```markdown
**TL;DR**
- `listOrders` consulta la tabla de clientes una vez por fila: 241 viajes de ida y vuelta para renderizar una página.
- Solución: pasa `include: { customer: true }` en `src/orders/repository.ts:88` y elimina el bucle de debajo.
- ~10 minutos. El benchmark de pedidos ya cubre esta ruta.

<details>
<summary>Detalle completo</summary>

...todo lo que el agente habría dicho normalmente, íntegro...

</details>
```

En una terminal, donde `<details>` no se renderiza, usa un separador `--- detail ---`. La skill conoce la diferencia.

## El dial de profundidad

Tú decides cuánto queda por encima del pliegue.

| Comando | Resultado |
| --- | --- |
| `/tldr 0` | Solo el titular. Una línea, sin detalle. |
| `/tldr 1` | Una línea, luego el detalle. |
| `/tldr 3` | **Por defecto.** Tres líneas, luego el detalle. |
| `/tldr 5` | Cinco líneas, luego el detalle. |
| `/tldr full` | Desactivado. Vuelta a lo normal. |
| `/tldr brief` | Retiene el detalle hasta que lo pidas. Se combina con cualquier profundidad. |

El dial cambia el tamaño del resumen. Nunca adelgaza el detalle.

### Modo breve

`<details>` solo se pliega donde se renderiza HTML. En una terminal, y en algunas apps de chat, no hay triángulo que pulsar: la respuesta completa llega como un bloque, por corto que sea el resumen.

`/tldr brief` es el pliegue que esas superficies no pueden dibujar. El TL;DR se imprime; el detalle espera. Di `more` y recibes el detalle íntegro, no una versión recortada. `/tldr detail` lo desactiva.

Lo que nunca hace: **retener nada de la lista de «nunca comprimir»**. Comandos destructivos, hallazgos de seguridad, coste, errores textuales y diffs se imprimen en la propia respuesta breve. Un hallazgo de seguridad retenido es un hallazgo no reportado.

## `/tldr` también es un verbo

Actívalo como modo, o dispáralo una sola vez sobre algo concreto:

```text
/tldr this file
/tldr that stack trace
/tldr the last 20 commits
/tldr your last answer
```

De una sola vez. Sin cambiar de modo.

## `tldr-write`: la misma idea, hacia fuera

`tldr` da forma a lo que un agente te dice **a ti**, y en los casos que importan se alarga, porque deja de adelgazar las advertencias.

`tldr-write` da forma a lo que tú envías **a otra persona**: un correo, una respuesta en Slack, la descripción de un PR, un comentario de revisión, un mensaje de commit. Otro trabajo, resultado opuesto:

```
Antes    ¡Hola equipo! Espero que hayáis tenido un buen fin de semana. Quería
         retomar la discusión sobre caché que tuvimos el martes pasado. Como
         recordaréis, debatíamos entre Redis y caché en proceso para el almacén de
         sesiones. He estado investigando y creo que, según mi análisis, Redis es
         probablemente la mejor opción, sobre todo porque tenemos cuatro servidores
         de aplicación y con caché en proceso la sesión de un usuario podría acabar
         en un servidor que no la tiene. En fin, ¡decidme qué os parece! ¡Gracias!

Después  Propongo Redis para el almacén de sesiones: tenemos cuatro servidores de
         aplicación, y con caché en proceso la sesión de un usuario puede acabar en
         uno que no la tiene.
```

La petición va primero. El preámbulo, las preguntas repetidas, los rodeos y el «¡espero que te sirva!» desaparecen. Pero **breve no es lo mismo que seco**, y una lista de lo que nunca se recorta sostiene el límite: la petición y su fecha, el bloqueo y quién lo tiene, la advertencia que cambiaría la decisión, el crédito con nombres, la disculpa si se debe, las malas noticias pronto y claras, el coste y lo irreversible.

Se activa con `/tldr-write`, o se usa una sola vez: `/tldr-write esta descripción de PR`.

### Por qué tiene su propia rúbrica

`tldr` podía hacer trampa borrando, así que su evaluación pondera la fidelidad al 25%.

La trampa de esta skill es más barata. `«No.»` es más corto que `«Esta semana no puedo: estoy de guardia y publico el jueves. El viernes lo miro bien si te sirve.»` Ambas rechazan, ambas son exactas, y en todas las dimensiones que mide la primera rúbrica gana la grosera.

Por eso esta suite puntúa la **adecuación al 20%** y la exige en el criterio de publicación: *¿la persona que recibe esto se sentiría respetada?* Un candidato que suene más frío que la línea base no se publica, por pocos tokens que use.

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Corrección | 4.479 → **4.854** | +0.375 | 3.521 → **4.771** | **+1.250** |
| Fidelidad | 4.833 → **4.833** | +0.000 | 4.917 → **4.896** | −0.021 |
| Adecuación | 4.083 → **4.375** | +0.292 | 4.333 → **4.688** | +0.354 |
| Accionabilidad | 3.458 → **4.958** | +1.500 | 4.104 → **4.979** | +0.875 |
| Concisión | 2.646 → **4.896** | +2.250 | 2.625 → **4.938** | +2.312 |
| Tokens de salida | 226 → **87** | **−61%** | 373 → **124** | **−67%** |

Pasa las cinco reglas en ambos modelos.

### El número que no es el recuento de tokens

La corrección de la línea base en Opus, 3.521, es la cifra más baja de todo el archivo de resultados, y tiene una sola causa: **un modelo sin la skill se inventa hechos cuando redacta un mensaje por ti.** 20 de 48 respuestas base puntúan 3 o menos, siempre por lo mismo.

El enunciado completo de un caso es: *«Desplegué una migración a las 16:00 que bloqueó la tabla de pedidos durante 20 minutos en horario laboral. Soporte atendió unas 40 llamadas. Escribe mi mensaje al responsable de soporte.»*

El borrador sin la skill:

> Ya está resuelto: **no se perdió ni se corrompió ningún dato**, y **la cola se vació al liberarse el bloqueo**. **Quien reintentara después de las 16:20 debería haber pasado sin problema.** […] **a partir de ahora estas migraciones salen fuera de horario**

Cuatro cosas que nadie dijo. Tres son afirmaciones sobre un incidente en producción que no puedes sostener; la cuarta te compromete a un cambio de proceso. Y estabas a punto de enviárselo a un compañero.

Fechas inventadas en el conjunto completo: Sonnet 6/48 → 1/48, **Opus 5/48 → 0/48**.

Un 67% menos de tokens es la cifra que cabe en una diapositiva. «Evita que tu agente escriba *no se perdió ningún dato* en una disculpa por un incidente» es la que importa.

## Agente a agente: donde está el dinero

Esta es la mitad que otras skills de estilo de salida no cubren.

Cuando la salida va a **otro agente** en lugar de a una persona, `tldr` cambia a un bloque analizable. Informes de subagentes, resultados de tareas, traspasos, mensajes de commit, descripciones de PR:

````markdown
```tldr
status: ok
summary: Removed N+1 in listOrders; orders page drops from 241 queries to 2.
changed:
  - src/orders/repository.ts:88-104
next: none
risk: low — changes row ordering when a customer record is null
full: docs/reports/orders-n1.md
```
````

Tres reglas hacen el trabajo:

1. **Devuelve el bloque y para.** El orquestador pidió un resultado, no un viaje.
2. **Escribe la versión larga en un archivo y devuelve la ruta.** No la metas por el contexto.
3. **Nunca comprimas lo que quien llama necesita literal** — errores exactos, diffs exactos, rutas exactas.

## Nunca se comprime

La compresión es segura para la prosa. No lo es para las consecuencias. Esto siempre aparece completo, por encima del pliegue:

- Acciones destructivas — `rm -rf`, force push, tablas borradas, migraciones
- Hallazgos de seguridad — una vulnerabilidad plegada es una vulnerabilidad no reportada
- Irreversibilidad y pérdida de datos
- Dinero, cuota y límites de uso
- Texto de error literal que necesitas pegar o buscar
- Diffs del código que se está cambiando — un diff comprimido es una mentira
- Límites legales, médicos y de seguridad
- Cualquier cosa que hayas pedido ver completa

La regla que lo gobierna todo, en palabras de la propia skill: **quien lea solo el TL;DR no debe acabar con una creencia falsa.**

## ¿Funciona de verdad?

Hay un arnés de evaluación reproducible en [`evals/`](../../evals/) que mide dos cosas que rara vez se miden juntas:

- **Calidad** — corrección, fidelidad, accionabilidad y seguridad, evaluadas a ciegas contra una línea base.
- **Tokens** — recuento real de tokens de salida, porque el sentido de comprimir es el coste.

Medido sobre 16 casos × 3 ensayos, evaluado a ciegas contra una línea base sin skill, en dos modelos con el mismo instrumento. Esta es la skill publicada (v0.4.0):

| | Sonnet | | Opus | |
| --- | ---: | --- | ---: | --- |
| Corrección | 4.896 → **4.938** | +0.042 | 4.708 → **4.875** | +0.167 |
| Fidelidad | 4.583 → **4.854** | +0.271 | 4.667 → **4.854** | +0.188 |
| Accionabilidad | 4.417 → **4.875** | +0.458 | 4.500 → **4.833** | +0.333 |
| Seguridad | 4.458 → **4.750** | +0.292 | 4.542 → **4.896** | +0.354 |
| Tokens de salida agente-a-agente | 172 → **105** | −39% | 320 → **137** | −57% |
| Tokens de salida para humanos, media | 346 → 374 | +8% | 535 → 555 | +4% |
| Tokens de la propia skill por turno (siempre activa) | 4,380 → **1,078** | −75% | 4,380 → **1,078** | −75% |

Mejor en todas las dimensiones, en ambos modelos, y **el criterio de publicación pasa las cinco reglas en ambos**. Lee las filas de tokens con cuidado: donde la skill comprime — los informes agente-a-agente — la salida cae entre un tercio y la mitad. Donde se niega a comprimir — acciones destructivas, hallazgos de seguridad, coste, errores — la salida se alarga, porque el modelo ahora mantiene cada advertencia por encima del pliegue en vez de adelgazarla; por eso la media sube, y cada uno de esos casos puntuó más alto en fidelidad o seguridad. La mediana no se publica aquí: entre dos ejecuciones de la misma skill cambió de signo, así que con 48 filas no es una cifra estable. El número más grande es el tamaño de la propia skill: un arnés siempre activo la reenvía en cada turno, y la versión anterior de 18k costaba unas 80 veces por turno lo que ahorraba.

Hicieron falta trece ejecuciones, incluidas las que fallaron y una en la que el error estaba en mi propio arnés. Metodología, criterios de publicación y las trece en [`evals/RESULTS.md`](../../evals/RESULTS.md). Los números se publican tanto si favorecen a la skill como si no.

## Agentes compatibles

Claude Code, Cursor, Cybara, OpenClaw, Hermes, Codex, Gemini CLI, GitHub Copilot, OpenCode, Zed, Windsurf, Cline, Roo Code, Aider, Amp, Qwen Code, Kimi Code CLI, Pi, Oh My Pi y Antigravity — instrucciones completas en [INSTALL.md](../../INSTALL.md).

La skill es markdown puro sin runtime, así que funciona en cualquier herramienta que acepte instrucciones personalizadas, incluidas las que no están en la lista.

## Licencia

MIT.

---

<p align="center">
  <strong>TL;DR: dale una estrella. ⭐</strong><br/>
  <sub>Acabas de leerte entero un README sobre no leer cosas.<br/>
  No seas perezoso justo en el último clic.</sub>
</p>
