# Questions

Questions for the user, one entry each; `python3 .claude/gw/scripts/questions.py` reads and rewrites this
file (format: header of scripts/questions.py). Answer by number: `questions.py answer "5. a, 6. ok"`.

## Q-1
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q7, reglas del JSON canónico: a) basado en RFC 8785 (JCS); b) reglas propias
- Recommendation: a: JCS (RFC 8785) tal cual, orden UTF-16 y números ECMAScript con stdlib; entrada restringida (enteros en ±(2^53-1); NaN, ±Inf, -0 y claves duplicadas rechazados, con loads_strict) (R6)
- Answer: a
- Answered: 2026-11-27

## Q-2
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q8, formato del hash: a) sha256:<hex>; b) hex sin prefijo
- Recommendation: a: sha256:<hex>, también en file_hash (R5)
- Answer: a
- Answered: 2026-11-27

## Q-3
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q9, qué entra en el hash: a) el artefacto entero; b) sin los campos anotados x-gart-volatile; c) sin un campo de sobre fijo meta
- Recommendation: c: campo de sobre fijo meta, definido en gart.common/0, que nunca entra en el hash (R2)
- Answer: c
- Answered: 2026-11-27

## Q-4
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q10, dónde vive gart.common/0: a) dentro del paquete gart; b) cada repo lo copia aparte
- Recommendation: a: dentro del paquete gart
- Answer: a
- Answered: 2026-11-27

## Q-5
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q11, tabla de namespaces: a) docs/namespaces.md; b) nadie la lleva; c) gart/namespaces.json y página generada
- Recommendation: c: gart/namespaces.json como dato del paquete, la página se genera de él; la regla vale al publicar, no al cargar (R4)
- Answer: c
- Answered: 2026-11-27

## Q-6
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q12, versionado y copias: a) semver y tabla de hashes en el CHANGELOG; b) sin tabla; c) semver y VENDOR.json como tabla de la versión
- Recommendation: c: semver; VENDOR.json es la tabla de la versión; el CI de gart la casa con su tag; el CHANGELOG solo enlaza (R3)
- Answer: c
- Answered: 2026-11-27

## Q-7
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q13, cuándo un /0 pasa a /1: a) cuando lo usa un consumidor de otro repo; b) a mano por el repo dueño
- Recommendation: b: lo sube a mano el repo dueño cuando el check de otro repo depende del tipo; que GVE lo lea no cuenta (R7)
- Answer: b
- Answered: 2026-11-27

## Q-8
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: DDD q14 (nueva, de R4), cómo llegan los esquemas de otro repo: a) copia de solo lectura con VENDOR.json; b) ruta a un clon local del otro repo; c) cada consumidor lo resuelve a su manera
- Recommendation: a: copia de solo lectura de los esquemas ajenos, marcada como tal, con su VENDOR.json y comprobada con el mismo kit (R4)
- Answer: a
- Answered: 2026-11-27

## Q-9
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: gw-update 0.9.0→0.9.1, rama: a) la de la sesión (ccr-c6c4e060-0l41l0), que ya lleva gart-H1 sin fusionar; b) una rama nueva claude/gw-update desde main
- Recommendation: a: actualizar en la rama de la sesión, en un commit propio; el PR lleva H1 y la 0.9.1 juntos y la revisión separa los commits
- Answer: a
- Answered: 2026-11-27

## Q-10
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: ¿Aplico apply.py --update (escribe 110 archivos del flujo y migra .claude/gw.json; puede pedir permiso para tocar .claude/settings.json y .githooks/)?
- Recommendation: ok: --update (110 archivos del flujo sin cambios locales y gw.json a 0.9.1)
- Answer: ok
- Answered: 2026-11-27

## Q-11
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: Fusión a mano: a) traer las 2 reglas nuevas de REVIEW.md (tiempo límite que mata el grupo de procesos; un test no depende de que exista lo que comprueba) y subir solo los marcadores del resto (AGENTS, CLAUDE y GLOSSARY solo cambian el marcador); b) otra cosa
- Recommendation: a: añadir las 2 reglas nuevas de REVIEW.md y subir el marcador de AGENTS, CLAUDE, GLOSSARY, REVIEW, la bitácora y gw-opt-tokens.md a v0.9.1 sin generar los .gw-new
- Answer: a
- Answered: 2026-11-27

## Q-12
- Refs:
- Status: answered
- Asked: 2026-11-27
- Question: Para leer las 4 copias en gart-H2, el subagente necesita acceso a galivelop-developer, galivelop-image-generator, galivelop-voice-generator y galivelop-client-catcher (rechazaste add_repo desde la sesión principal): a) lo añado en solo lectura para que lo lea un subagente; b) los clonas tú o me dices otra vía
- Recommendation: a: añadirlos en solo lectura; los lee un subagente Explore haiku que devuelve un resumen con rutas, la sesión principal no los abre
- Answer: a
- Answered: 2026-11-27

