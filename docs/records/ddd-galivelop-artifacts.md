# DDD — galivelop-artifacts (`gart`)

**Final · 2026-11-27.** Sustituye al borrador 1 (2026-11-21). Sale del borrador 2 (2026-11-26) y de su revisión
(R1–R10), los dos en `galivelop-developer/docs/records/`. Las decisiones q1–q14 están al final, cada una con su ADR
en `docs/adr/`.

Nombre definitivo. Repositorio y proyecto: `galivelop-artifacts`. Paquete Python importable: `gart`. Licencia y
visibilidad: repo público, con la misma licencia que los demás repos Galivelop.

**Qué cambia respecto al borrador 1:**
- Tres repos nuevos usan gart como validador común: gmod, grun y gforge.
- gworld necesita referirse a otros artefactos por su hash y llevar la licencia de cada contenido. Para eso hay JSON
  canónico y hash, `ArtifactRef` y `gart.common/0`.
- Con más de ocho repos que copian gart, la copia tiene su propio kit de comprobación.
- Se añaden los hitos gart-H9 a gart-H11.

## 1. Propósito

Una biblioteca **solo stdlib** (Python ≥ 3.10) para definir, validar y migrar artefactos JSON versionados. Es el
contrato común entre los repos Galivelop. Cada repo define y publica sus esquemas, y gart da cuatro cosas comunes:
- el lenguaje de esos esquemas;
- la validación;
- las migraciones;
- la forma canónica de serializar y de calcular el hash.

**Criterios de éxito**
1. Las cuatro copias se sustituyen por gart sin cambiar sus tests: `gdev/schema.py`, `gimg/schema.py`,
   `gvoice/schema.py` y `opportunity_intel/schema.py`.
2. GVE valida `gve.*/1` con gart.
3. gmod (`gmod.machine/0`), grun (`grun.lock/0`), los artefactos de gforge y los `gworld.*/0` se validan con gart sin
   una copia propia del validador.
4. Mismo artefacto, mismos bytes canónicos y mismo `sha256` en Linux, macOS, Windows y la Deck (vectores fijos).
5. En cada consumidor, un test detecta en menos de un segundo y sin red si su copia difiere de su `VENDOR.json`.

## 2. Lenguaje del dominio

| Término | Significado |
|---|---|
| `Artifact` | Documento JSON con un campo de tipo, el que ya usa GVE en `gve.*/1`, que lo liga a un `KindId`. |
| `KindId` | `<ns>.<nombre>/<n>`, p. ej. `gworld.pack/0`. `/0` es provisional: puede cambiar sin migración. Desde `/1` es estable. El paso a `/1` lo hace a mano el repo dueño cuando el check de otro repo depende del tipo; que GVE lo lea no cuenta. |
| `Namespace` | Prefijo de un repo dueño (`gdev`, `gimg`, `gvoice`, `oi`, `gve`, `gmod`, `grun`, `gforge`, `gworld`, `gart`). La tabla es `gart/namespaces.json`. |
| `Schema` | El subconjunto de JSON Schema de §6. Lo publica el repo dueño de su namespace. |
| `Registry` | Carpetas locales de esquemas que carga un proceso. No hay registro central ni servidor. |
| `validate()` | Devuelve una lista de `ValidationError`, vacía si es válido. Nunca lanza por un artefacto inválido. |
| `ValidationError` | Ruta como JSON Pointer, código, parámetros y texto es/en del catálogo. |
| `SchemaError` | Error del esquema, no del artefacto (p. ej., una palabra clave desconocida). Este sí lanza. |
| `Migration` | Función pura de `/n` a `/n+1`. |
| `CanonicalJson` | Los bytes de un valor JSON según RFC 8785 (JCS). |
| `Meta` | Campo de sobre `meta`, de primer nivel, para datos volátiles (fecha, máquina). Nunca entra en el hash. |
| `ContentHash` | `sha256:<hex>`. De un artefacto: sus bytes canónicos sin `meta`. De un archivo: sus bytes tal cual. |
| `ArtifactRef` | `{kind, hash}`: un artefacto JSON que apunta a otro sin copiarlo (`gworld.check` a la narración, `gworld.state` al pack). Un archivo que no es un artefacto se apunta solo con su hash, sin `kind`. |
| `Fingerprint` | sha256 del esquema canónico. Fija un esquema estable. |
| `VendoredCopy` | Copia de solo lectura dentro de un consumidor, con su `VENDOR.json`: del paquete `gart/` o de los esquemas de otro repo. |
| `gart.common/0` | `$defs` que trae el paquete gart y reutiliza cualquier esquema: `ContentHash`, `ArtifactRef`, `License`, `Timestamp`, `Meta`. |

