"""Caso de uso: emitir una receta electrónica.

Por ahora recibe una Receta del dominio en vez de un diccionario crudo.
La inyección de pasarelas, reloj, folios y bitácora llega en la Etapa 5.
"""
from clinicasegura.dominio.modelos import Receta


class EmisionDeRecetas:
    def emitir(self, receta: Receta, cadena: str):
        ...