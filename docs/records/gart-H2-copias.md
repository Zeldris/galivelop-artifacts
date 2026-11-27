# gart-H2: comparación de las copias del validador

Resumen de un subagente Explore (2026-11-27) sobre clones `--depth 1`; leyó código y nombres de tests, no los corrió.
Falta gdev (Q-13).

| | gimg `gimg/schema.py` (265 l., tests 369) | gvoice `gvoice/schema.py` (342 l., tests 305) | oi `opportunity_intel/schema.py` (240 l., tests 206) |
|---|---|---|---|
| Palabras clave | las 18 del alcance + `maxProperties`, `dependentRequired` | las del alcance + `allOf`, `if/then/else`; sin `maxProperties` ni `dependentRequired` | subconjunto: sin `$ref`, `$defs`, `const`, `propertyNames`, `minProperties` |
| Anotaciones | `$schema $id title description default examples $comment` | igual | sin `default` ni `examples` (las rechaza) |
| Clave desconocida | `SchemaError` en `check_schema` | igual | rechazada, también dentro de `validate` |
| API | `check_schema`, `load_schema`, `validate -> list[ValidationError(path, code, params)]`, `format_error(err, lang)` | igual, `load_schema` con caché y deepcopy | `validate` llama a `check_schema`; `check` lanza `ValidationError` con `SchemaFailure` |
| Rutas | JSON Pointer (`/items/0/id`) | igual | `$.items[2].id` |
| `$ref` | solo `#/...`; **sin detección de ciclos** (RecursionError, sin test) | `#/...` y archivo hermano, rechaza salir de la carpeta; detecta ciclos con test | no |
| Números | bool no es número; 1.0 es entero; rechaza inf/NaN | igual | acepta inf/NaN |
| `pattern` | `re.ASCII`, `$`→`\Z` | igual | sin `re.ASCII`, recompila en cada llamada |
| `enum` vacío | no lo comprueba | — | lo rechaza |
| Mensajes | es/en, 17 claves | es/en, 15 claves | es/en en los locales comunes |

**Veredicto:** base gvoice (copia de gimg@4365f9a mejorada). De gimg, el rechazo de números no finitos ya está en las
dos. Por decidir contra el alcance del DDD §6: `allOf`/`if/then/else`, `maxProperties`, `dependentRequired` (fuera de
la lista) y los `$ref` a archivo hermano (son del `Registry`, gart-H4). De oi, merece la pena: `enum` no vacío y orden
estable de errores.
