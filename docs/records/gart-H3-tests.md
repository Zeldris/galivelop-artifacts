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
