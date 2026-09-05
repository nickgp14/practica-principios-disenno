"""Punto de arranque: arma el servicio con sus dependencias reales.

La configuración entra por el entorno (variables de entorno), no por
valores incrustados en el código.
"""
import os
from datetime import datetime

from clinicasegura.dominio.servicio import EmisionDeRecetas
from clinicasegura.infraestructura.folios import GeneradorFolioUUID
from clinicasegura.infraestructura.registro import construir_registro


class RelojDelSistema:
    """Implementación real del puerto Reloj: usa la hora del sistema."""

    def ahora(self) -> datetime:
        return datetime.now()


class BitacoraEnConsola:
    """Implementación mínima del puerto Bitacora, mientras no hay una
    implementación con base de datos real."""

    def registrar(self, evento: str, folio: str) -> None:
        print(f"[bitacora] {evento} folio={folio}")


def construir_servicio() -> EmisionDeRecetas:
    """Arma el caso de uso con sus dependencias reales, leyendo
    configuración del entorno con valores por defecto razonables."""
    timeout_ms = int(os.environ.get("FARMACIA_TIMEOUT_MS", "1500"))

    # Por ahora no hay pasarelas reales conectadas (eso depende de tener
    # URLs y credenciales reales de cada farmacia). El registro arranca
    # vacío; se van agregando pasarelas conforme existan.
    registro = construir_registro([])

    return EmisionDeRecetas(
        pasarelas=registro,
        reloj=RelojDelSistema(),
        folios=GeneradorFolioUUID(),
        bitacora=BitacoraEnConsola(),
    )