## 3. Contextos acotados

| Contexto | Qué hace | Dependencias |
|---|---|---|
| **Validation** (núcleo puro) | `validate`, `check_schema`. Sin E/S y sin idioma: devuelve códigos | ninguna |
| **Canon** | `loads_strict`, `canonical_bytes`, `content_hash`, `file_hash`, `verify_ref`. Puro salvo `file_hash`, que lee un archivo | ninguna |
| **Registry** | Carga esquemas de carpetas locales, resuelve `$ref` locales y comprueba fingerprints y namespaces | Validation, Canon |
| **Migration** | Encadena migraciones `/n` → `/m` y valida cada paso | Validation, Registry |
| **Vendoring** | `gart vendor` y `gart vendor --check`; genera el test de copia | Canon |
| **Presentation** | Catálogo es/en (`schema.<code>`) y CLI | todos |

**Relación con los demás repos:** gart es **upstream**, y los demás se conforman con su contrato (*conformist*).
Ninguno le aporta código; solo le piden cambios. Cada consumidor es dueño de su namespace y de sus esquemas; gart es
dueño del validador, del formato `KindId`, del canon y de las reglas de versión.

**Cómo llega cada cosa a un consumidor:**
- **El validador:** copia de `gart/` con su `VENDOR.json` y un test de sha256.
- **Los esquemas de otro repo:** copia de solo lectura, marcada como ajena, con su `VENDOR.json` y comprobada con el
  mismo kit. Se actualiza a mano.

```
                 gart (lenguaje de esquemas, canon, refs)
                   │  copia + test de sha256
   ┌──────┬──────┬─┴────┬──────┬──────┬───────┬────────┬────────┐
  gdev  gimg  gvoice   oi    gve   gmod    grun    gforge   gworld
                              │      │       │        │        │
                       mide todo   machine  lock   dataset  pack/map/state
                                   /0       /0     /run     /canon/check
```

- **gworld** usa `ArtifactRef` y `License`. `gworld.state` lleva el hash del pack y `gworld.check`, el de la
  narración que juzgó.
- **gforge** fija un dataset (archivos) a un entrenamiento con su hash, y así puede repetir un ajuste.
- **grun** escribe `grun.lock/0` con los hashes de los modelos (GGUF, binarios) y de los packs que cargó.
- **GVE** compara artefactos por `ContentHash`, nunca por su texto, y carga como copias ajenas los esquemas que mide.

## 4. Modelo

- **Raíz del agregado:** `Registry`. Todo alta de esquema o migración pasa por él y comprueba las invariantes.
- **Entidad:** `ArtifactKind`, con `KindId`, `Schema`, `Fingerprint`, estado (`provisional` o `stable`) y su
  `Migration` hacia `/n+1`, si existe.
- **Objetos de valor:** `KindId`, `Schema`, `ValidationError`, `JsonPointer`, `Migration`, `CanonicalJson`, `Meta`,
  `ContentHash`, `ArtifactRef`, `VendorManifest`.
- **Servicios:**
  - `validate(artifact, registry) -> list[ValidationError]`
  - `check_schema(schema) -> None` (lanza `SchemaError`)
  - `Registry.load(path, owner=...)` para los esquemas propios; las copias ajenas se cargan marcadas como tales
  - `migrate(artifact, to, registry)`
  - `loads_strict(text) -> obj` (rechaza lo que el canon no admite)
  - `canonical_bytes(obj) -> bytes`
  - `content_hash(obj) -> ContentHash` (quita `meta`; no necesita el esquema)
  - `file_hash(path) -> ContentHash`
  - `verify_ref(ref, artifact) -> list[ValidationError]`
  - `vendor_check(path) -> list[ValidationError]`
- **Eventos:** ninguno (biblioteca sin estado).

**Artefactos propios de gart:**

