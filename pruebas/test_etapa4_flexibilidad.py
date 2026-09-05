"""ETAPA 4 · Flexibilidad, obsolescencia y portabilidad.

Principios 7 (diseñar para la flexibilidad), 8 (anticipar la obsolescencia)
y 9 (diseñar para la portabilidad).

CONCEPTO — dónde vive la variación
  En el legado, la variación vive en un condicional: cada cadena nueva
  obliga a abrir y modificar el orquestador. Con un puerto y un registro,
  la variación vive en un archivo nuevo y el orquestador queda cerrado a
  modificación. Eso es «abierto y cerrado» sostenido por inversión de
  dependencias.

EXPERIMENTO CLAVE (esta prueba lo hace por usted, pero entiéndalo)
  La prueba de abajo define una cuarta cadena, FarmaViva, que NO existe en
  su código, la registra desde fuera y emite una receta con ella. Si su
  diseño es correcto, funciona sin que usted toque una sola línea del
  servicio. Si tiene un if, falla. Prediga cuál de las dos cosas pasará
  antes de correrla.

QUÉ DEBE HACER USTED
  1. infraestructura/registro.py: construir_registro(pasarelas) -> dict
  2. El servicio recibe el registro y busca por clave. Cero condicionales
     por nombre de cadena.
  3. Cadena desconocida: lanza CadenaNoSoportada. Nunca devuelve None.
  4. Ni URLs ni rutas literales fuera de infraestructura; la configuración
     entra por el entorno (factor III de los doce factores).
  5. DEPENDENCIAS.md con la tabla de obsolescencia: por cada dependencia
     externa, versión acotada, licencia, riesgo y ruta de salida.
"""
import ast
import os
import re
from datetime import date, datetime
from decimal import Decimal

import pytest

from pruebas.apoyo import (PAQUETE, arbol, archivos_py, codigo,
                           existe_documento, filas_de_tabla, importar,
                           obtener)

pytestmark = pytest.mark.etapa4


# ----------------------------------------------------------------- dobles
class RelojFijo:
    def ahora(self) -> datetime:
        return datetime(2026, 3, 1, 9, 0, 0)


class FoliosSecuenciales:
    def __init__(self):
        self.n = 0

    def siguiente(self) -> str:
        self.n += 1
        return f"F-{self.n:05d}"


class BitacoraEspia:
    def __init__(self):
        self.eventos = []

    def registrar(self, evento: str, folio: str) -> None:
        self.eventos.append((evento, folio))


def _receta():
    modelos = importar("clinicasegura.dominio.modelos")
    return modelos.Receta(
        cedula=modelos.Cedula("1-1234-5678"),
        medicamento="N02BE01",
        dias=30,
        dosis_mg=Decimal("500"),
    )


def test_se_agrega_una_cadena_nueva_sin_tocar_el_servicio():
    """El corazón del principio 7. Esta cadena no existe en su código."""
    EmisionDeRecetas = obtener("clinicasegura.dominio.servicio",
                               "EmisionDeRecetas")
    modelos = importar("clinicasegura.dominio.modelos")

    enviadas = []

    class PasarelaFarmaViva:                      # definida aquí, fuera de su código
        cadena = "farmaviva"

        def enviar(self, receta, folio, vence):
            enviadas.append((receta, folio, vence))
            return modelos.Despacho(folio=folio, cadena=self.cadena,
                                    vence=vence)

    construir = obtener("clinicasegura.infraestructura.registro",
                        "construir_registro")
    registro = construir([PasarelaFarmaViva()])

    servicio = EmisionDeRecetas(
        pasarelas=registro, reloj=RelojFijo(),
        folios=FoliosSecuenciales(), bitacora=BitacoraEspia(),
    )
    despacho = servicio.emitir(_receta(), "farmaviva")

    assert len(enviadas) == 1, (
        "La cadena nueva nunca recibió la receta. Revise que el servicio "
        "busque en el registro y no ramifique por nombre."
    )
    assert despacho.cadena == "farmaviva"


