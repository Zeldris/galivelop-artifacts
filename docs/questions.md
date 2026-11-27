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