| KindId | Contenido |
|---|---|
| `gart.common/0` | `$defs` de `ContentHash` (`^sha256:[0-9a-f]{64}$`), `ArtifactRef`, `License` (SPDX id o `LicenseRef-*`, y autor), `Timestamp` (UTC, ISO 8601, `Z`) y `Meta` (objeto). |
| `gart.vendor/0` | El `VENDOR.json` de cada copia: origen, versión y hash de cada archivo copiado. |
| `gart.diff/0` | La tabla de diferencias entre las cuatro copias, como artefacto verificable. |

## 5. Invariantes (cada una con su test)

1. **`KindId`** casa con `^[a-z][a-z0-9]*\.[a-z][a-z0-9_.]*/(0|[1-9][0-9]*)$`.
   - Test: tabla de válidos e inválidos.
2. **Un esquema estable publicado no cambia:** su `Fingerprint` coincide con el registrado; cambiar es publicar
   `/n+1` con su migración.
   - Test: cambiar un byte da error.
3. **Cada `/n+1` estable tiene una migración** desde `/n`, y su salida valida contra `/n+1`.
   - Test: los ejemplos de `/n` migrados validan.
4. **El validador falla cerrado:** una palabra clave desconocida es `SchemaError`.
   - Test: el motivo del error nombra la palabra.
5. **Los catálogos es/en tienen las mismas claves y marcadores.**
   - Test: diferencia de conjuntos.
6. **Solo la biblioteca estándar y sin red** (`$ref` solo locales).
   - Test: importar con `socket` bloqueado y revisar los `import` con AST.
7. **Determinista:** misma entrada y registro, mismos errores en el mismo orden (ruta y luego código).
   - Test: 100 repeticiones con `PYTHONHASHSEED` distinto.
8. **Donde las reglas de validación de las copias difieren, gana la más estricta**, apuntada en `gart.diff/0`. Las
   anotaciones no validan: se admite la unión de las de las cuatro copias.
   - Test: cada fila de la tabla tiene su caso; los esquemas actuales de cada copia pasan `check_schema`.
9. **JSON canónico único: RFC 8785 (JCS)**, claves en orden de unidades UTF-16 y números con el formato de
   ECMAScript, escrito solo con la biblioteca estándar. Restricciones de entrada propias: se rechazan los números
   (enteros o no) fuera de ±(2^53−1), `NaN`, `±Inf`, `-0` y las claves duplicadas (estas, al leer con `loads_strict`).
   - Test: vectores fijos en un JSON, con los bytes esperados en hex y el hash; `.gitattributes` los marca `-text`.
     Cada restricción tiene su caso de rechazo con su motivo. El CI los corre en Linux; macOS, Windows y la Deck se
     comprueban en la máquina y quedan pendientes en el plan hasta entonces.
10. **Un `ArtifactRef` solo verifica si coinciden el kind y el hash** del artefacto apuntado.
    - Test: un hash cambiado y un kind cambiado dan códigos distintos.
11. **Un consumidor nunca edita una copia:** el `VENDOR.json` es la tabla de esa versión y lo genera `gart vendor`.
    El test del consumidor rehace los sha256 con `hashlib`, sin importar el código copiado, y compara también el
    conjunto de archivos. El CI de gart comprueba que la tabla de cada versión publicada casa con su tag. Límite: sin
    red, el test no detecta que se editen a la vez un archivo y su `VENDOR.json`.
    - Test: editar, borrar o añadir un archivo da error y lo nombra.
12. **Un repo solo publica esquemas de su namespace**, según `gart/namespaces.json` (la página de namespaces se genera
    de él). La regla vale para la carpeta propia, no para las copias ajenas.
    - Test: `Registry.load(path, owner="gmod")` con un `gworld.*` da error; el mismo esquema como copia ajena carga.
13. **Un `License` es un identificador SPDX válido** de una lista que trae gart, o un `LicenseRef-*`.
    - Test: un id inventado da error.
14. **`meta` nunca entra en el hash de un artefacto.**
    - Test: dos artefactos que solo difieren en `meta` dan el mismo `ContentHash`; en otro campo, distinto.

**Versiones de gart:** semver. Una versión menor nunca rompe un esquema estable. El CHANGELOG enlaza la tabla de cada
versión.

## 6. Alcance

