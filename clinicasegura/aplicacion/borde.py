"""Borde de la aplicación: traduce datos externos al idioma del dominio.

La validación de formato usa expresiones regulares de la biblioteca
estándar, en vez de recorrer la cédula carácter por carácter a mano
como hacía el legado.
"""
import re

PATRON_CEDULA = re.compile(r"^\d-\d{4}-\d{4}$")


def validar_cedula(valor: str) -> bool:
    return bool(PATRON_CEDULA.match(valor))