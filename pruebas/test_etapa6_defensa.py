"""ETAPA 6 · Diseño defensivo.

Principio 11 (diseñar defensivamente, sin caer en código paranoico).

CONCEPTO — la frontera de confianza
  AFUERA (formulario, HTTP, archivo, cola): no confiable. Aquí se PARSEA:
  el dato entra como un tipo válido o no entra. Si falla: excepción de
  dominio y respuesta 400. Nunca se desactiva.
  ADENTRO (su propio código): confiable. Aquí se AFIRMA. Si una aserción
  falla no es un dato malo, es un defecto de programación. Se apaga con -O.

  Verificar lo mismo en las dos zonas es código paranoico: el lector deja
  de distinguir cuál comprobación es esencial.

EXPERIMENTO OBLIGATORIO (pegue la salida en BITACORA.md)
  $ python  -c "from clinicasegura.legado import ServicioRecetas as S; \\
      S().emitir({'cedula':'x','dias':0,'dosis_mg':1}, 'farmauno')"
  $ python -O -c "from clinicasegura.legado import ServicioRecetas as S; \\
      S().emitir({'cedula':'x','dias':0,'dosis_mg':1}, 'farmauno')"
  Prediga antes qué cambia entre las dos corridas. La segunda es
  exactamente lo que ocurre en producción.

QUÉ DEBE HACER USTED
  aplicacion/borde.py:
      SolicitudReceta  (pydantic, extra="forbid", frozen=True)
      a_receta(solicitud) -> Receta
  El caso de uso recibe Receta, nunca un diccionario. Si la farmacia falla,
  se propaga FarmaciaNoDisponible con contexto: la receta es crítica y no
  admite degradación silenciosa.
"""
import ast
from datetime import datetime
from decimal import Decimal

import pytest

from pruebas.apoyo import arbol, archivos_py, importar, obtener

pytestmark = pytest.mark.etapa6

VALIDA = {"cedula": "1-1234-5678", "medicamento": "N02BE01",
          "dias": 30, "dosis_mg": "500"}


def _solicitud(**cambios):
    SolicitudReceta = obtener("clinicasegura.aplicacion.borde",
                              "SolicitudReceta")
    datos = dict(VALIDA)
    datos.update(cambios)
    return SolicitudReceta(**datos)


# ------------------------------------------------------------ el borde
def test_el_borde_acepta_lo_valido_y_lo_convierte_en_un_tipo_del_dominio():
    receta = obtener("clinicasegura.aplicacion.borde", "a_receta")(_solicitud())
    modelos = importar("clinicasegura.dominio.modelos")
    assert isinstance(receta, modelos.Receta)
    assert isinstance(receta.cedula, modelos.Cedula), (
        "a_receta debe devolver tipos del dominio, no cadenas sueltas. "
        "Parsear, no validar: aguas abajo el estado inválido ya no existe."
    )
    assert isinstance(receta.dosis_mg, Decimal)


@pytest.mark.parametrize("cambio,por_que", [
    ({"dias": 0}, "los días deben ser mayores que cero"),
    ({"dias": 400}, "la vigencia máxima son 90 días"),
    ({"dosis_mg": "-5"}, "la dosis debe ser positiva"),
    ({"cedula": "abc"}, "la cédula tiene formato 0-0000-0000"),
])
def test_el_borde_rechaza_lo_invalido(cambio, por_que):
    with pytest.raises(Exception) as e:
        _solicitud(**cambio)
    assert e.type.__name__ != "AssertionError", (
        f"Se rechazó con assert ({por_que}). Un assert desaparece con "
        f"python -O y deja el borde abierto justo en producción."
    )


def test_el_borde_rechaza_campos_desconocidos():
    with pytest.raises(Exception):
        _solicitud(**{"es_vip": True})
    # el mensaje del fallo importa tanto como el fallo
    SolicitudReceta = obtener("clinicasegura.aplicacion.borde",
                              "SolicitudReceta")
    config = getattr(SolicitudReceta, "model_config", {})
    assert config.get("extra") == "forbid", (
        "SolicitudReceta debe declarar extra=\"forbid\". Aceptar campos "
        "desconocidos es la puerta de la contaminación de parámetros."
    )
    assert config.get("frozen") is True, (
        "SolicitudReceta debe ser frozen: lo que entró validado no se "
        "vuelve a mutar aguas abajo."
    )


