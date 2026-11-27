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
- Status: open
- Asked: 2026-11-27
- Question: Floats de magnitud ≥ 2^53 (p. ej. 1e20, 1e300, 9.007199254740992e15) en el canon: a) se rechazan con canon.int_range al leer y al escribir; b) se aceptan como ahora, sin ida y vuelta (canonical_bytes los escribe como dígitos que loads_strict rechaza)
- Recommendation: a: la inv. 9 rechaza los enteros fuera de ±(2^53−1) y todo double de 2^53 o más es entero; con b el canon escribe bytes (1e20 → 100000000000000000000) que su propio loads_strict rechaza, y la regla se salta escribiendo el entero con exponente (9.007199254740992e15). Se pierden los números de magnitud ≥ 2^53, que ningún artefacto actual usa
