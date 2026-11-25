# DDD: galivelop-artifacts (borrador 1, 2026-11-21)

**Uso:** entrada del experimento «desde el paso 0» (R8 de `docs/diseno-galivelopcode.md`). Cuando toque, la persona crea un repo vacío y GalivelopCode lo levanta solo a partir de este documento. No se edita para ayudar al modelo: las preguntas abiertas (§8) se resuelven dentro del experimento y se apunta cómo.

Nombre definitivo. Repositorio y proyecto: `galivelop-artifacts`. Paquete Python importable: `gart`. Licencia y visibilidad: repo público, con la misma licencia que los demás repos Galivelop.

## 1. Propósito

Una biblioteca **solo stdlib** (Python ≥ 3.10) para **definir, validar y migrar artefactos JSON versionados** que
se pasan entre los repos Galivelop. Sustituye a las cuatro copias del validador (`gdev/schema.py`,
`gimg/schema.py`, `gvoice/schema.py`, `opportunity_intel/schema.py`) y da el formato común de los artefactos entre GVE
y GalivelopCode (`gve.*/1`, `gdev.*/0`).

**Éxito:** las cuatro copias se sustituyen sin cambiar el comportamiento de sus tests, y GVE valida sus `gve.*/1` con
ella.

## 2. Lenguaje del dominio

| Término | Código | Significado |
|---|---|---|
| Esquema | `Schema` | Documento JSON Schema (subconjunto soportado, §6) que describe un tipo de artefacto en una versión |
| Artefacto | `Artifact` | Documento JSON que declara su tipo y se valida contra su esquema |
| Tipo de artefacto | `KindId` | `<espacio>.<nombre>/<versión>`, p. ej. `gve.evidence/1`. La versión es un entero mayor |
| Espacio | `namespace` | El repo dueño del tipo: `gve`, `gdev`, `gimg`, `gvoice`, `gcc`… Solo su dueño publica en él |
| Registro | `Registry` | Conjunto de esquemas y migraciones conocidos, cargado de carpetas locales |
| Validación | `validate()` | Comprobar un artefacto contra su esquema; devuelve una lista de errores, nunca lanza por un dato inválido |
| Error de validación | `ValidationError` | `path` (JSON Pointer), `code` (`required`, `type`…) y parámetros; el texto sale del catálogo es/en |
| Migración | `Migration` | Función pura que lleva un artefacto de `/n` a `/n+1` |
| Versión provisional | `/0` | Tipo en pruebas: puede cambiar sin migración; nunca se publica como estable |

**Notas sobre el proyecto y la compatibilidad:**
- El repositorio y el proyecto se llaman `galivelop-artifacts`; el paquete Python importable se llama `gart`.
- Se usa el campo que ya usa GVE en sus tipos `gve.*/1`, para no romper GVE.

## 3. Contextos acotados

1. **Validación (núcleo):** `Schema` y `validate()`. Puro: sin E/S y sin idioma (devuelve códigos).
2. **Registro:** carga esquemas de carpetas, resuelve `KindId` → `Schema` y `$ref` locales entre esquemas del registro.
3. **Migración:** cadena de `Migration` de `/n` a la versión pedida, validando cada paso.
4. **Presentación:** catálogo es/en de mensajes (`schema.<code>`) y CLI.

**Mapa con los demás repos:** núcleo compartido. Cada repo consumidor es dueño de su espacio y de sus esquemas; `gart` es dueño solo del validador, del formato `KindId` y de las reglas de versión. Los consumidores reciben el validador como una copia vendorizada con su versión específica y un test que compara la huella sha256 para garantizar integridad, manteniendo así la dependencia «solo stdlib» e instalable en cualquier sitio. Cada repositorio conserva sus propios esquemas y `gart` solo los carga; no existe un registro centralizado.

## 4. Modelo

- **Raíz del agregado:** `Registry`. Todo alta de esquema o migración pasa por ella y comprueba las invariantes.
- **Entidades:** `ArtifactKind` (espacio + nombre, con sus versiones).
- **Objetos de valor:** `KindId`, `Schema`, `ValidationError`, `JsonPointer`, `Migration`.
- **Servicios:** `validate(artifact, registry)`, `migrate(artifact, to, registry)`, `check_schema(schema)`.
- **Eventos:** ninguno (biblioteca sin estado).

## 5. Invariantes (cada una con su test)

