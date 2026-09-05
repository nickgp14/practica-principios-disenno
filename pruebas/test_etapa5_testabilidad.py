"""ETAPA 5 · Testabilidad.

Principio 10 (diseñar para la testabilidad).

CONCEPTO — las dos mitades
  Controlabilidad: puedo poner el sistema en el estado que quiero probar.
                   Entradas, reloj, azar y dependencias entran DESDE AFUERA.
  Observabilidad:  puedo ver qué pasó sin depurador. Valor de retorno,
                   evento registrado o estado consultable.
  Los cuatro enemigos: estado global, dependencias construidas adentro,
  fuentes no deterministas incrustadas y decisión mezclada con efecto.

EXPERIMENTO (anote la salida en BITACORA.md)
  Antes de rediseñar, intente esto en la terminal:
    >>> from clinicasegura.legado import ServicioRecetas
    >>> s = ServicioRecetas()
    >>> s.emitir({"cedula": "1-1234-5678", "dias": 30, "dosis_mg": 500}, "farmauno")
  Prediga primero qué va a pasar. Luego cuente cuántas cosas del mundo real
  necesitó tocar para llegar a una sola línea de regla de negocio.

QUÉ DEBE HACER USTED
  EmisionDeRecetas recibe por constructor, con estos nombres exactos:
      pasarelas, reloj, folios, bitacora
  Nada más. Y la fecha de vencimiento sale del reloj inyectado.
"""
import inspect
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from pruebas.apoyo import PAQUETE, codigo, importar, obtener, parametros

pytestmark = pytest.mark.etapa5

FIJO = datetime(2026, 3, 1, 9, 0, 0)


class RelojFijo:
    def __init__(self, cuando=FIJO):
        self.cuando = cuando

    def ahora(self) -> datetime:
        return self.cuando


class FoliosSecuenciales:
    def __init__(self):
        self.n = 0

    def siguiente(self) -> str:
        self.n += 1
        return f"F-{self.n:05d}"


class FarmaciaFalsa:
    """Un FALSO, no un simulador: implementación real, en memoria."""
    cadena = "farmauno"

    def __init__(self):
        self.recibidas = []

    def enviar(self, receta, folio, vence):
        modelos = importar("clinicasegura.dominio.modelos")
        self.recibidas.append((receta, folio, vence))
        return modelos.Despacho(folio=folio, cadena=self.cadena, vence=vence)


class BitacoraEspia:
    def __init__(self):
        self.eventos = []

    def registrar(self, evento: str, folio: str) -> None:
        self.eventos.append((evento, folio))


def _armar(reloj=None):
    EmisionDeRecetas = obtener("clinicasegura.dominio.servicio",
                               "EmisionDeRecetas")
    farmacia, bitacora = FarmaciaFalsa(), BitacoraEspia()
    servicio = EmisionDeRecetas(
        pasarelas={farmacia.cadena: farmacia},
        reloj=reloj or RelojFijo(),
        folios=FoliosSecuenciales(),
        bitacora=bitacora,
    )
    return servicio, farmacia, bitacora


def _receta():
    m = importar("clinicasegura.dominio.modelos")
    return m.Receta(cedula=m.Cedula("1-1234-5678"), medicamento="N02BE01",
                    dias=30, dosis_mg=Decimal("500"))


def test_todo_lo_no_determinista_entra_por_constructor():
    EmisionDeRecetas = obtener("clinicasegura.dominio.servicio",
                               "EmisionDeRecetas")
    params = set(parametros(EmisionDeRecetas.__init__))
    esperados = {"pasarelas", "reloj", "folios", "bitacora"}
    assert params == esperados, (
        f"El constructor recibe {sorted(params)} y se esperan "
        f"{sorted(esperados)}.\n"
        f"   La firma del constructor es la documentación honesta de las "
        f"dependencias del servicio: lo que no aparece ahí, no se puede "
        f"controlar desde una prueba."
    )


def test_la_vigencia_es_determinista_porque_el_reloj_se_inyecta():
    servicio, farmacia, _ = _armar(RelojFijo())
    d1 = servicio.emitir(_receta(), "farmauno")
    d2 = servicio.emitir(_receta(), "farmauno")
    assert d1.vence == d2.vence, (
        "Dos emisiones con el mismo reloj deben vencer el mismo día. "
        "Si no, alguien sigue llamando a datetime.now()."
    )
    esperado = (FIJO + timedelta(days=30)).date()
    real = d1.vence.date() if isinstance(d1.vence, datetime) else d1.vence
    assert real == esperado, (
        f"La vigencia debe ser de 30 días desde el reloj inyectado. "
        f"Se esperaba {esperado} y llegó {real}."
    )


def test_el_folio_es_predecible_porque_el_azar_se_inyecta():
    servicio, _, _ = _armar()
    assert servicio.emitir(_receta(), "farmauno").folio == "F-00001"
    assert servicio.emitir(_receta(), "farmauno").folio == "F-00002"


def test_la_prueba_corre_sin_red_y_el_doble_lo_demuestra():
    servicio, farmacia, _ = _armar()
    servicio.emitir(_receta(), "farmauno")
    assert len(farmacia.recibidas) == 1, (
        "El servicio no usó la pasarela inyectada. ¿Sigue construyendo la "
        "conexión adentro?"
    )
    receta, folio, vence = farmacia.recibidas[0]
    assert not isinstance(receta, dict), (
        "Al adaptador le llegó un diccionario. Debe llegarle una Receta."
    )


def test_lo_que_ocurrio_se_puede_observar_sin_depurador():
    servicio, _, bitacora = _armar()
    despacho = servicio.emitir(_receta(), "farmauno")
    assert bitacora.eventos, (
        "Nadie registró el evento. La Ley 8968 exige trazabilidad del "
        "acceso al expediente: la bitácora es un puerto de primera clase, "
        "y además es su observabilidad."
    )
    assert any(despacho.folio in str(e) for e in bitacora.eventos), (
        f"El evento registrado no menciona el folio {despacho.folio}."
    )


def test_el_servicio_no_construye_sus_propias_dependencias():
    fuente = codigo(PAQUETE / "dominio" / "servicio.py")
    for prohibido in ("requests", "urllib", "sqlite3",
                      "datetime.now", "random.", "os.environ"):
        assert prohibido not in fuente, (
            f"El servicio contiene «{prohibido}». Ninguno de los cuatro "
            f"enemigos de la testabilidad puede vivir en el caso de uso."
        )


def test_el_estudiante_escribio_al_menos_tres_pruebas_propias():
    """No basta con pasar las nuestras: escribir la prueba es la práctica."""
    from pruebas.apoyo import RAIZ
    mias = list((RAIZ / "mis_pruebas").glob("test_*.py")) if (
        RAIZ / "mis_pruebas").exists() else []
    if not mias:
        pytest.fail(
            "Falta la carpeta mis_pruebas/ con sus propias pruebas.\n"
            "   Escriba al menos tres que antes eran imposibles:\n"
            "     1) la vigencia con un reloj fijo,\n"
            "     2) la cadena caída (la pasarela lanza TimeoutError),\n"
            "     3) una receta inválida rechazada en el borde."
        )
    total = 0
    for p in mias:
        total += p.read_text(encoding="utf-8").count("def test_")
    assert total >= 3, (
        f"Encontré {total} pruebas suyas en mis_pruebas/. Se piden al menos 3."
    )
