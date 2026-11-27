# Pendiente

Lo que queda abierto; la bitácora solo apunta aquí. Se añade y se quita en este archivo.

## Pendiente

- Comprobar los vectores canónicos (inv. 9) en macOS, Windows y la Deck al cerrar gart-H9: lo hace la persona en cada máquina
- DDD §8 (leves R11 y R12): decidir License antes de gart-H10; gart.diff/0 se queda en /0
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
