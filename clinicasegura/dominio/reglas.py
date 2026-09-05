"""Reglas de negocio puras de ClínicaSegura.

Una función pura: mismas entradas, mismo resultado, sin efectos de lado
(no imprime, no lee el reloj, no lee estado global, no toca disco).
"""
from decimal import Decimal


def calcular_recargo(
    dias_restantes: int,
    tarifa_diaria: Decimal,
    recargo_por_riesgo: bool,
) -> Decimal:
    """Calcula el recargo de una receta.

    Si aplica riesgo alto, el recargo se duplica (mismo comportamiento
    que el legado, donde riesgo_alto multiplicaba por 2).
    """
    base = tarifa_diaria * dias_restantes
    if recargo_por_riesgo:
        return base * 2
    return base