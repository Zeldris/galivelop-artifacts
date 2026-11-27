<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-c6c4e060-0l41l0` (sesión en la nube; sale de `claude/arranque`) |
| **Fase / tarea** | gart-H9 cerrado y bloque revisado (3 hallazgos aplicados, 4 leves en `docs/records/pending.md`); Q-15 a aplicada (floats ≥ 2^53 rechazados). Antes: bloque gart-H1/H2 revisado (10 hallazgos aplicados, 4 leves en `docs/records/pending.md`). Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit `feat(gart-H9)` |
| **Siguiente paso** | PR #1 (https://github.com/Zeldris/galivelop-artifacts/pull/1) abierto con la marca de 39bb1bb: fusionar con el CI en verde; luego gart-H12 (barrido de `gart/canon.py`) y gart-H3 |
| **Check** | verde tras los arreglos de la revisión (unittest, doctor sin FAIL, ci-local) |

## Para la próxima publicación

gart-H1, H2 y H9 con sus revisiones y la retro 2026-11-27, por pull request (Q-16 a, confirmado por la persona el 2026-11-27).

## Hecho (5 últimas)

1. 2026-11-27 — Fase 1 hacia `main` (diff desde 3326968): sin graves ni medios, 2 leves a pendientes; docs de la inv. 9 y ADR 0007 al día (floats ≥ 2^53).
2. 2026-11-27 — Revisión del bloque gart-H9: entero enorme y sustitutos sueltos rechazados por `loads_strict` como CanonError, motivos de test no vacíos; 4 leves apuntados.
3. 2026-11-27 — gart-H9: `gart/canon.py` (`CanonError`, `loads_strict`, `canonical_bytes` JCS, `content_hash`, `file_hash`), vectores en `tests/vectors/canon.json` y 16 tests.
4. 2026-11-27 — Revisión del bloque gart-H1/H2: 10 arreglos (KindId ida y vuelta y versión enorme, `$ref` a no-esquema, raíz `""`, orden por (ruta, código), propertyNames con causa, números enormes); 4 leves apuntados.
5. 2026-11-27 — gart-H2: `gart/schema.py` (`SchemaError`, `ValidationError`, `check_schema`, `validate`), portado de gvoice; 56 tests.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