def test_una_cadena_desconocida_lanza_un_error_de_dominio():
    EmisionDeRecetas = obtener("clinicasegura.dominio.servicio",
                               "EmisionDeRecetas")
    CadenaNoSoportada = obtener("clinicasegura.dominio.errores",
                                "CadenaNoSoportada")
    servicio = EmisionDeRecetas(pasarelas={}, reloj=RelojFijo(),
                                folios=FoliosSecuenciales(),
                                bitacora=BitacoraEspia())
    with pytest.raises(CadenaNoSoportada):
        servicio.emitir(_receta(), "no-existe")


def test_el_servicio_no_ramifica_por_nombre_de_cadena():
    fuente = codigo(PAQUETE / "dominio" / "servicio.py")
    for nombre in ("farmauno", "saludtotal", "cruzverde", "farmaviva"):
        assert nombre not in fuente.lower(), (
            f"El servicio menciona «{nombre}». Si el orquestador conoce los "
            f"nombres de las cadenas, no está cerrado a modificación."
        )


def test_no_quedan_urls_ni_rutas_literales_fuera_de_infraestructura():
    culpables = []
    for p in archivos_py():
        if "infraestructura" in str(p) or "arranque" in p.name:
            continue
        texto = codigo(p)
        for patron, que in ((r"https?://", "una URL"),
                            (r"[A-Za-z]:\\\\", "una ruta de Windows"),
                            (r"[\"']/tmp/", "una ruta absoluta")):
            if re.search(patron, texto):
                culpables.append(f"{p.name} contiene {que}")
    assert not culpables, (
        "Detalles de plataforma fuera de infraestructura:\n   "
        + "\n   ".join(culpables)
        + "\n   El mismo artefacto debe correr en desarrollo, pruebas y "
          "producción: cambia el entorno, no el código."
    )


def test_la_configuracion_entra_por_el_entorno():
    importar("clinicasegura.arranque")
    fuente = codigo(PAQUETE / "arranque.py")
    assert "environ" in fuente or "getenv" in fuente, (
        "arranque.py debe leer la configuración del entorno (os.environ) "
        "con valores por defecto razonables. Factor III de los doce factores."
    )
    construir = obtener("clinicasegura.arranque", "construir_servicio")
    os.environ.setdefault("FARMACIA_TIMEOUT_MS", "1500")
    servicio = construir()
    assert servicio is not None, "construir_servicio() debe devolver el caso de uso armado."


def test_no_se_usa_open_con_codificacion_implicita():
    culpables = []
    for p in archivos_py():
        for nodo in ast.walk(arbol(p)):
            if (isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Name)
                    and nodo.func.id == "open"):
                claves = {k.arg for k in nodo.keywords}
                if "encoding" not in claves:
                    culpables.append(f"{p.name}:{nodo.lineno}")
    assert not culpables, (
        "open() sin encoding explícito en: " + ", ".join(culpables)
        + "\n   En Windows la codificación por defecto no es UTF-8 y el "
          "error solo aparece en la máquina de otra persona."
    )


def test_existe_la_tabla_de_obsolescencia_de_dependencias():
    """Principio 8: el fin de vida entra al backlog, no a la memoria."""
    p = existe_documento("DEPENDENCIAS.md")
    if p is None:
        pytest.fail(
            "Falta DEPENDENCIAS.md. Debe listar cada dependencia externa "
            "con: versión acotada, licencia, riesgo y ruta de salida."
        )
    filas = filas_de_tabla(p.read_text(encoding="utf-8"))
    assert len(filas) >= 3, (
        f"La tabla tiene {len(filas)} dependencias. Liste al menos tres "
        f"(las suyas y las de la práctica: pytest, pydantic, y la que use "
        f"para hablar con las farmacias)."
    )
    texto = p.read_text(encoding="utf-8").lower()
    for exigido in ("licencia", "salida", "riesgo", "versión"):
        assert exigido in texto, (
            f"DEPENDENCIAS.md no habla de «{exigido}». Adoptar sin criterios "
            f"y no inventar aquí son el mismo error: decidir sin evidencia."
        )
    vacias = [f[0] for f in filas
              if any(c.strip() in ("", "...", "TODO") for c in f)]
    assert not vacias, "Filas incompletas en DEPENDENCIAS.md: " + ", ".join(vacias)
