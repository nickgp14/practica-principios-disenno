"""ETAPA 0 · Diagnóstico  —  observar antes de tocar.

Principios en juego: los once, en modo lectura.

Qué debe hacer usted:
  Abra clinicasegura/legado.py, léalo entero y llene DIAGNOSTICO.md
  (hay una plantilla en la raíz del proyecto) con una fila por principio:
  el número, el nombre y el hallazgo concreto — archivo y línea — que lo
  viola. Si cree que un principio NO está violado, escríbalo igual y
  justifique por qué.

Por qué esta etapa existe:
  Diseñar no empieza escribiendo: empieza nombrando lo que está mal. Un
  informe que dice «el código está acoplado» no vale nada; uno que dice
  «legado.py:38 CONFIG es un diccionario global mutable que leen tres
  métodos» sí.
"""
import pytest

from pruebas.apoyo import existe_documento, filas_de_tabla

pytestmark = pytest.mark.etapa0

PRINCIPIOS = [
    "dividir", "cohesión", "acoplamiento", "abstracción", "reusabilidad",
    "reusar", "flexibilidad", "obsolescencia", "portabilidad",
    "testabilidad", "defensiv",
]


def _diagnostico() -> str:
    p = existe_documento("DIAGNOSTICO.md")
    if p is None:
        pytest.fail(
            "Falta DIAGNOSTICO.md en la raíz del proyecto.\n"
            "   Copie la plantilla de la guía y llénela antes de programar."
        )
    return p.read_text(encoding="utf-8")


def test_hay_una_fila_por_cada_uno_de_los_once_principios():
    filas = filas_de_tabla(_diagnostico())
    assert len(filas) >= 11, (
        f"La tabla de diagnóstico tiene {len(filas)} filas de datos y se "
        f"esperan 11, una por principio de Lethbridge."
    )


def test_cada_fila_nombra_un_principio_distinto():
    filas = filas_de_tabla(_diagnostico())
    texto = " ".join(" ".join(f).lower() for f in filas)
    faltan = [p for p in PRINCIPIOS if p not in texto]
    assert not faltan, (
        "En la tabla no aparecen estos principios: "
        + ", ".join(faltan)
    )


def test_cada_hallazgo_cita_archivo_y_linea():
    filas = filas_de_tabla(_diagnostico())
    sin_evidencia = [
        f[0] for f in filas
        if not any(".py" in c and any(ch.isdigit() for ch in c) for c in f)
    ]
    assert not sin_evidencia, (
        "Estas filas no citan archivo y línea (por ejemplo «legado.py:38»): "
        + ", ".join(sin_evidencia)
        + "\n   Una decisión sin evidencia vale cero, también en el diagnóstico."
    )


def test_ninguna_fila_quedo_vacia_o_con_el_texto_de_la_plantilla():
    filas = filas_de_tabla(_diagnostico())
    malas = [f[0] for f in filas
             if any(c.strip() in ("", "...", "TODO", "PENDIENTE") for c in f)]
    assert not malas, "Filas incompletas: " + ", ".join(malas)
