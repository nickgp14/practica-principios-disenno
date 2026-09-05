"""ETAPA 2 · Reducir el acoplamiento.

Principio 3 (reducir el acoplamiento donde sea posible).

CONCEPTO — los tipos de acoplamiento, de peor a mejor
  Contenido : un módulo toca las tripas de otro.
  Común     : dos módulos comparten una variable global mutable. Es lo que
              hace CONFIG en el legado: nadie sabe quién la cambió.
  Control   : el llamador pasa una bandera que decide qué rama ejecuta el
              llamado ("farmauno", riesgo_alto=True).
  Estampado : recibe un objeto completo para usar dos campos.
  Datos     : recibe exactamente los valores que usa.  ← la meta

EXPERIMENTO (hágalo antes de programar, y anote la salida en BITACORA.md)
  >>> from clinicasegura.legado import CONFIG, ServicioRecetas
  >>> CONFIG["vigencia_dias"] = 1
  Ahora TODA receta del proceso vence mañana, y ningún método lo declaró.
  Prediga primero: ¿cuántos lugares del archivo cambian de comportamiento
  con esa sola línea? Cuéntelos después leyendo el código.

QUÉ DEBE HACER USTED
  1. Eliminar el estado global mutable. La configuración se pasa como
     argumento o se construye una sola vez en el arranque.
  2. Convertir la regla de negocio en una función pura de firma estrecha:
        dominio/reglas.py
          calcular_recargo(dias_restantes, tarifa_diaria, recargo_por_riesgo)
     Tres valores simples. Ni Receta, ni Paciente, ni diccionarios.
  3. Que el caso de uso reciba objetos del dominio, no diccionarios crudos.
"""
import ast
import inspect
from decimal import Decimal

import pytest

from pruebas.apoyo import (arbol, archivos_py, codigo_de, obtener,
                           parametros)

pytestmark = pytest.mark.etapa2

SIMPLES = {"int", "float", "bool", "str", "Decimal", "date", "datetime"}


def test_no_queda_estado_global_mutable():
    culpables = []
    for p in archivos_py():
        for nodo in arbol(p).body:                 # solo nivel de módulo
            if not isinstance(nodo, (ast.Assign, ast.AnnAssign)):
                continue
            valor = nodo.value
            if isinstance(valor, (ast.Dict, ast.List, ast.Set)):
                objetivos = (nodo.targets if isinstance(nodo, ast.Assign)
                             else [nodo.target])
                for t in objetivos:
                    if isinstance(t, ast.Name):
                        culpables.append(f"{p.name}:{nodo.lineno} {t.id}")
    assert not culpables, (
        "Quedan contenedores mutables a nivel de módulo:\n   "
        + "\n   ".join(culpables)
        + "\n   Eso es acoplamiento común: dos módulos que se comunican por "
          "una variable que nadie declara en su firma.\n"
          "   Si necesita una constante, use una tupla, un frozenset o "
          "types.MappingProxyType."
    )


def test_la_regla_de_negocio_es_una_funcion_pura_de_firma_estrecha():
    calcular = obtener("clinicasegura.dominio.reglas", "calcular_recargo")
    params = parametros(calcular)
    assert len(params) == 3, (
        f"calcular_recargo recibe {params}. Se esperan exactamente tres "
        f"valores simples: días restantes, tarifa diaria y si aplica "
        f"recargo por riesgo.\n"
        f"   Recibir la Receta o el Paciente completos es acoplamiento de "
        f"estampado: arrastra medio dominio a quien quiera reusar la función."
    )
    for nombre, p in inspect.signature(calcular).parameters.items():
        anot = p.annotation
        texto = getattr(anot, "__name__", str(anot))
        assert any(s in texto for s in SIMPLES), (
            f"El parámetro «{nombre}» está anotado como {texto}. Los tres "
            f"parámetros deben ser tipos simples."
        )


def test_la_regla_de_negocio_no_tiene_efectos_ni_depende_del_entorno():
    calcular = obtener("clinicasegura.dominio.reglas", "calcular_recargo")
    a = calcular(10, Decimal("250"), False)
    b = calcular(10, Decimal("250"), False)
    assert a == b, "La función debe ser pura: mismas entradas, mismo resultado."
    assert calcular(10, Decimal("250"), True) == a * 2, (
        "El recargo por riesgo duplica el monto, igual que en el legado. "
        "No cambie el comportamiento observable."
    )
    assert calcular(0, Decimal("250"), False) == Decimal("0")

    fuente = inspect.getsource(calcular)
    for prohibido in ("print(", "open(", "now(", "random", "CONFIG"):
        assert prohibido not in fuente, (
            f"calcular_recargo usa «{prohibido}». Una función pura no "
            f"imprime, no lee el reloj, no lee estado global y no toca disco."
        )


def test_el_caso_de_uso_no_recibe_diccionarios_crudos():
    servicio = obtener("clinicasegura.dominio.servicio", "EmisionDeRecetas")
    firma = inspect.signature(servicio.emitir)
    anotaciones = [str(p.annotation) for n, p in firma.parameters.items()
                   if n != "self"]
    assert not any("dict" in a.lower() for a in anotaciones), (
        f"emitir() todavía recibe un diccionario: {anotaciones}.\n"
        f"   Un dict no tiene contrato: el llamador adivina las llaves y el "
        f"error aparece en producción, no en el editor."
    )
    assert any("Receta" in a for a in anotaciones), (
        f"emitir() debe recibir una Receta del dominio. Firma actual: "
        f"{anotaciones}"
    )


def test_el_registro_de_bitacora_entra_por_un_puerto_y_no_por_sqlite():
    """Acoplamiento de contenido: el caso de uso no abre conexiones."""
    fuente = codigo_de("dominio")
    for prohibido in ("sqlite3", "connect(", "INSERT INTO", "commit()"):
        assert prohibido not in fuente, (
            f"El dominio contiene «{prohibido}». La bitácora es un puerto "
            f"(la Ley 8968 la exige, así que es de primera clase), pero su "
            f"implementación vive en infraestructura."
        )
