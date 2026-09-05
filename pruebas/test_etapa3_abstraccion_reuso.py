"""ETAPA 3 · Abstracción y reuso.

Principios 4 (mantener alto el nivel de abstracción),
5 (aumentar la reusabilidad) y 6 (reusar lo que ya existe).

CONCEPTO — el radio de impacto
  La medida honesta de una abstracción no es cuántas interfaces tiene:
  es cuántos archivos se enteran cuando cambia un detalle. En el legado,
  el JSON del proveedor circula por todo el sistema; si el proveedor
  renombra un campo, se rompe cada archivo que lo leyó.

EXPERIMENTO (anote la salida en BITACORA.md)
  $ grep -rn 'data\\|attributes\\|full_name\\|risk_lvl' clinicasegura/
  Cuente las coincidencias. Ese número es su radio de impacto de hoy.
  Repita el mismo grep al terminar la etapa. Prediga antes cuánto bajará.

QUÉ DEBE HACER USTED
  1. dominio/puertos.py con Protocol: Pasarela, Reloj, GeneradorFolio,
     Bitacora. Los define el dominio según lo que NECESITA, no según lo
     que el proveedor ofrece: por eso la operación se llama enviar, no post.
  2. El JSON del proveedor no sale del adaptador. El dominio habla de
     Receta y Despacho.
  3. Principio 6: no reimplemente lo que la biblioteca estándar ya hace.
     La validación de cédula es una expresión regular; el folio sale de
     uuid o secrets; el dinero es Decimal, no float.
"""
import ast
import dataclasses
import inspect
import typing

import pytest

from pruebas.apoyo import (PAQUETE, archivos_py, codigo, codigo_de,
                           identificadores, importar, modulos_importados,
                           obtener)

pytestmark = pytest.mark.etapa3

PUERTOS = {
    "Pasarela": ["enviar"],
    "Reloj": ["ahora"],
    "GeneradorFolio": ["siguiente"],
    "Bitacora": ["registrar"],
}


def test_el_dominio_declara_sus_puertos_como_protocolos():
    mod = importar("clinicasegura.dominio.puertos")
    for nombre, metodos in PUERTOS.items():
        puerto = obtener("clinicasegura.dominio.puertos", nombre)
        assert getattr(puerto, "_is_protocol", False), (
            f"{nombre} debe ser un typing.Protocol.\n"
            f"   Un Protocol define el puerto por su forma, sin obligar a "
            f"la infraestructura a heredar del dominio: la dependencia "
            f"queda invertida de verdad."
        )
        for m in metodos:
            assert hasattr(puerto, m), (
                f"El puerto {nombre} debe declarar el método «{m}»."
            )
    assert mod is not None


def test_los_puertos_hablan_el_idioma_del_dominio_y_no_el_del_proveedor():
    """Se revisan los NOMBRES que usted eligió, no sus comentarios."""
    ruta = PAQUETE / "dominio" / "puertos.py"
    nombres = {n.lower() for n in identificadores(ruta)}
    mecanismo = {"post", "get", "http", "json", "soap", "url", "payload",
                 "request", "response", "sql", "query"}
    delatores = sorted(n for n in nombres
                       if any(m == n or n.startswith(m + "_") or
                              n.endswith("_" + m) for m in mecanismo))
    assert not delatores, (
        f"Los puertos usan nombres del mecanismo: {delatores}.\n"
        f"   Un puerto se nombra por la necesidad del negocio (enviar, "
        f"registrar), nunca por cómo lo resuelve el proveedor. Si la "
        f"operación se llama post, el día que la cadena migre a SOAP el "
        f"nombre miente."
    )


def test_emitir_devuelve_un_tipo_del_dominio_y_no_un_diccionario():
    servicio = obtener("clinicasegura.dominio.servicio", "EmisionDeRecetas")
    retorno = inspect.signature(servicio.emitir).return_annotation
    texto = getattr(retorno, "__name__", str(retorno))
    assert "Despacho" in texto, (
        f"emitir() declara devolver {texto}. Debe devolver un Despacho: "
        f"un diccionario obliga al llamador a adivinar las llaves y deja "
        f"que el estado inválido circule."
    )
    Despacho = obtener("clinicasegura.dominio.modelos", "Despacho")
    campos = {f.name for f in dataclasses.fields(Despacho)}
    assert {"folio", "cadena", "vence"} <= campos, (
        f"Despacho debe tener al menos folio, cadena y vence. Tiene: {campos}"
    )


def test_el_json_del_proveedor_no_sale_del_adaptador():
    fugas = []
    for p in archivos_py():
        if "infraestructura" in str(p):
            continue
        texto = codigo(p)
        for marca in ("full_name", "risk_lvl", "attributes"):
            if marca in texto:
                fugas.append(f"{p.name} contiene {marca}")
    assert not fugas, (
        "El modelo del proveedor se filtró fuera del adaptador:\n   "
        + "\n   ".join(fugas)
        + "\n   Ese es exactamente el radio de impacto que midió al empezar."
    )


def test_no_se_reinventa_lo_que_la_biblioteca_estandar_ya_resuelve():
    """Principio 6: reusar lo existente."""
    validar = None
    for ruta in ("clinicasegura.dominio.modelos",
                 "clinicasegura.aplicacion.borde"):
        mod = importar(ruta)
        for nombre in dir(mod):
            if "cedula" in nombre.lower() and callable(getattr(mod, nombre)):
                validar = getattr(mod, nombre)
    texto = codigo_de()
    assert "re" in modulos_importados_de_todo() or "pydantic" in texto, (
        "La cédula debe validarse con una expresión regular (módulo re) o "
        "con pydantic, no con un recorrido carácter por carácter escrito a "
        "mano.\n   Nunca escriba usted parsers de formatos estándar."
    )
    assert "'0'" not in texto or "'9'" not in texto, (
        "Sobrevivió la comparación carácter por carácter del legado."
    )
    assert validar is None or callable(validar)


def modulos_importados_de_todo() -> set:
    todos = set()
    for p in archivos_py():
        todos |= modulos_importados(p)
    return todos


def test_el_folio_y_el_dinero_usan_los_tipos_correctos():
    todos = modulos_importados_de_todo()
    assert {"uuid", "secrets", "random"} & todos, (
        "Nadie genera folios. Use uuid o secrets desde infraestructura "
        "(y random solo si lo inyecta, nunca incrustado en el dominio)."
    )
    assert "decimal" in todos, (
        "El dinero se representa con Decimal, no con float. Es el ejemplo "
        "canónico de reusar la biblioteca estándar en vez de improvisar."
    )


def test_la_cedula_es_un_tipo_del_dominio_y_no_una_cadena_suelta():
    Cedula = obtener("clinicasegura.dominio.modelos", "Cedula")
    Receta = obtener("clinicasegura.dominio.modelos", "Receta")
    campos = {f.name: f.type for f in dataclasses.fields(Receta)}
    assert "cedula" in campos, "Receta debe tener el campo cedula."
    assert "Cedula" in str(campos["cedula"]), (
        f"Receta.cedula está anotado como {campos['cedula']}. Debe ser el "
        f"tipo Cedula: hacer irrepresentable el estado inválido empieza por "
        f"no usar str para todo."
    )
    assert typing.get_type_hints(Cedula) is not None
