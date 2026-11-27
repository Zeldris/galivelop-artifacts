<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-70ec6319-y2c8pd` (sesión en la nube; sale de `main` tras el PR #1) |
| **Fase / tarea** | gart-H3 hecho, falta su revisión de bloque: palabras clave de ADR 0015 y `actual` en `type` (8c81320); tabla `gart.diff/0` (`docs/records/gart-diff.json`, 12 filas, cada uno de los 68 tests de las copias que fallan tiene la suya, comprobado con `docs/records/gart-H3/coverage.py`). Copias clonadas en solo lectura: `/home/user/galivelop-developer`, `/home/user/galivelop-client-catcher`, `/home/user/zeldris/galivelop-{image,voice}-generator`. Q-17 (License, gart-H10) sigue abierta. Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit `feat(gart-H3): tabla gart.diff/0…` |
| **Siguiente paso** | revisión del bloque gart-H3 (diff desde dc424ed^: `gart/schema.py`, `gart/schemas/`, `tests/test_diff_table.py`, `docs/records/gart-H3/`); luego gart-H4 (`Registry`, `load_schema`, `$ref` a archivo hermano: cierra D01) |
| **Check** | verde en local (ver el commit); CI de 8c81320 por mirar |

## Para la próxima publicación

gart-H12 (barrido del canon), por pull request como el #1.

## Hecho (5 últimas)

1. 2026-11-27 — gart-H3: maxProperties, dependentRequired, allOf, if/then/else y `actual` en `type` (ADR 0015); tabla `gart.diff/0` con esquema, test y cruce con el harness.
2. 2026-11-27 — gart-H12: `_emit` con subclases de int/float, código `canon.depth` (anidación profunda o cíclica), path vacío de `loads_strict` documentado, límite `MAX_DEPTH` = 256 igual en todas las versiones de Python, motivos en los vectores int_range y vector RFC 8785 §3.2.2 sin 1E30.
3. 2026-11-27 — Fase 1 hacia `main` (diff desde 3326968): sin graves ni medios, 2 leves a pendientes; docs de la inv. 9 y ADR 0007 al día (floats ≥ 2^53).
4. 2026-11-27 — Revisión del bloque gart-H9: entero enorme y sustitutos sueltos rechazados por `loads_strict` como CanonError, motivos de test no vacíos; 4 leves apuntados.
5. 2026-11-27 — gart-H9: `gart/canon.py` (`CanonError`, `loads_strict`, `canonical_bytes` JCS, `content_hash`, `file_hash`), vectores en `tests/vectors/canon.json` y 16 tests.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
