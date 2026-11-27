# Pendiente

Lo que queda abierto; la bitácora solo apunta aquí. Se añade y se quita en este archivo.

## Pendiente

- Comprobar los vectores canónicos (inv. 9) en macOS, Windows y la Deck al cerrar gart-H9: lo hace la persona en cada máquina
- DDD §8 (leves R11 y R12): decidir License antes de gart-H10; gart.diff/0 se queda en /0
- gart-H2: instancias muy anidadas dan RecursionError (900 niveles); límite de profundidad con error propio o documentarlo
- gart-H2: `_ecma_pattern` solo traduce `$` (`[]x]`, `\s`, `.` difieren de ECMA-262)
- gart-H2: un NaN en la instancia pasa `minimum` si el esquema no tiene `type` (lo cierra `loads_strict` en gart-H9 o una comprobación en `validate`)
- gart-H2: un `required` repetido por `$ref` y su hermano da errores duplicados
- gart-H9: `_emit` (gart/canon.py) aplica str()/repr() a subclases: en 3.10 str(IntEnum.A) da 'Cls.A' y canonical_bytes sale inválido; arreglo str(int(v)) y _number(float(v))
- gart-H9: una anidación profunda o cíclica sale como canon.type o canon.syntax («invalid JSON») aunque el JSON sea válido; propuesta canon.depth (mismo tema que el pendiente de profundidad de gart-H2)
- gart-H9: los errores de los hooks de `loads_strict` dejan `path` vacío (p. ej. clave duplicada anidada o float de magnitud ≥ 2^53), aunque CanonError documenta path como JSON Pointer; dar ubicación o documentar que loads_strict no la da
- gart-H9 (revisión hacia main): los vectores de rechazo de números esperan solo «outside»; que cada uno diga «integer outside» o «number outside»
- gart-H9 (revisión hacia main): ningún vector compara ya con los bytes de la muestra de RFC 8785 §3.2.2; recuperar uno con su parte sin números