1. `KindId` casa con `^[a-z][a-z0-9]*\.[a-z][a-z0-9_.]*/(0|[1-9][0-9]*)$`.
2. **Un esquema estable (`/n`, n ≥ 1) publicado no cambia:** el registro guarda su huella sha256 y un cambio falla; cambiar es publicar `/n+1` con su migración.
3. Cada `/n+1` estable tiene una migración desde `/n`, y su salida valida contra `/n+1`.
4. El validador **falla cerrado**: una palabra clave desconocida en un esquema es `SchemaError`, no se ignora.
5. Los catálogos es/en tienen las mismas claves y los mismos marcadores.
6. Sin dependencias fuera de stdlib; sin red (`$ref` solo locales).
7. Mismo artefacto y registro, mismo resultado y mismo orden de errores (determinista).
8. Cuando las cuatro copias de validadores difieren en sus reglas, gana la versión más estricta, y la diferencia se apunta en la tabla de diferencias.

## 6. Alcance

**Dentro:** el subconjunto actual de las cuatro copias (`type`, `properties`, `required`, `additionalProperties`, `propertyNames`, `minProperties`, `items`, `minItems`, `maxItems`, `enum`, `const`, `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`, `$ref`, `$defs` y las anotaciones), unificando lo que difiera entre ellas; registro; migraciones; CLI `gart validate <archivo>`, `gart migrate <archivo> --to <kind>`, `gart list`, `gart show <kind>`.

**Fuera:** JSON Schema completo, `format`, `$ref` remotos, generar código o documentación desde los esquemas, un servidor de registro.

Los consumidores reciben el validador como una copia vendorizada con su versión y un test que compara la huella sha256; se mantiene «solo stdlib, se instala en cualquier sitio». Cada repo conserva sus propios esquemas y `gart` solo los carga; no hay registro central.

## 7. Escalera de hitos (también banco de GalivelopCode, D37)

| Hito | Nivel | Qué | Lo decide |
|---|---|---|---|
| H1 | un archivo | `KindId`: análisis y validación del formato | tests de `KindId` |
| H2 | un archivo | Validador con el subconjunto común, migrado de la copia más completa | tests de cada palabra clave |
| H3 | varios pasos | Unificar las diferencias entre las cuatro copias (tabla de diferencias primero) | los tests de las cuatro copias pasan contra `gart` |
| H4 | varios pasos | `Registry`: carga de carpetas, `$ref` entre esquemas, huellas (invariante 2) | tests de registro y de cambio rechazado |
| H5 | partir un hito | Migraciones `/n` → `/n+1` encadenadas y validadas | tests de cadena y de salida inválida |
| H6 | varios pasos | Catálogo es/en y CLI | tests de `main([...])` en los dos idiomas |
| H7 | llevar una fase | Primer consumidor: sustituir `gdev/schema.py` | check de `gdev` en verde |
| H8 | llevar una fase | Resto de consumidores y tipos `gve.*/1` | check de cada repo en verde |

Cada hito, con su commit y su test, es una tarea minable por GVE.

## 8. Preguntas abiertas

## Decisiones de la F-1

| id | pregunta | respuesta | sección |
|---|---|---|---|
| q1 | ¿Cuál es el nombre definitivo del proyecto: `galivelop-artifacts` o `gart`? | El repositorio y el proyecto se llaman `galivelop-artifacts`; el paquete Python importable se llama `gart`. | 2. Lenguaje del dominio, preamble |
| q2 | ¿Cómo deben recibir los consumidores el validador: como una copia vendorizada (submódulo) o instalada desde git? | Copia vendorizada con su versión y un test que compara la huella sha256; se mantiene «solo stdlib, se instala en cualquier sitio». | 3. Contextos acotados, 6. Alcance |
| q3 | ¿Qué campo debe declarar el tipo en el artefacto JSON: mantener el existente usado por GVE o introducir uno nuevo? | Se usa el campo que ya usa GVE en sus tipos `gve.*/1`, para no romper GVE. | 2. Lenguaje del dominio |
| q4 | ¿Dónde deben residir físicamente los esquemas: en repositorios individuales o en un registro central? | Cada repo conserva sus propios esquemas y `gart` solo los carga; no hay registro central. | 3. Contextos acotados, 6. Alcance |
| q5 | ¿Cuál es la política de resolución cuando las cuatro copias de validadores difieren en sus reglas? | Cuando las cuatro copias difieran, gana la versión más estricta, y la diferencia se apunta en la tabla de diferencias. | 5. Invariantes (cada una con su test) |
| q6 | ¿Cuál es la licencia y visibilidad del repo de `gart`? | Repo público, con la misma licencia que los demás repos Galivelop. | preamble |
