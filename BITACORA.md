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

**Sello:** fa2d7d8876cee3ab

## Etapa 2 — Reducir el acoplamiento

**Predicción:** Creo que hasta 4 lugares cambian el comportamiento si se modifica CONFIG["vigencia_dias"], porque la línea donde se calcula `vence` en def emitir y los bloques de farmauno,saludtotal y cruzverde usan el valor `vence`. Aunque solo hay una lectura como tal de CONFIG el efecto se extiende por el if/elif.

**Observación:** cuando se ejecuta el comando no hay ningun error o advertencia es un cambio sigiloso. Cualquier instancia de ServicioRecetas que se haga luego de esa línea en cualquier parte va a calcular vigencias de 1 día en vez de 30. Es un problema de acoplamiento porque existe pero no está declarada en ninguna firma de función.

```
Nicole@DESKTOP-4CA2HN8 MINGW64 ~/Documents/GitHub/practica-principios-diseno (main)
$ python
Python 3.13.7 (tags/v3.13.7:bcee1c3, Aug 14 2025, 14:15:11) [MSC v.1944 64 bit (AMD64)] on win32
Type "help", "copyright", "credits" or "license" for more information.
>>> from clinicasegura.legado import CONFIG, ServicioRecetas
... CONFIG["vigencia_dias"] = 1
...
>>>
(.venv)
Nicole@DESKTOP-4CA2HN8 MINGW64 ~/Documents/GitHub/practica-principios-diseno (main)
$ pytest -m etapa2
.FFF.                                                                                                                                                                                                      [100%]
=================================================================================================== FAILURES ====================================================================================================
________________________________________________________________________ test_la_regla_de_negocio_es_una_funcion_pura_de_firma_estrecha _________________________________________________________________________
pruebas\apoyo.py:22: in importar
    return importlib.import_module(ruta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'clinicasegura.dominio.reglas'

During handling of the above exception, another exception occurred:
pruebas\test_etapa2_acoplamiento.py:68: in test_la_regla_de_negocio_es_una_funcion_pura_de_firma_estrecha
    calcular = obtener("clinicasegura.dominio.reglas", "calcular_recargo")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pruebas\apoyo.py:38: in obtener
    mod = importar(ruta)
          ^^^^^^^^^^^^^^
pruebas\apoyo.py:24: in importar
    pytest.fail(
E   Failed: Falta el módulo «clinicasegura.dominio.reglas».
E      Cree el archivo clinicasegura/dominio/reglas.py (y el __init__.py de su paquete).
E      Detalle: No module named 'clinicasegura.dominio.reglas'
_______________________________________________________________________ test_la_regla_de_negocio_no_tiene_efectos_ni_depende_del_entorno ________________________________________________________________________
pruebas\apoyo.py:22: in importar
    return importlib.import_module(ruta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'clinicasegura.dominio.reglas'

During handling of the above exception, another exception occurred:
pruebas\test_etapa2_acoplamiento.py:87: in test_la_regla_de_negocio_no_tiene_efectos_ni_depende_del_entorno
    calcular = obtener("clinicasegura.dominio.reglas", "calcular_recargo")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pruebas\apoyo.py:38: in obtener
    mod = importar(ruta)
          ^^^^^^^^^^^^^^
pruebas\apoyo.py:24: in importar
    pytest.fail(
E   Failed: Falta el módulo «clinicasegura.dominio.reglas».
E      Cree el archivo clinicasegura/dominio/reglas.py (y el __init__.py de su paquete).
E      Detalle: No module named 'clinicasegura.dominio.reglas'
_______________________________________________________________________________ test_el_caso_de_uso_no_recibe_diccionarios_crudos _______________________________________________________________________________
pruebas\apoyo.py:22: in importar
    return importlib.import_module(ruta)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
..\..\..\AppData\Local\Programs\Python\Python313\Lib\importlib\__init__.py:88: in import_module
    return _bootstrap._gcd_import(name[level:], package, level)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
E   ModuleNotFoundError: No module named 'clinicasegura.dominio.servicio'

During handling of the above exception, another exception occurred:
pruebas\test_etapa2_acoplamiento.py:106: in test_el_caso_de_uso_no_recibe_diccionarios_crudos
    servicio = obtener("clinicasegura.dominio.servicio", "EmisionDeRecetas")
               ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
pruebas\apoyo.py:38: in obtener
    mod = importar(ruta)
          ^^^^^^^^^^^^^^
pruebas\apoyo.py:24: in importar
    pytest.fail(
E   Failed: Falta el módulo «clinicasegura.dominio.servicio».
E      Cree el archivo clinicasegura/dominio/servicio.py (y el __init__.py de su paquete).
E      Detalle: No module named 'clinicasegura.dominio.servicio'
============================================================================================ short test summary info ============================================================================================
FAILED pruebas/test_etapa2_acoplamiento.py::test_la_regla_de_negocio_es_una_funcion_pura_de_firma_estrecha - Failed: Falta el módulo «clinicasegura.dominio.reglas».
FAILED pruebas/test_etapa2_acoplamiento.py::test_la_regla_de_negocio_no_tiene_efectos_ni_depende_del_entorno - Failed: Falta el módulo «clinicasegura.dominio.reglas».
FAILED pruebas/test_etapa2_acoplamiento.py::test_el_caso_de_uso_no_recibe_diccionarios_crudos - Failed: Falta el módulo «clinicasegura.dominio.servicio».
3 failed, 2 passed, 79 deselected in 0.33s
(.venv)

```

