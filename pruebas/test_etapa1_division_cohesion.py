"""ETAPA 1 · Dividir y conquistar, y subir la cohesión.

Principios 1 (dividir y conquistar) y 2 (aumentar la cohesión).

Qué debe hacer usted:
  Partir el monolito en tres paquetes con responsabilidades distintas:

    clinicasegura/dominio/         reglas y tipos del negocio. No conoce
                                   red, ni base de datos, ni reloj.
      modelos.py    Cedula, Receta, Despacho   (dataclasses congelados)
      reglas.py     funciones puras de negocio
      errores.py    ErrorDominio y sus descendientes
    clinicasegura/aplicacion/      traduce el mundo exterior al dominio
    clinicasegura/infraestructura/ habla con el mundo exterior

  Nadie fuera de infraestructura puede importar red, base de datos ni reloj.

Criterio de logro:
  Cada módulo se puede describir en una frase sin usar la palabra «y».
"""
import ast
import dataclasses

import pytest

from pruebas.apoyo import (arbol, archivos_py, codigo, importar,
                           modulos_importados, obtener)

pytestmark = pytest.mark.etapa1

INFRA = {"urllib", "requests", "httpx", "sqlite3", "psycopg", "boto3",
         "socket", "http"}


def test_existen_los_tres_paquetes():
    for paquete in ("dominio", "aplicacion", "infraestructura"):
        importar(f"clinicasegura.{paquete}")


def test_el_dominio_define_sus_tipos_y_son_inmutables():
    for nombre in ("Cedula", "Receta", "Despacho"):
        tipo = obtener("clinicasegura.dominio.modelos", nombre)
        assert dataclasses.is_dataclass(tipo), (
            f"{nombre} debe ser un dataclass: un tipo abstracto de datos "
            f"fija operaciones e invariantes, no una bolsa de atributos."
        )
        assert tipo.__dataclass_params__.frozen, (
            f"{nombre} debe ser frozen=True. Un valor del dominio que se "
            f"puede mutar desde fuera no tiene invariantes que valgan."
        )


def test_el_dominio_define_sus_propios_errores():
    base = obtener("clinicasegura.dominio.errores", "ErrorDominio")
    assert issubclass(base, Exception)
    for nombre in ("RecetaInvalida", "CadenaNoSoportada",
                   "FarmaciaNoDisponible"):
        err = obtener("clinicasegura.dominio.errores", nombre)
        assert issubclass(err, base), (
            f"{nombre} debe heredar de ErrorDominio para que el borde pueda "
            f"distinguir un error de negocio de una falla técnica."
        )


def test_el_dominio_no_importa_infraestructura():
    culpables = []
    for p in archivos_py("dominio"):
        prohibidos = modulos_importados(p) & INFRA
        if prohibidos:
            culpables.append(f"{p.name} importa {sorted(prohibidos)}")
    assert not culpables, (
        "El dominio conoce infraestructura:\n   " + "\n   ".join(culpables)
        + "\n   La flecha de dependencia apunta hacia el núcleo, nunca al revés."
    )


def test_el_dominio_no_lee_el_reloj_del_sistema():
    culpables = []
    for p in archivos_py("dominio"):
        for nodo in ast.walk(arbol(p)):
            if isinstance(nodo, ast.Call) and isinstance(nodo.func,
                                                         ast.Attribute):
                if nodo.func.attr in ("now", "today", "utcnow"):
                    culpables.append(f"{p.name}:{nodo.lineno}")
    assert not culpables, (
        "El dominio llama al reloj del sistema en: " + ", ".join(culpables)
        + "\n   El tiempo entra por un puerto; si no, la vigencia no se "
          "puede probar sin esperar."
    )


def test_ningun_modulo_nuevo_reproduce_el_monolito():
    """Cohesión: ninguna clase del rediseño concentra medio sistema."""
    gordas = []
    for p in archivos_py():
        for nodo in ast.walk(arbol(p)):
            if isinstance(nodo, ast.ClassDef):
                publicos = [n for n in nodo.body
                            if isinstance(n, (ast.FunctionDef,
                                              ast.AsyncFunctionDef))
                            and not n.name.startswith("_")]
                if len(publicos) > 5:
                    gordas.append(f"{p.name}:{nodo.name} "
                                  f"({len(publicos)} métodos públicos)")
    assert not gordas, (
        "Estas clases siguen haciendo demasiado: " + ", ".join(gordas)
        + "\n   Si necesita la palabra «y» para describir la clase, "
          "son dos clases."
    )


def test_el_legado_sigue_existiendo_pero_ya_nadie_lo_usa():
    from pruebas.apoyo import PAQUETE
    assert (PAQUETE / "legado.py").exists(), (
        "No borre legado.py: es la evidencia del «antes» que pide la rúbrica."
    )
    usuarios = [p.name for p in archivos_py() if "legado" in codigo(p)]
    assert not usuarios, (
        "Estos módulos todavía importan el legado: " + ", ".join(usuarios)
    )
