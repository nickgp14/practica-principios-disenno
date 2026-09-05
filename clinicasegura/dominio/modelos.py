"""Tipos del dominio de ClínicaSegura.

Estos tipos no conocen red, base de datos ni reloj: son solo datos y las
invariantes que los hacen válidos. Son inmutables (frozen) porque un valor
del dominio que se puede mutar desde fuera no tiene garantías que valgan.
"""
from dataclasses import dataclass
from decimal import Decimal


@dataclass(frozen=True)
class Cedula:
    valor: str


@dataclass(frozen=True)
class Receta:
    cedula: Cedula
    medicamento: str
    dias: int
    dosis_mg: Decimal
    riesgo_alto: bool = False


@dataclass(frozen=True)
class Despacho:
    folio: str
    cadena: str
    vence: str 
    recargo: Decimal = Decimal("0")