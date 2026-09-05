"""Borde de la aplicación: la frontera de confianza.

Todo lo que entra desde afuera (formulario web, HTTP) llega aquí como
datos crudos y no confiables. SolicitudReceta los parsea: o el dato
entra como un tipo válido, o no entra en absoluto. Nunca se valida con
assert, porque un assert desaparece con python -O y deja el borde
abierto justo en producción.
"""
import re
from decimal import Decimal, InvalidOperation

from pydantic import BaseModel, ConfigDict, field_validator

from clinicasegura.dominio.errores import RecetaInvalida
from clinicasegura.dominio.modelos import Cedula, Receta

PATRON_CEDULA = re.compile(r"^\d-\d{4}-\d{4}$")


class SolicitudReceta(BaseModel):
    """Los datos crudos tal como llegan del formulario web, ya validados
    y con el estado inválido hecho irrepresentable."""

    model_config = ConfigDict(extra="forbid", frozen=True)

    cedula: str
    medicamento: str
    dias: int
    dosis_mg: str

    @field_validator("cedula")
    @classmethod
    def _cedula_con_formato_valido(cls, v: str) -> str:
        if not PATRON_CEDULA.match(v):
            raise ValueError("la cédula debe tener el formato 0-0000-0000")
        return v

    @field_validator("dias")
    @classmethod
    def _dias_dentro_del_rango_permitido(cls, v: int) -> int:
        if v <= 0:
            raise ValueError("los días deben ser mayores que cero")
        if v > 90:
            raise ValueError("la vigencia máxima permitida es de 90 días")
        return v

    @field_validator("dosis_mg")
    @classmethod
    def _dosis_positiva(cls, v: str) -> str:
        try:
            valor = Decimal(v)
        except InvalidOperation:
            raise ValueError("la dosis debe ser un número válido")
        if valor <= 0:
            raise ValueError("la dosis debe ser positiva")
        return v


def a_receta(solicitud: SolicitudReceta) -> Receta:
    """Convierte una solicitud ya validada en un tipo real del dominio."""
    try:
        return Receta(
            cedula=Cedula(solicitud.cedula),
            medicamento=solicitud.medicamento,
            dias=solicitud.dias,
            dosis_mg=Decimal(solicitud.dosis_mg),
        )
    except (ValueError, InvalidOperation) as e:
        raise RecetaInvalida(str(e)) from e