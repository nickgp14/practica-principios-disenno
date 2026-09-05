"""Puertos del dominio de ClínicaSegura.

Un puerto es una interfaz que el DOMINIO define según lo que necesita,
no según lo que el proveedor externo ofrece. Por eso los métodos se
llaman "enviar" y no "post": si mañana cambia el mecanismo (HTTP, SOAP,
colas de mensajes), el nombre del puerto sigue siendo verdadero.

Se usan typing.Protocol en vez de clases abstractas (ABC) porque un
Protocol define el puerto por su FORMA (qué métodos tiene), sin obligar
a la infraestructura a heredar del dominio. La dependencia queda
invertida de verdad: el dominio no conoce ninguna clase concreta de
infraestructura.
"""
from typing import Protocol

from clinicasegura.dominio.modelos import Despacho, Receta


class Pasarela(Protocol):
    """Envía una receta a una cadena de farmacias."""

    def enviar(self, receta: Receta) -> Despacho:
        ...


class Reloj(Protocol):
    """Da la hora actual. Se inyecta para poder fijarla en las pruebas."""

    def ahora(self):
        ...


class GeneradorFolio(Protocol):
    """Genera folios únicos. Se inyecta para poder predecirlos en pruebas."""

    def siguiente(self) -> str:
        ...


class Bitacora(Protocol):
    """Registra eventos de auditoría (exigido por la Ley 8968)."""

    def registrar(self, folio: str, evento: str) -> None:
        ...