## Q-13
- Refs: gart-H2
- Status: answered
- Asked: 2026-11-27
- Question: galivelop-developer no se pudo añadir (el permiso automático lo rechazó; los otros 3 ya están clonados en solo lectura): a) lo autorizas tú (regla de permiso para add_repo o lo añades a la sesión) y lo leo igual; b) se elige la copia más completa entre las 3 y gdev se compara en gart-H3
- Recommendation: a: sin gdev la comparación queda con 3 de 4 copias; gdev es el primer consumidor (gart-H7), así que conviene verla antes de elegir
- Answer: a
- Answered: 2026-11-27

## Q-14
- Refs: gart-H2
- Status: answered
- Asked: 2026-11-27
- Question: Base gvoice para gart-H2: a) solo las palabras clave del alcance del DDD §6 (fuera allOf, if/then/else, maxProperties, dependentRequired y $ref a archivo hermano), con enum no vacío y orden estable de errores de oi; b) además las que usan las copias aunque no estén en la lista (amplía el DDD)
- Recommendation: a: el DDD §6 fija la lista; lo que usan las copias y no está en ella (allOf, if/then/else, maxProperties, dependentRequired) se apunta para gart-H3, donde la tabla gart.diff/0 dirá qué consumidor lo necesita; los $ref a archivo hermano esperan al Registry (gart-H4)
- Answer: a
- Answered: 2026-11-27

## Q-15
- Refs: gart-H9
- Status: answered
- Asked: 2026-11-27
- Question: Floats de magnitud ≥ 2^53 (p. ej. 1e20, 1e300, 9.007199254740992e15) en el canon: a) se rechazan con canon.int_range al leer y al escribir; b) se aceptan como ahora, sin ida y vuelta (canonical_bytes los escribe como dígitos que loads_strict rechaza)
- Recommendation: a: la inv. 9 rechaza los enteros fuera de ±(2^53−1) y todo double de 2^53 o más es entero; con b el canon escribe bytes (1e20 → 100000000000000000000) que su propio loads_strict rechaza, y la regla se salta escribiendo el entero con exponente (9.007199254740992e15). Se pierden los números de magnitud ≥ 2^53, que ningún artefacto actual usa
- Answer: a
- Answered: 2026-11-27

## Q-16
- Refs: gart-H9
- Status: answered
- Asked: 2026-11-27
- Question: Siguiente paso tras gart-H9: a) llevar la rama a main (tres fases: revisión, gw-opt-tokens + retro, marca) o b) seguir con gart-H3 según el orden del plan (o c) gart-H10, como decía la bitácora)
- Recommendation: b) seguir con gart-H3: el plan fija H9 → H3 → H4 → H10 y llevar a main ahora (14 commits, CI verde) obliga a la revisión final y la retro; mejor tras H3/H4 o cuando un consumidor lo pida
- Answer: a
- Answered: 2026-11-27

## Q-17
- Refs: gart-H3
- Status: open
- Asked: 2026-11-27
- Question: License de gart-H10 (decidir antes de empezarlo): a) lista SPDX corta, sin expresiones, autor obligatorio; b) lista SPDX entera con expresiones; c) otra
- Recommendation: a) MIT/Apache-2.0/BSD/ISC/CC-BY/CC0 como lista corta, sin expresiones OR/AND en /0, autor obligatorio; se amplía en un /1 si un consumidor lo pide

## Q-18
- Refs: gart-H3
- Status: answered
- Asked: 2026-11-27
- Question: Palabras clave que gart-H2 dejó fuera y que usan esquemas publicados (maxProperties y dependentRequired en 3 de gimg; allOf e if/then/else en 2 de gvoice): a) entran las cuatro en gart; b) solo las de gimg; c) ninguna, y gimg y gvoice reescriben sus esquemas
- Recommendation: a: sin ellas gart no puede validar los esquemas que ya publican gimg y gvoice (gart-H8); las cuatro son pequeñas y gvoice ya las tiene con tests; se amplía el DDD §6 con un ADR
- Answer: a
- Answered: 2026-11-27

## Q-19
- Refs: gart-H3
- Status: answered
- Asked: 2026-11-27
- Question: Contrato de errores frente a oi (rutas $.a[0], param property, actual en type, tipos separados por |): a) gart se queda con JSON Pointer y name, añade actual a los params de type y oi se adapta en gart-H8; b) igual pero sin actual; c) gart copia el formato de oi
- Recommendation: a: JSON Pointer es el contrato de gart y name ya lo usan las otras tres copias; actual añade información sin romper a nadie y oi la necesita para sus mensajes
- Answer: a
- Answered: 2026-11-27

## Q-20
- Refs: gart-H3
- Status: answered
- Asked: 2026-11-27
- Question: Qué significa «los tests de las cuatro copias pasan contra gart» en gart-H3: a) pasan los de comportamiento; los de API (load_schema → gart-H4, format_error y mensajes → gart-H6, check de oi → gart-H8) quedan como filas de gart.diff/0 con su hito; b) pasan todos ya en gart-H3
- Recommendation: a: adelantar el Registry y el catálogo mezclaría tres hitos; cada test que no pase tendrá su fila en gart.diff/0 con el hito que lo cierra
- Answer: a
- Answered: 2026-11-27
