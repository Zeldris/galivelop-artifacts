# gart-H3: los tests de cada copia contra gart

`python3 -I tools/copies_tests.py --copy ...` (2026-11-28) corre la suite de cada copia tal cual y con `check_schema`
y `validate` de gart (misma clase de error y forma de ruta que la copia). Clones en los commits de `gart.diff/0`.

| Copia | Tests | Fallan ya sin gart | Fallan solo con gart | Filas |
|---|---|---|---|---|
| gdev | 1444 | 0 | 0 | — |
| gimg | 2096 | 0 | 0 | — |
| gvoice | 747 de 775 (un módulo no importa) | 0 | 331 | 328 + 2 por `$ref` a archivo hermano (D29, gart-H4); 1 por el ciclo visto ya en `check_schema` (D12) |
| oi | 510 | 3 (`test_evidence*`, ajenos al validador) | 37 | params `property`/`actual` (D31), texto de `SchemaError` (D32), ruta y orden (D24, D28) |

Ninguna diferencia nueva de conducta: gart es igual o más estricto en todas. Lo que falta para que las cuatro pasen
es el `Registry` (gvoice, gart-H4) y la forma del error en oi.

**Cierre (Q-20 a, Q-21 a):** gart-H3 se cierra así; gvoice se vuelve a pasar con `copies_tests.py` al cerrar gart-H4 y oi al migrar (gart-H8). gart añade `actual` al error `type` y mantiene `name` (D31).

## gart-H4

`python3 -I tools/copies_tests.py --copy gvoice=/home/user/zeldris/galivelop-voice-generator` (2026-11-28), con el adaptador
de gvoice pasando por un `Registry` cargado con `gvoice/schemas` (`foreign=True`) y `validate_schema(..., base=carpeta)`.

| Copia | Tests | Fallan ya sin gart | Fallan solo con gart, antes | Fallan solo con gart, ahora |
|---|---|---|---|---|
| gvoice | 775 (ya importan todos) | 0 | 331 | 4 |

Los 328 + 2 fallos por `$ref` a archivo hermano (D29) desaparecen. Quedan 4, todos de texto o de orden, ninguno de
conducta más laxa:

- `RefTests.test_cyclic_ref_is_a_schema_error_not_recursion`: gart ya ve el ciclo en `check_schema` (D12), gvoice lo
  espera solo en `validate`.
- `RefTests.test_non_schema_file_ref_is_rejected`, `RefTests.test_ref_leaving_the_folder_is_rejected` y
  `SchemaCheckTests.test_remote_ref_rejected`: gvoice espera los textos «not local» y «leaves the schemas folder»; gart
  rechaza los mismos `$ref` (`pack.json`, `../x.schema.json`, `http://...`) con otro motivo («neither a kind id nor a
  sibling file name», «remote or unsafe reference»). Es la diferencia de texto del error (D32); se cierra al migrar
  gvoice a gart.

El «antes» (331) es la medición de gart-H3 de arriba: la suite entera tarda mucho, no se repitió.

**Decisión (revisión de bloque, inv. 2):** un kind estable solo puede hacer `$ref` a su propio documento (`#/...`) y a otros kinds estables; un `$ref` a un archivo hermano o a un kind `/0` es `SchemaError` en `load` y en `pin`. Así su huella cubre todo lo que acepta (los destinos son estables, fijados y sujetos a la misma regla). Consecuencia: `gart.common/0` solo se puede usar desde kinds estables cuando pase a `/1`.
