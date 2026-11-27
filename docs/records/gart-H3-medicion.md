# gart-H3: los tests de las cuatro copias contra gart

Medición de un subagente (2026-11-27) sobre clones `--depth 1`: gdev@014f7ff, oi@0edac88, gimg@a3c314a,
gvoice@1990d92. Solo `tests/test_schema.py` de cada repo, con el módulo `schema` de la copia sustituido por
`gart.schema` (sin alias de comportamiento; las API ausentes, como stubs que fallan con `missing API`).

| repo | con su módulo | contra gart |
|---|---|---|
| gdev | 35 ok | 30 ok, 5 error |
| gimg | 59 ok | 31 ok, 28 error |
| gvoice | 48 ok | 32 ok, 3 fallo, 13 error |
| oi | 32 ok | 7 ok, 25 fallo o error |

**gart nunca es más laxo que una copia** (lo mismo con ~90 casos límite por repo y comparando cada llamada de los
tests con las dos implementaciones). Donde difiere, es más estricto: patrones ASCII y no finitos frente a oi; esquemas
mal formados (`enum` vacío, `type` desconocido, `minLength` negativo…) y palabras clave desconocidas (`format`,
`oneOf`, `not`…) que las copias aceptaban o con las que fallaban de otra forma.

## Causas

| causa | repos | hito |
|---|---|---|
| `load_schema`, `_SCHEMAS`, `$ref` a archivo hermano | los cuatro | gart-H4 (`Registry`) |
| `format_error`, mensajes es/en | los cuatro | gart-H6 (catálogo) |
| `maxProperties`, `dependentRequired` | gimg: `project-config`, `brand-sheet`, `order` | por decidir (Q-18) |
| `allOf`, `if`/`then`/`else` | gvoice: `order`, `effect-chain` | por decidir (Q-18) |
| rutas `$.a[0]`, params `property` y `actual`, separador de tipos `\|` | oi | por decidir (Q-19) |
| `check` y `ValidationError` como excepción | oi | gart-H8 (lo adapta oi) |
| `_error` privado | gdev, gimg, gvoice | no es API: el test de la copia se adapta |
| `propertyNames`: gart da `reason`/`detail` en vez de `pattern` | gdev, gimg, gvoice | gart (más informativo; ningún test lo comprueba) |
| textos de `SchemaError` | oi, gvoice | gart (el contrato es el tipo de error, no el texto) |

Adaptador y batería de casos límite: `docs/records/gart-H3/` (`bash docs/records/gart-H3/run.sh [--own|--diag|--diff]`, con los clones en las rutas de `run.sh`).