**Dentro**
- Palabras clave: `type`, `properties`, `required`, `additionalProperties`, `propertyNames`, `minProperties`,
  `items`, `minItems`, `maxItems`, `enum`, `const`, `pattern`, `minLength`, `maxLength`, `minimum`, `maximum`,
  `$ref`, `$defs`, `maxProperties`, `dependentRequired`, `allOf`, `if`, `then`, `else` (las seis últimas, Q-18).
- Anotaciones: la unión de las de las cuatro copias; entre ellas `title`, `description`, `examples`, `$comment`,
  `$schema`, `$id` y `default`.
- JSON canónico, `ContentHash`, `file_hash`, `ArtifactRef`, `gart.common/0`.
- Kit de copia: `gart vendor <destino>`, `gart vendor --check` y la plantilla del test del consumidor, para el paquete
  y para los esquemas ajenos.
- CLI: `gart validate <archivo>`, `gart migrate <archivo> --to <kind>`, `gart list`, `gart show <kind>`,
  `gart hash <archivo>`, `gart ref <archivo>` (imprime el `ArtifactRef`) y `gart vendor [--check]`.

**Fuera**
- JSON Schema completo y `format`.
- `$ref` remotos.
- Generar código o documentación desde los esquemas (salvo la página de namespaces).
- Servidor o registro central de esquemas.
- Firmas criptográficas: el hash da integridad, no autoría.
- Guardar los artefactos: de eso se ocupa cada repo.

## 7. Escalera de hitos

Cada hito, con su commit y su test, es una tarea minable por GVE.

| Hito | Nivel | Qué | Lo decide | Primer consumidor o quien lo pide |
|---|---|---|---|---|
| gart-H1 | un archivo | `KindId`: análisis y validación del formato | tests de `KindId` | — |
| gart-H2 | un archivo | Validador del subconjunto y las anotaciones, migrado de la copia más completa | tests de cada palabra clave | — |
| gart-H3 | varios pasos | Unificar las cuatro copias (tabla `gart.diff/0` primero) | los tests de las cuatro copias pasan contra gart | — |
| gart-H4 | varios pasos | `Registry`: carpetas locales, `$ref` entre esquemas y fingerprints | tests de registro y de cambio rechazado | — |
| gart-H5 | partir un hito | Migraciones `/n` → `/n+1` encadenadas y validadas | tests de cadena y de salida inválida | — |
| gart-H6 | varios pasos | Catálogo es/en y CLI | tests de `main([...])` en los dos idiomas | — |
| gart-H7 | llevar una fase | Primer consumidor: `gdev/schema.py` pasa a ser la copia de `gart/` | check de gdev en verde | consume gdev |
| gart-H8 | llevar una fase | Resto de consumidores y `gve.*/1` | check de cada repo en verde | consumen gimg, gvoice, oi y gve |
| gart-H9 | un archivo, más los vectores | Canon: `loads_strict`, JCS, `ContentHash`, `file_hash` y `meta` | vectores fijos y casos de rechazo (inv. 9 y 14) | lo piden gforge y grun |
| gart-H10 | varios pasos | `ArtifactRef`, `gart.common/0` y `License` | tests de las inv. 10 y 13 | lo pide gworld |
| gart-H11 | varios pasos | Kit de copia (`vendor`, `--check`, test plantilla, copias ajenas), `gart/namespaces.json` y su página | tests de las inv. 11 y 12 | lo piden los nueve repos |
| gart-H12 | un archivo, más los vectores | Barrido de `gart/canon.py`: los 5 leves de gart-H9 en `docs/records/pending.md` | tests de cada leve | retro 2026-11-27 |

**Orden:** gart-H1 → H2 → H9 → H12 → H3 → H4 → H10 → H5 → H6 → H11 → H7 → H8. El canon y las refs van antes que los
consumidores porque gmod, grun, gforge y gworld nacen ya con ellos: ninguno de los repos nuevos escribe su propia
función de hash.

**gdev como consumidor:**
- gdev no cambia hasta gart-H7. Entonces añade el `VENDOR.json` y el test de la plantilla; `gdev/schemas/` se queda en
  gdev.
- gart-H7 depende de las anotaciones (gart-H2) y de mover a `meta`, en un `/0`, los campos volátiles de los 2
  esquemas de gdev que los tienen, entre ellos `gdev.intervention/0`. Un `/1` estable de GVE con esos campos pediría
  su `/2`.
