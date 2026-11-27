<!-- galivelop-workflow v0.9.1 -->
# Bitácora (traspaso)

> Léela entera al empezar cualquier sesión. Lo que no está subido no existe: commit + push en cada punto estable,
> con esta bitácora actualizada en el mismo commit. El flujo nunca la sobrescribe una vez creada.

## Estado actual

| Campo | Valor |
|---|---|
| **Rama** | `ccr-70ec6319-y2c8pd` (sesión en la nube; sale de `main` tras el PR #1) |
| **Fase / tarea** | gart-H12 cerrado (5 leves de gart-H9; revisado en la sesión: diff de un archivo y vectores). PR #1 (gart-H1, H2, H9) fusionado en `main`. Presupuesto de compactaciones: 0 |
| **Último punto estable** | el commit `gart-H12: barrido de gart/canon.py` |
| **Siguiente paso** | gart-H3: unificar las cuatro copias (tabla `gart.diff/0` primero); Q-17 (License) se decide antes de gart-H10 |
| **Check** | verde (95 tests, doctor sin FAIL, ci-local); el CI de 52116ba salió rojo (`test_deep_text`: en el Python del CI `json.loads` no desborda) y se arregló con `MAX_DEPTH` |

## Para la próxima publicación

gart-H12 (barrido del canon), por pull request como el #1.

## Hecho (5 últimas)

1. 2026-11-27 — gart-H12: `_emit` con subclases de int/float, código `canon.depth` (anidación profunda o cíclica), path vacío de `loads_strict` documentado, límite `MAX_DEPTH` = 256 igual en todas las versiones de Python, motivos en los vectores int_range y vector RFC 8785 §3.2.2 sin 1E30.
2. 2026-11-27 — Fase 1 hacia `main` (diff desde 3326968): sin graves ni medios, 2 leves a pendientes; docs de la inv. 9 y ADR 0007 al día (floats ≥ 2^53).
3. 2026-11-27 — Revisión del bloque gart-H9: entero enorme y sustitutos sueltos rechazados por `loads_strict` como CanonError, motivos de test no vacíos; 4 leves apuntados.
4. 2026-11-27 — gart-H9: `gart/canon.py` (`CanonError`, `loads_strict`, `canonical_bytes` JCS, `content_hash`, `file_hash`), vectores en `tests/vectors/canon.json` y 16 tests.
5. 2026-11-27 — Revisión del bloque gart-H1/H2: 10 arreglos (KindId ida y vuelta y versión enorme, `$ref` a no-esquema, raíz `""`, orden por (ruta, código), propertyNames con causa, números enormes); 4 leves apuntados.

## Pendiente

Lo pendiente está en [`docs/records/pending.md`](records/pending.md); se añade y se quita allí.

## Comprobar el estado

- Últimos commits: `git fetch origin <rama> && git log --oneline -5 origin/<rama>`.
- El check: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- Flujo bien montado: `python3 .claude/gw/scripts/doctor.py`.
- Estado de la bitácora tal como lo recibe una sesión nueva: `python3 .claude/gw/scripts/recover.py --state`.
