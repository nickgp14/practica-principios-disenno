# Bitácora de la práctica

Estudiante: Nicole Ivette Gamboa Padilla
Carné: 2025109339

> Cómo se llena cada entrada, en este orden y sin saltarse pasos:
>
> 1. **Predicción** — escríbala ANTES de correr nada. Qué cree que va a
>    pasar y por qué. Equivocarse aquí y entender después vale más que
>    acertar; no vuelva a corregirla.
> 2. **Observación** — corra el experimento de la etapa y pegue la salida.
> 3. **Explicación** — por qué pasó lo que pasó, en sus palabras, citando
>    **su** archivo y **su** línea (`servicio.py:24`).
> 4. **Sello** — corra `python herramientas/marcador.py` al cerrar la
>    etapa y pegue el sello que imprime.

## Etapa 0 — Diagnóstico

**Predicción:** Creo que pueden haber al menos 8 o 9 principios violados, ya que el enunciado dice que ServicioRecetas valida,calcula, habla HTTP, escribe en la bd, genera folios, y exporta, al final con todo eso se violan principios en cadena: cohesión, acoplamiento (normalmente una clase con demasiadas responsabilidades depende de muchas cosas externas), abstracción porque si se mezcla HTTP y BD muy poco probable que haya una interfaz limpia y quizá también testeabilidad porque con una clase así debe ser difícil de levantar.

**Observación:** Cuando leí el archivo de legado.py conté 10 de los 11 principios violados: 1 (Divide y vencerás),2 (Cohesión), 3 (Acoplamiento), 4 (Abstracción), 5 (Reusabilidad), 6 (Reuso de código existente), 7 (Flexibilidad), 9(Portabilidad), 10 (Testabilidad), 11 (Diseño defensivo).

```
```

**Explicación:** Mi predición fue de 8-9 y el resultado real fue de 10, un poco por encima de lo que esperaba. 
Subestimé el acoplamiento (principio 3) y la testabilidad (principio 10): no anticipé que el reloj (datetime.now(),línea 68) y el generador de folios (random.randint, línea 71) estuvieran incrustados directamente en emitir().
**Sello:** 55c7ed9262c7c871

## Etapa 1 — Dividir y conquistar, cohesión

**Predicción:** Creo que podrían hacerse 3 más, uno para las tipo plantillas de  Receta, cedula (osea sus campos), otro para funciones puras y otro para manejar errores.

**Observación:**

```
Nicole@DESKTOP-4CA2HN8 MINGW64 ~/Documents/GitHub/practica-principios-diseno (main)
$ pytest -m etapa1
FFF....                                                                                                                                                                                                    [100%]
=================================================================================================== FAILURES ====================================================================================================
________________________________________________________________________________________ test_existen_los_tres_paquetes _________________________________________________________________________________________
pruebas\apoyo.py:22: in importar
    return importlib.import_module(ruta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'clinicasegura.dominio'

During handling of the above exception, another exception occurred:
pruebas\test_etapa1_division_cohesion.py:37: in test_existen_los_tres_paquetes
    importar(f"clinicasegura.{paquete}")
pruebas\apoyo.py:24: in importar
    pytest.fail(
E   Failed: Falta el módulo «clinicasegura.dominio».
E      Cree el archivo clinicasegura/dominio.py (y el __init__.py de su paquete).
E      Detalle: No module named 'clinicasegura.dominio'
_______________________________________________________________________________ test_el_dominio_define_sus_tipos_y_son_inmutables _______________________________________________________________________________
pruebas\apoyo.py:22: in importar
    return importlib.import_module(ruta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'clinicasegura.dominio'

During handling of the above exception, another exception occurred:
pruebas\test_etapa1_division_cohesion.py:42: in test_el_dominio_define_sus_tipos_y_son_inmutables
    tipo = obtener("clinicasegura.dominio.modelos", nombre)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pruebas\apoyo.py:38: in obtener
    mod = importar(ruta)
          ^^^^^^^^^^^^^^
pruebas\apoyo.py:24: in importar
    pytest.fail(
E   Failed: Falta el módulo «clinicasegura.dominio.modelos».
E      Cree el archivo clinicasegura/dominio/modelos.py (y el __init__.py de su paquete).
E      Detalle: No module named 'clinicasegura.dominio'
__________________________________________________________________________________ test_el_dominio_define_sus_propios_errores ___________________________________________________________________________________
pruebas\apoyo.py:22: in importar
    return importlib.import_module(ruta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'clinicasegura.dominio'

During handling of the above exception, another exception occurred:
pruebas\test_etapa1_division_cohesion.py:54: in test_el_dominio_define_sus_propios_errores
    base = obtener("clinicasegura.dominio.errores", "ErrorDominio")
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pruebas\apoyo.py:38: in obtener
    mod = importar(ruta)
          ^^^^^^^^^^^^^^
pruebas\apoyo.py:24: in importar
    pytest.fail(
E   Failed: Falta el módulo «clinicasegura.dominio.errores».
E      Cree el archivo clinicasegura/dominio/errores.py (y el __init__.py de su paquete).
E      Detalle: No module named 'clinicasegura.dominio'
============================================================================================ short test summary info ============================================================================================
FAILED pruebas/test_etapa1_division_cohesion.py::test_existen_los_tres_paquetes - Failed: Falta el módulo «clinicasegura.dominio».
FAILED pruebas/test_etapa1_division_cohesion.py::test_el_dominio_define_sus_tipos_y_son_inmutables - Failed: Falta el módulo «clinicasegura.dominio.modelos».
FAILED pruebas/test_etapa1_division_cohesion.py::test_el_dominio_define_sus_propios_errores - Failed: Falta el módulo «clinicasegura.dominio.errores».
3 failed, 4 passed, 77 deselected in 0.27s
(.venv)
Nicole@DESKTOP-4CA2HN8 MINGW64 ~/Documents/GitHub/practica-principios-diseno (main)
$
```
3 test fallan porque faltan módulos nuevos. Los otros 4 pasan porqie no hay problemas (dominio no importa infraestructura, no llama al reloj y nada importa legado.py)
**Explicación:** La predición de 3 archivos no fue del todo correcta porque si era el contenido(tipos,funciones,errores) pero son 3 paquetes completos con dominio, aplicación e infraestructura.

**Sello:**

## Etapa 2 — Reducir el acoplamiento

**Predicción:**

**Observación:**

```
```

**Explicación:**

**Sello:**

## Etapa 3 — Abstracción y reuso

**Predicción:**

**Observación:**

```
```

**Explicación:**

**Sello:**

## Etapa 4 — Flexibilidad, obsolescencia y portabilidad

**Predicción:**

**Observación:**

```
```

**Explicación:**

**Sello:**

## Etapa 5 — Testabilidad

**Predicción:**

**Observación:**

```
```

**Explicación:**

**Sello:**

## Etapa 6 — Diseño defensivo

**Predicción:**

**Observación:**

```
```

**Explicación:**

**Sello:**

## Cierre — Los principios en conflicto

Nombre dos principios que se estorbaron entre sí en SU rediseño, y con qué
criterio resolvió el conflicto. Cite el archivo donde se ve la decisión.

**Conflicto 1:**

**Conflicto 2:**