def test_no_se_usan_aserciones_sobre_datos_externos():
    culpables = []
    for p in archivos_py("aplicacion"):
        for nodo in ast.walk(arbol(p)):
            if isinstance(nodo, ast.Assert):
                culpables.append(f"{p.name}:{nodo.lineno}")
    assert not culpables, (
        "Hay assert en el borde: " + ", ".join(culpables)
        + "\n   La aserción protege supuestos internos; el dato no "
          "confiable se rechaza con una excepción que nunca se apaga."
    )


# ------------------------------------------------------- política de fallo
def test_si_la_farmacia_falla_se_propaga_un_error_de_dominio_con_contexto():
    EmisionDeRecetas = obtener("clinicasegura.dominio.servicio",
                               "EmisionDeRecetas")
    FarmaciaNoDisponible = obtener("clinicasegura.dominio.errores",
                                   "FarmaciaNoDisponible")

    class PasarelaCaida:
        cadena = "farmauno"

        def enviar(self, receta, folio, vence):
            raise TimeoutError("la cadena no respondió")

    class RelojFijo:
        def ahora(self): return datetime(2026, 3, 1)

    class Folios:
        def siguiente(self): return "F-00001"

    class Bitacora:
        def __init__(self): self.eventos = []
        def registrar(self, evento, folio): self.eventos.append((evento, folio))

    modelos = importar("clinicasegura.dominio.modelos")
    receta = modelos.Receta(cedula=modelos.Cedula("1-1234-5678"),
                            medicamento="N02BE01", dias=30,
                            dosis_mg=Decimal("500"))
    bitacora = Bitacora()
    servicio = EmisionDeRecetas(pasarelas={"farmauno": PasarelaCaida()},
                                reloj=RelojFijo(), folios=Folios(),
                                bitacora=bitacora)
    with pytest.raises(FarmaciaNoDisponible) as e:
        servicio.emitir(receta, "farmauno")
    assert "farmauno" in str(e.value) or "F-00001" in str(e.value), (
        "El error de dominio debe llevar contexto (cadena o folio). Un "
        "error sin contexto obliga a reproducir el problema para entenderlo."
    )
    assert bitacora.eventos, (
        "La falla no quedó registrada. Fallar rápido no significa fallar "
        "en silencio: se propaga Y se deja rastro."
    )


def test_nunca_se_devuelve_none_para_señalar_un_error():
    for p in archivos_py("dominio"):
        arbol_p = arbol(p)
        for nodo in ast.walk(arbol_p):
            if not isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                continue
            if nodo.name.startswith("_"):
                continue
            for hijo in ast.walk(nodo):
                if isinstance(hijo, ast.Return) and isinstance(
                        hijo.value, ast.Constant) and hijo.value.value is None:
                    pytest.fail(
                        f"{p.name}:{hijo.lineno} devuelve None desde "
                        f"{nodo.name}(). Devolver None o menos uno hace que "
                        f"el error viaje callado hasta el reporte gerencial."
                    )


def test_no_hay_except_vacio_en_ningun_lado():
    culpables = []
    for p in archivos_py():
        for nodo in ast.walk(arbol(p)):
            if isinstance(nodo, ast.ExceptHandler):
                cuerpo = nodo.body
                if len(cuerpo) == 1 and isinstance(cuerpo[0], ast.Pass):
                    culpables.append(f"{p.name}:{nodo.lineno}")
                if nodo.type is None:
                    culpables.append(f"{p.name}:{nodo.lineno} (except desnudo)")
    assert not culpables, (
        "except vacío o desnudo en: " + ", ".join(culpables)
        + "\n   Es la única política prohibida del curso. Silenciar la "
          "excepción no es tolerancia a fallos: es ceguera."
    )


def test_no_hay_reintentos_sin_limite():
    culpables = []
    for p in archivos_py():
        for nodo in ast.walk(arbol(p)):
            if isinstance(nodo, ast.While) and isinstance(
                    nodo.test, ast.Constant) and nodo.test.value is True:
                culpables.append(f"{p.name}:{nodo.lineno}")
    assert not culpables, (
        "while True en: " + ", ".join(culpables)
        + "\n   Un reintento sin límite ni espera creciente agota recursos. "
          "Si reintenta, acote los intentos y verifique que la operación "
          "sea idempotente."
    )
