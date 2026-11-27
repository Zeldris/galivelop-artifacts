# ¿Entran en gart las palabras clave que usan los esquemas ya publicados y no están en el §6?

Status: accepted

Entran `maxProperties`, `dependentRequired`, `allOf` e `if`/`then`/`else`. Los errores de `type` llevan además
`actual`, el tipo JSON de la instancia.

Por qué: la medición de gart-H3 (`docs/records/gart-H3-medicion.md`) encontró que tres esquemas publicados de gimg
(`project-config`, `brand-sheet`, `order`) y dos de gvoice (`order`, `effect-chain`) las usan. Sin ellas, gart no
puede validar esos esquemas en gart-H8. gvoice y gimg ya las tienen con tests, y se portan de ahí. `actual` lo
necesitan los mensajes de oi y no rompe a ningún consumidor.

Descartado: que gimg y gvoice reescriban sus esquemas (más trabajo en dos repos y esquemas menos claros); copiar el
formato de errores de oi (`$.a[0]`, `property`): las otras tres copias ya usan JSON Pointer y `name`.

Sección de origen: 6. Alcance (amplía la lista de palabras clave; Q-18 y Q-19)
