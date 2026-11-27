<!-- galivelop-workflow v0.9.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-c6c4e060-0l41l0` (sesión en la nube; sale de `claude/arranque`) |
| **Fase / tarea** | gw-update 0.9.0→0.9.1 en preparación (simulacro hecho, nada aplicado); gart-H2 en espera. Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit de gart-H1 |
| **Siguiente paso** | Esperar las respuestas de la persona a Q-9..Q-12 (`docs/questions.md`): rama, `apply.py --update`, fusión a mano de `REVIEW.md` y marcadores, y acceso de un subagente a las 4 copias. Luego gw-update y, tras él, gart-H2 con `merge-main.py` y `gw-orchestrate-dealer` |
| **Check** | `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (gart-H1) |

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. 2026-11-27 — gart-H1: `KindId` (análisis, validación, `/0` provisional, `next()`), inv. 1 con tabla de válidos e inválidos.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
