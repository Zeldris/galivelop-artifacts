# ¿Dónde está la tabla de namespaces?

<!-- gvc-ddd-decision: q11 -->

Status: accepted

En `gart/namespaces.json`, dato del paquete del que se genera la página. La regla de namespace vale al publicar los esquemas propios, no al cargar copias ajenas.

Por qué: El `Registry` puede leerla y viaja con la copia.

Descartado: `docs/namespaces.md`; no llevar tabla.

Sección de origen: 5. Invariantes
