# ¿Qué reglas sigue el JSON canónico?

<!-- gvc-ddd-decision: q7 -->

Status: accepted

RFC 8785 (JCS) tal cual, con orden UTF-16 y números ECMAScript escritos con la biblioteca estándar. Se rechazan en la entrada los números (enteros o no) fuera de ±(2^53−1), `NaN`, `±Inf`, `-0`, las claves duplicadas (`loads_strict`) y más de 256 niveles de anidación (`MAX_DEPTH`, para que el límite no dependa de la versión de Python).

Por qué: Es un estándar que otro lenguaje puede reproducir.

Descartado: Reglas propias; ordenar por punto de código, como decía el borrador 2.

Sección de origen: 5. Invariantes
