# Pendiente

Lo que queda abierto; la bitácora solo apunta aquí. Se añade y se quita en este archivo.

## Pendiente

- gart-H4 (inv. 13): `gart.common/0` `License.id` solo comprueba la forma (SPDX o `LicenseRef-*`); falta la lista SPDX real que trae gart y el test del id inventado
- Comprobar los vectores canónicos (inv. 9) en macOS, Windows y la Deck al cerrar gart-H9: lo hace la persona en cada máquina
- DDD §8 (leves R11 y R12): License decidida (Q-17 a: lista SPDX corta sin expresiones, autor obligatorio), falta llevarla al DDD en gart-H10; gart.diff/0 se queda en /0
- gart-H2: instancias muy anidadas dan RecursionError (900 niveles); límite de profundidad con error propio o documentarlo
- gart-H2: `_ecma_pattern` solo traduce `$` (`[]x]`, `\s`, `.` difieren de ECMA-262)
- gart-H2: un NaN en la instancia pasa `minimum` si el esquema no tiene `type` (lo cierra `loads_strict` en gart-H9 o una comprobación en `validate`)
- gart-H2: un `required` repetido por `$ref` y su hermano da errores duplicados
- gart-H12 (revisión de bloque): `_pairs` sustituye el objeto entero por el `_Bad` de clave duplicada y oculta valores malos anteriores: `loads_strict('{"a":NaN,"a":1}')` da canon.duplicate_key en vez de canon.nan; devolver antes el `_Bad` de un valor ya visto
- gart-H12 (revisión de bloque): `_walk` comprueba todas las claves de un dict antes que sus valores: `{"a":[NaN],"\ud800":1}` da canon.type en la clave en vez de canon.nan en /a/0; comprobar cada clave justo antes de su hijo
- gart-H12 (revisión de bloque): `loads_strict('[' * 600)` da canon.depth aunque el texto es JSON inválido (canon.syntax); documentarlo o comprobar el cierre
- gart-H12 (revisión de bloque): `_emit` comprueba el rango de enteros sobre la subclase y escribe `int(value)`: una subclase con `__int__`→2**60 y `__abs__`→1 pasa; usar `_check_int(int(value), path)`
- gart-H12 (revisión de bloque): los `except RecursionError` dicen «nested too deeply» y los demás «nested deeper»: un código con dos motivos; una constante para el mensaje
- gart-H12 (revisión de bloque): `_emit` repite a mano el escape de `_pointer`; usar `_pointer(key)`
- gart-H3 (revisión de bloque): `dependentRequired` acepta nombres repetidos en una lista (`{'a':['c','c']}` da dos errores iguales); rechazarlos en `_check`
- gart-H3 (revisión de bloque): `GART_COPIES` con una entrada sin `=` deja la ruta vacía y `tests/test_copies.py` revisa el propio repo; fallar con nombre o ruta vacíos
- gart-H3 (revisión de bloque): `tests/test_copies.py` cuenta dos veces los `schemas/` anidados y falla con esquemas inválidos a propósito bajo `tests/**/schemas/`; deduplicar y excluir fixtures
- gart-H3 (revisión de bloque): `tools/copies_probe.py --copy` sin valor da IndexError en vez del uso
- gart-H3 (revisión de bloque): un esquema construido en Python que se contiene (`s['allOf']=[s]`) pasa `_check` y da RecursionError en `validate` (no sale de JSON)
- gart-H3 (revisión de bloque): `test_row_ids_are_unique_and_sorted` compara ids como texto (`D100` < `D99`); limitar el patrón a dos dígitos o ordenar por número
- gart-H3 (revisión de bloque): `copies_probe.py` quita la copia de `sys.path` tras importarla; un import perezoso sale como CRASH falso
- gart-H3 (revisión de bloque): en `gart.diff/0`, D20 y D21 (gimg) no llevan `consumer` y D22 y D23 (gvoice) sí; unificar
- gart-H3 (revisión de bloque): con la misma ruta y código (`required`, `dependentRequired`) el orden sigue el de las claves del esquema; decidir si la inv. 7 pide ordenar también por params
- gart-H3 (revisión de bloque): `test_copies` cuenta como pendiente de gart-H4 un archivo con `$ref` externo aunque tenga además otro error (check_schema para en el primero)
- gart-H3 (revisión de bloque): `check_schema` acepta `minProperties > maxProperties` (y lo mismo con Items y Length): esquema que nadie cumple
- gart-H4 (revisión de bloque): `copies_tests` corre el `plain` de una copia y gart a la vez en el mismo cwd (riesgo de carrera)
- gart-H4 (revisión de bloque): el patrón de `KindId` admite `..` en el nombre: un kind así carga pero no se puede referenciar con `$ref`
- gart-H4 (revisión de bloque): `"<kind>#"` y `"<kind>"` a secas se aceptan como `$ref` mientras `"#"` se rechaza (gart.diff/0 B1)
- gart-H4 (revisión de bloque): `Registry.validate` de un artefacto que no es objeto devuelve `required schema` en vez de un error de tipo
- gart-H4 (revisión de bloque): el adaptador de gvoice en `copies_tests` ignora la carpeta de esquemas que pasa un test de gvoice y usa siempre `gvoice/schemas`
- gart-H4 (revisión de bloque): los commits ab5ffdf y f5b27ca cambiaron código sin actualizar la bitácora
