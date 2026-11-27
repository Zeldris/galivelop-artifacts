<!-- galivelop-workflow v0.9.0 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `claude/arranque` |
| **Fase / tarea** | DDD final escrito (`docs/records/ddd-galivelop-artifacts.md`, q1–q14 y ADR 0001–0014), pendiente de que la persona lo lea. Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit del DDD final |
| **Siguiente paso** | tras la lectura de la persona, empezar gart-H1 (`KindId`); a `main` solo con su confirmación y las tres fases |
| **Check** | `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`: verde (árbol `cbc403d`) |

## Para la próxima publicación

_(lo que va a `main` a continuación, y a qué espera)_

## Hecho (5 últimas)

1. _(fecha — qué se cerró, en dos líneas como mucho: el detalle está en el commit; la más antigua sale cuando hay más
   de 5, el historial está en git)_

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
