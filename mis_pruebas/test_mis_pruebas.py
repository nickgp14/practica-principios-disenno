"""Pruebas propias — cosas que con el legado eran imposibles de probar.

1) La vigencia con un reloj fijo.
2) La cadena caída (la pasarela lanza TimeoutError).
3) Una receta inválida rechazada en el borde.
"""
from datetime import datetime, timedelta
from decimal import Decimal

import pytest

from clinicasegura.dominio.errores import RecetaInvalida
from clinicasegura.dominio.modelos import Cedula, Receta
from clinicasegura.dominio.servicio import EmisionDeRecetas


FIJO = datetime(2026, 6, 15, 10, 0, 0)


class RelojFijo:
    def ahora(self):
        return FIJO


class FoliosSecuenciales:
    def __init__(self):
        self.n = 0

    def siguiente(self):
        self.n += 1
        return f"F-{self.n:05d}"


class BitacoraEspia:
    def __init__(self):
        self.eventos = []

    def registrar(self, evento, folio):
        self.eventos.append((evento, folio))


class PasarelaQueFunciona:
    cadena = "farmauno"

    def enviar(self, receta, folio, vence):
        from clinicasegura.dominio.modelos import Despacho
        return Despacho(folio=folio, cadena=self.cadena, vence=vence)


class PasarelaCaida:
    """Simula que la farmacia no responde a tiempo."""
    cadena = "farmauno"

    def enviar(self, receta, folio, vence):
        raise TimeoutError("La farmacia no respondió a tiempo.")


def _receta():
    return Receta(
        cedula=Cedula("1-1234-5678"),
        medicamento="N02BE01",
        dias=30,
        dosis_mg=Decimal("500"),
    )


def test_la_vigencia_usa_el_reloj_fijo_que_yo_inyecto():
    """Con el legado esto era imposible: datetime.now() estaba incrustado
    dentro de emitir() y no había forma de controlar la fecha."""
    servicio = EmisionDeRecetas(
        pasarelas={"farmauno": PasarelaQueFunciona()},
        reloj=RelojFijo(),
        folios=FoliosSecuenciales(),
        bitacora=BitacoraEspia(),
    )
    despacho = servicio.emitir(_receta(), "farmauno")
    esperado = FIJO + timedelta(days=30)
    assert despacho.vence == esperado


def test_la_cadena_caida_propaga_el_error_en_vez_de_fallar_en_silencio():
    """Con el legado, un except Exception: pass se tragaba el error sin
    dejar rastro. Aquí, si la pasarela falla, el error debe propagarse."""
    servicio = EmisionDeRecetas(
        pasarelas={"farmauno": PasarelaCaida()},
        reloj=RelojFijo(),
        folios=FoliosSecuenciales(),
        bitacora=BitacoraEspia(),
    )
    with pytest.raises(TimeoutError):
        servicio.emitir(_receta(), "farmauno")


def test_una_receta_con_dias_negativos_es_invalida():
    """Con el legado, el assert de validación desaparecía si se corría
    con python -O. Aquí la validación no puede desaparecer nunca."""
    with pytest.raises((RecetaInvalida, ValueError)):
        Receta(
            cedula=Cedula("1-1234-5678"),
            medicamento="N02BE01",
            dias=-5,
            dosis_mg=Decimal("500"),
        )