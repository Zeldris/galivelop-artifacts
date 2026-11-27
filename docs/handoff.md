<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-c6c4e060-0l41l0` (sesión en la nube; sale de `claude/arranque`) |
| **Fase / tarea** | gart-H9 hecho (`gart/canon.py`, vectores y tests), pendiente de revisión de bloque. Antes: bloque gart-H1/H2 revisado (10 hallazgos aplicados, 4 leves en `docs/records/pending.md`). Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit `feat(gart-H9)` |
| **Siguiente paso** | Revisión de bloque de gart-H9 y luego decidir con la persona `main` (tres fases) o gart-H10 |
| **Check** | verde tras los arreglos de la revisión (unittest, doctor sin FAIL, ci-local) |

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. 2026-11-27 — gart-H9: `gart/canon.py` (`CanonError`, `loads_strict`, `canonical_bytes` JCS, `content_hash`, `file_hash`), vectores en `tests/vectors/canon.json` y 16 tests.
2. 2026-11-27 — Revisión del bloque gart-H1/H2: 10 arreglos (KindId ida y vuelta y versión enorme, `$ref` a no-esquema, raíz `""`, orden por (ruta, código), propertyNames con causa, números enormes); 4 leves apuntados.
3. 2026-11-27 — gart-H2: `gart/schema.py` (`SchemaError`, `ValidationError`, `check_schema`, `validate`), portado de gvoice; 56 tests.
4. 2026-11-27 — CI de GitHub arranca otra vez (verde en f45a1ce); quitado de pendientes.
5. 2026-11-27 — Flujo a v0.9.1 (`/gw-update`): 110 archivos del flujo, `gw.json`, 2 reglas nuevas en `REVIEW.md`, marcadores.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
