"""Errores propios del dominio de ClínicaSegura.

Todo error de negocio hereda de ErrorDominio, para que el borde de la
aplicación pueda distinguir una falla de negocio (dato inválido, cadena
no soportada) de una falla técnica (red caída, bug de programación).
"""


class ErrorDominio(Exception):
    """Raíz de todos los errores de negocio de ClínicaSegura."""


class RecetaInvalida(ErrorDominio):
    """La receta no cumple las reglas del negocio (dosis, días, etc.)."""


class CadenaNoSoportada(ErrorDominio):
    """Se pidió despachar a una cadena de farmacias que no existe."""


class FarmaciaNoDisponible(ErrorDominio):
    """La farmacia respondió con error o no respondió a tiempo."""