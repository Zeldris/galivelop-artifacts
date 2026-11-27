<!-- galivelop-workflow v0.9.1 -->
# Glosario

Vocabulario de galivelop-artifacts. Primero van los términos del flujo; el proyecto añade debajo los de su dominio y los
mantiene al día (skill `domain-modeling`). El flujo nunca sobrescribe este archivo una vez creado.

## Términos del flujo

- **Bitácora**: `docs/handoff.md`, el estado del trabajo para la siguiente sesión: rama, tarea en curso, siguiente paso,
  check.
- **Relevo**: una sesión que se acaba y otra que sigue desde la bitácora, sin preguntar por dónde iba.
- **Punto estable**: un estado con el check en verde, con commit y subido.
- **Check**: las órdenes del proyecto que tienen que pasar en cada commit que se sube: `bash -n .githooks/pre-commit`, `bash -n .githooks/pre-push`, `python3 -m unittest discover -s tests -t .`, `python3 .claude/gw/scripts/doctor.py`, `python3 .claude/gw/scripts/ci-local.py --validate`.
- **Commit `WIP:`**: un commit subido con algo a medias o en rojo; la bitácora dice qué falla y por qué.
- **Rama protegida**: `main`, lo publicado; solo recibe trabajo revisado, con confirmación
  de la persona.
- **Marca de revisión**: `docs/records/reviewed.txt`, el archivo versionado con el sha del último commit revisado; los ganchos
  aceptan código hasta él.
- **Contenido frente a código**: el contenido (lo que casa con `content` de `.claude/gw.json`) no necesita revisión
  de código; todo lo demás es código.
- **Encargo a un subagente**: lo que recibe un subagente: objetivo, rutas, restricciones, el check que debe pasar y
  qué tiene que devolver.
- **Retro**: la retrospectiva de la sesión antes de ir a la rama protegida; sus propuestas se presentan a la persona y
  lo que confirme se aplica en la rama.
- **Propuesta (`.gw-new`)**: un archivo del flujo que la actualización no pudo aplicar sin perder cambios locales;
  se fusiona a mano y luego se borra.

## Términos del proyecto

<!-- gvc:ddd-glossary:begin -->
- **Esquema**: Documento JSON Schema (subconjunto soportado, §6) que describe un tipo de artefacto en una versión (`Schema`)
- **Artefacto**: Documento JSON que declara su tipo y se valida contra su esquema (`Artifact`)
- **Tipo de artefacto**: `<espacio>.<nombre>/<versión>`, p. ej. `gve.evidence/1`. La versión es un entero mayor (`KindId`)
- **Espacio**: El repo dueño del tipo: `gve`, `gdev`, `gimg`, `gvoice`, `gcc`… Solo su dueño publica en él (`namespace`)
- **Registro**: Conjunto de esquemas y migraciones conocidos, cargado de carpetas locales (`Registry`)
- **Validación**: Comprobar un artefacto contra su esquema; devuelve una lista de errores, nunca lanza por un dato inválido (`validate()`)
- **Error de validación**: `path` (JSON Pointer), `code` (`required`, `type`…) y parámetros; el texto sale del catálogo es/en (`ValidationError`)
- **Migración**: Función pura que lleva un artefacto de `/n` a `/n+1` (`Migration`)
- **Versión provisional**: Tipo en pruebas: puede cambiar sin migración; nunca se publica como estable (`/0`)
<!-- gvc:ddd-glossary:end -->
