"""Registro de pasarelas de farmacias.

Convierte una lista de pasarelas en un diccionario buscable por el
nombre de cadena de cada una. Agregar una cadena nueva es agregar una
pasarela a la lista que se le pasa a construir_registro(); el servicio
nunca necesita saber cuántas ni cuáles cadenas existen.
"""


def construir_registro(pasarelas):
    """Recibe una lista de pasarelas y devuelve un dict {cadena: pasarela}."""
    return {p.cadena: p for p in pasarelas}