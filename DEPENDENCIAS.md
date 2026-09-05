# Dependencias externas

Una fila por dependencia externa que el proyecto usa hoy, incluidas las de
la práctica. Complete las cuatro columnas: sin ruta de salida, la
dependencia es un compromiso indefinido.

| Dependencia | Versión acotada | Licencia | Riesgo | Ruta de salida |
|-------------|-----------------|----------|--------|----------------|
| pytest | >=8.0,<9.0 | MIT | Bajo. Es el estándar de facto para pruebas en Python, con comunidad muy grande y mantenimiento activo. | Si se descontinuara, migrar a unittest (viene incluido en Python) sería directo, aunque tomaría tiempo reescribir los tests. |
| pydantic | >=2.0,<3.0 | MIT | Bajo-medio. Muy usado en la industria, pero la migración de v1 a v2 cambió bastante la API, así que futuras versiones mayores podrían romper cosas. | Reemplazar la validación por dataclasses propias con validación manual (funciones que revisan los datos a mano). |
| Python (biblioteca estándar: sqlite3, urllib, json, uuid, secrets, decimal) | 3.12 o superior | PSF License (libre) | Bajo. Es la biblioteca estándar del lenguaje, no depende de terceros y Python tiene soporte a largo plazo. | No aplica una "salida" como tal, pero si algún módulo se deprecia, la alternativa está documentada en la guía oficial de Python. |
