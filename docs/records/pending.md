# Pendiente

Lo que queda abierto; la bitácora solo apunta aquí. Se añade y se quita en este archivo.

## Pendiente

- Comprobar los vectores canónicos (inv. 9) en macOS, Windows y la Deck al cerrar gart-H9: lo hace la persona en cada máquina
- DDD §8 (leves R11 y R12): decidir License antes de gart-H10; gart.diff/0 se queda en /0
- gart-H2: instancias muy anidadas dan RecursionError (900 niveles); límite de profundidad con error propio o documentarlo
- gart-H2: `_ecma_pattern` solo traduce `$` (`[]x]`, `\s`, `.` difieren de ECMA-262)
- gart-H2: un NaN en la instancia pasa `minimum` si el esquema no tiene `type` (lo cierra `loads_strict` en gart-H9 o una comprobación en `validate`)
- gart-H2: un `required` repetido por `$ref` y su hermano da errores duplicados
- gart-H3: gart/schema.py:189 — para floats no finitos el error de `type` dice expected 'number', actual 'number' (`_json_type` vs `_is_type`, D11); proponer actual 'non-finite number' y actualizar test_actual_names_the_json_type_of_the_instance
- gart-H3: gart/schema.py:194 — `_json_type` da 'object' para cualquier no-JSON (tuple, set, bytes); oi da `type(value).__name__`; proponer lo mismo que oi
- gart-H3: gart/schemas/diff.schema.json:61 — una fila sin `resolution` recibe además el error engañoso 'required milestone' porque el `if` se cumple sin resolution; proponer `"required": ["resolution"]` dentro del `if`
