"""Utilidades de apoyo para las pruebas de la práctica.

No hay que modificar este archivo. Existe para que los mensajes de error
digan qué falta, en vez de un ImportError seco.
"""
from __future__ import annotations

import ast
import importlib
import inspect
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
PAQUETE = RAIZ / "clinicasegura"


# --------------------------------------------------------------- importar
def importar(ruta: str):
    """Importa un módulo del proyecto y falla con un mensaje útil."""
    import pytest
    try:
        return importlib.import_module(ruta)
    except ModuleNotFoundError as e:
        pytest.fail(
            f"Falta el módulo «{ruta}».\n"
            f"   Cree el archivo {ruta.replace('.', '/')}.py "
            f"(y el __init__.py de su paquete).\n"
            f"   Detalle: {e}"
        )
    except Exception as e:  # error dentro del módulo del estudiante
        pytest.fail(f"El módulo «{ruta}» existe pero no se pudo importar: "
                    f"{type(e).__name__}: {e}")


def obtener(ruta: str, nombre: str):
    """Importa `nombre` desde el módulo `ruta`."""
    import pytest
    mod = importar(ruta)
    if not hasattr(mod, nombre):
        pytest.fail(
            f"El módulo «{ruta}» no define «{nombre}».\n"
            f"   Revise el contrato de la etapa en la guía."
        )
    return getattr(mod, nombre)


# ----------------------------------------------------------- inspección
def archivos_py(subruta: str = "") -> list[Path]:
    base = PAQUETE / subruta if subruta else PAQUETE
    if not base.exists():
        return []
    return [p for p in base.rglob("*.py") if "legado" not in p.name]


def arbol(p: Path) -> ast.Module:
    return ast.parse(p.read_text(encoding="utf-8"), filename=str(p))


def modulos_importados(p: Path) -> set[str]:
    """Nombres de primer nivel importados por el archivo."""
    nombres: set[str] = set()
    for nodo in ast.walk(arbol(p)):
        if isinstance(nodo, ast.Import):
            for a in nodo.names:
                nombres.add(a.name.split(".")[0])
        elif isinstance(nodo, ast.ImportFrom):
            if nodo.level:            # import relativo
                continue
            if nodo.module:
                nombres.add(nodo.module.split(".")[0])
    return nombres


def codigo(p: Path) -> str:
    """Código del archivo SIN comentarios ni docstrings.

    Así las pruebas juzgan lo que el programa hace, no lo que el
    comentario dice. Un docstring que menciona «post» para explicar por
    qué NO se usa esa palabra no debe hacer fallar nada.
    """
    tree = arbol(p)
    for nodo in ast.walk(tree):
        if isinstance(nodo, (ast.Module, ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            cuerpo = getattr(nodo, "body", [])
            if (cuerpo and isinstance(cuerpo[0], ast.Expr)
                    and isinstance(cuerpo[0].value, ast.Constant)
                    and isinstance(cuerpo[0].value.value, str)):
                cuerpo.pop(0)
                if not cuerpo:
                    cuerpo.append(ast.Pass())
    ast.fix_missing_locations(tree)
    return ast.unparse(tree)


def codigo_de(subruta: str = "") -> str:
    return "\n".join(codigo(p) for p in archivos_py(subruta))


def identificadores(p: Path) -> set[str]:
    """Nombres que el programador eligió: clases, funciones, atributos."""
    nombres: set[str] = set()
    for nodo in ast.walk(arbol(p)):
        if isinstance(nodo, (ast.ClassDef, ast.FunctionDef,
                             ast.AsyncFunctionDef)):
            nombres.add(nodo.name)
            if isinstance(nodo, (ast.FunctionDef, ast.AsyncFunctionDef)):
                nombres.update(a.arg for a in nodo.args.args)
        elif isinstance(nodo, ast.Name):
            nombres.add(nodo.id)
        elif isinstance(nodo, ast.Attribute):
            nombres.add(nodo.attr)
        elif isinstance(nodo, ast.arg):
            nombres.add(nodo.arg)
    return nombres


def texto_de(subruta: str = "") -> str:
    return "\n".join(p.read_text(encoding="utf-8") for p in archivos_py(subruta))


def parametros(func) -> list[str]:
    return [n for n in inspect.signature(func).parameters if n != "self"]


def anotaciones(func) -> dict:
    return {n: p.annotation
            for n, p in inspect.signature(func).parameters.items()
            if n != "self"}


def existe_documento(nombre: str) -> Path | None:
    p = RAIZ / nombre
    return p if p.exists() else None


def filas_de_tabla(md: str) -> list[list[str]]:
    """Filas de datos de la primera tabla markdown del texto."""
    filas = []
    for linea in md.splitlines():
        linea = linea.strip()
        if not linea.startswith("|"):
            continue
        celdas = [c.strip() for c in linea.strip("|").split("|")]
        if not celdas:
            continue
        if all(set(c) <= set("-: ") and c for c in celdas):
            continue                      # separador de encabezado
        filas.append(celdas)
    return filas[1:] if filas else []      # descarta el encabezado
