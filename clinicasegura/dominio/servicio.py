"""Caso de uso: emitir una receta electrónica.

El servicio recibe sus dependencias por constructor (pasarelas, reloj,
folios, bitacora) en vez de construirlas adentro. Esto es lo que permite
agregar una cadena nueva sin tocar este archivo: basta con agregar una
pasarela más al registro que se le pasa desde afuera.
"""
from clinicasegura.dominio.errores import CadenaNoSoportada
from clinicasegura.dominio.modelos import Despacho, Receta
from clinicasegura.dominio.reglas import calcular_recargo


class EmisionDeRecetas:
    def __init__(self, pasarelas, reloj, folios, bitacora):
        self.pasarelas = pasarelas
        self.reloj = reloj
        self.folios = folios
        self.bitacora = bitacora

    def emitir(self, receta: Receta, cadena: str) -> Despacho:
        pasarela = self.pasarelas.get(cadena)
        if pasarela is None:
            raise CadenaNoSoportada(
                f"No hay pasarela registrada para la cadena «{cadena}»."
            )

        folio = self.folios.siguiente()
        vence = self.reloj.ahora()

        despacho = pasarela.enviar(receta, folio=folio, vence=vence)

        self.bitacora.registrar(evento="emitida", folio=folio)

        return despacho