- Pasar los sha256 propios de gdev (`ddd`, `catalog_confirm`, `download`) a `content_hash` o `file_hash` es una tarea
  aparte, medida, después de gart-H8.

**Banco de GalivelopCode:** los hitos entran con los ids `gart-H<n>` y el nivel de la tabla; los vectores de la inv. 9
sirven de tests de aceptación ocultos.

## 8. Preguntas abiertas

Ninguna bloquea gart-H1. Quedan dos leves de la revisión, para antes del hito que las toca:
- **gart-H10, `License`:** lista SPDX corta o entera, si se admiten expresiones (`MIT OR Apache-2.0`) y si el autor es
  obligatorio.
- **gart-H3, `gart.diff/0`:** es el producto de un solo hito; vale mientras se quede en `/0`.

## Decisiones de la F-1

| id | pregunta | respuesta | sección |
|---|---|---|---|
| q1 | ¿Cuál es el nombre definitivo del proyecto: `galivelop-artifacts` o `gart`? | El repositorio y el proyecto se llaman `galivelop-artifacts`; el paquete Python importable se llama `gart`. | 2. Lenguaje del dominio, preamble |
| q2 | ¿Cómo deben recibir los consumidores el validador: como una copia vendorizada (submódulo) o instalada desde git? | Copia vendorizada con su versión y un test que compara la huella sha256; se mantiene «solo stdlib, se instala en cualquier sitio». | 3. Contextos acotados, 6. Alcance |
| q3 | ¿Qué campo debe declarar el tipo en el artefacto JSON: mantener el existente usado por GVE o introducir uno nuevo? | Se usa el campo que ya usa GVE en sus tipos `gve.*/1`, para no romper GVE. | 2. Lenguaje del dominio |
| q4 | ¿Dónde deben residir físicamente los esquemas: en repositorios individuales o en un registro central? | Cada repo conserva sus propios esquemas y `gart` solo los carga; no hay registro central. | 3. Contextos acotados, 6. Alcance |
| q5 | ¿Cuál es la política de resolución cuando las cuatro copias de validadores difieren en sus reglas? | Cuando las cuatro copias difieran, gana la versión más estricta, y la diferencia se apunta en la tabla de diferencias. | 5. Invariantes (cada una con su test) |
| q6 | ¿Cuál es la licencia y visibilidad del repo de `gart`? | Repo público, con la misma licencia que los demás repos Galivelop. | preamble |
| q7 | ¿Qué reglas sigue el JSON canónico? | RFC 8785 (JCS) tal cual, con orden UTF-16 y números ECMAScript escritos con la biblioteca estándar. Se rechazan en la entrada los números (enteros o no) fuera de ±(2^53−1), `NaN`, `±Inf`, `-0` y las claves duplicadas (`loads_strict`). | 5. Invariantes |
| q8 | ¿Qué formato tiene el hash? | `sha256:<hex>`, también en `file_hash` para los archivos que no son JSON. | 2. Lenguaje del dominio |
| q9 | ¿Qué entra en el hash de un artefacto? | El artefacto sin el campo de sobre `meta`, definido en `gart.common/0`. | 2. Lenguaje del dominio, 5. Invariantes |
| q10 | ¿Dónde vive `gart.common/0`? | Dentro del paquete gart, y se copia con él. | 4. Modelo |
| q11 | ¿Dónde está la tabla de namespaces? | En `gart/namespaces.json`, dato del paquete del que se genera la página. La regla de namespace vale al publicar los esquemas propios, no al cargar copias ajenas. | 5. Invariantes |
| q12 | ¿Cómo se versiona gart y se comprueban las copias? | Semver; el `VENDOR.json` es la tabla de cada versión. El CI de gart la casa con su tag y el CHANGELOG solo la enlaza. Una menor nunca rompe un esquema estable. | 5. Invariantes |
| q13 | ¿Cuándo pasa un tipo de `/0` a `/1`? | Lo sube a mano el repo dueño cuando el check de otro repo depende del tipo; que GVE lo lea no cuenta. | 2. Lenguaje del dominio |
| q14 | ¿Cómo obtiene un repo los esquemas de otro? | Copia de solo lectura, marcada como ajena, con su `VENDOR.json` y comprobada con el mismo kit. | 3. Contextos acotados |