**Explicación:** La predicción que hice de 4 lugares estuvo bien para describir el efecto de acoplamiento básico, pero el arreglo real no era declarar la dependencia en esos 4 lugares era eliminarla del todo.calcular_recargo() en dominio/reglas.py (línea 14) ahora recibe tarifa_diaria como parámetro explícito en vez de leer CONFIG global, así que ya no hay ningún lugar donde un cambio externo silencioso pueda afectar el cálculo.

**Sello:** f5c6e182ed1c9acb

## Etapa 3 — Abstracción y reuso

**Predicción:** Creo que van a haber 4 coincidencias del grep en clinicasegura/, siento que las de legado.py en buscar_paciente() y reporte()

**Observación:** El grep encontró 7 coincidencias en archivos de texto y 4 más en binarios. Aunque 4 vienen de la palabra data dentro de "dataclasses" en modelos.py y no tienen nada que ver con el json del proveedor. Solo 3 son problema real: legado.py:125 (un parámetro de urllib) y legado.py:150-151 donde si es un problema  paciente["data"]["attributes"]["risk_lvl"]. Mi predicción en número fue baja pero si fue buena al conciderar legado.py como problema.

```
Nicole@DESKTOP-4CA2HN8 MINGW64 ~/Documents/GitHub/practica-principios-diseno (main)
$ grep -rn 'data\|attributes\|full_name\|risk_lvl' clinicasegura/
clinicasegura/dominio/modelos.py:7:from dataclasses import dataclass
clinicasegura/dominio/modelos.py:10:@dataclass(frozen=True)
clinicasegura/dominio/modelos.py:15:@dataclass(frozen=True)
clinicasegura/dominio/modelos.py:23:@dataclass(frozen=True)
Binary file clinicasegura/dominio/__pycache__/errores.cpython-313.pyc matches
Binary file clinicasegura/dominio/__pycache__/modelos.cpython-313.pyc matches
Binary file clinicasegura/dominio/__pycache__/servicio.cpython-313.pyc matches
clinicasegura/legado.py:125:                    data=json.dumps(cuerpo).encode("utf-8"),
clinicasegura/legado.py:150:            paciente["data"]["attributes"]["full_name"],
clinicasegura/legado.py:151:            paciente["data"]["attributes"]["risk_lvl"],
Binary file clinicasegura/__pycache__/legado.cpython-313.pyc matches
(.venv)
Nicole@DESKTOP-4CA2HN8 MINGW64 ~/Documents/GitHub/practica-principios-diseno (main)
$

```

**Explicación:** La predicción de 4 se quedó corta contra 7 coincidencias de texto reales pero 4 de esas eran falsos positivos de la palabra data dentro de dataclasses. Repetí el grep al cerrar la etapa y el resultado es el mismo:las únicas 
coincidencias reales del JSON del proveedor siguen en legado.py:150-151, que por 
consigna debe permanecer intacto como referencia del "antes". Cero código nuevo 
(dominio/, aplicacion/, infraestructura/) contiene full_name, risk_lvl o attributes 
el lugar de impacto real bajó de 2 líneas contaminadas a 0, aunque el grep crudo 
no lo muestre así por los falsos positivos de "dataclass".

**Sello:**  48e8030872082da9

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
