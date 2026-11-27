# ¿Cómo se versiona gart y se comprueban las copias?

<!-- gvc-ddd-decision: q12 -->

Status: accepted

Semver; el `VENDOR.json` es la tabla de cada versión. El CI de gart la casa con su tag y el CHANGELOG solo la enlaza. Una menor nunca rompe un esquema estable.

Por qué: El consumidor no tiene el CHANGELOG y comprueba sin red. Límite: no detecta que se editen a la vez un archivo y su `VENDOR.json`.

Descartado: Tabla de hashes en el CHANGELOG; sin tabla.

Sección de origen: 5. Invariantes
