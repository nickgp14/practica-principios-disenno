"""Marcador de la práctica.

Corre las pruebas etapa por etapa, muestra el avance y deja constancia de
la corrida en EVIDENCIA/registro.jsonl.

    python herramientas/marcador.py            # todas las etapas
    python herramientas/marcador.py 3          # solo la etapa 3

Cada corrida agrega una línea al registro con la fecha, la huella de su
código en ese momento y un sello encadenado con la corrida anterior. Ese
registro es la evidencia de que el rediseño lo hizo usted, paso a paso:
muestra cómo su código fue cambiando y cómo las pruebas fueron pasando de
rojo a verde. Copie el sello que imprime al terminar cada etapa en la
entrada correspondiente de BITACORA.md.

No edite EVIDENCIA/registro.jsonl a mano: los sellos están encadenados y
la prueba de evidencia detecta la manipulación.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

RAIZ = Path(__file__).resolve().parent.parent
EVIDENCIA = RAIZ / "EVIDENCIA"
REGISTRO = EVIDENCIA / "registro.jsonl"

ETAPAS = {
    0: "Diagnóstico",
    1: "Dividir y conquistar · cohesión",
    2: "Acoplamiento",
    3: "Abstracción y reuso",
    4: "Flexibilidad · obsolescencia · portabilidad",
    5: "Testabilidad",
    6: "Diseño defensivo",
}

VERDE, ROJO, GRIS, FIN = "\033[32m", "\033[31m", "\033[90m", "\033[0m"


def huella_del_codigo() -> str:
    """SHA-256 del contenido de todo lo que el estudiante escribe."""
    h = hashlib.sha256()
    archivos = []
    for carpeta in ("clinicasegura", "mis_pruebas"):
        base = RAIZ / carpeta
        if base.exists():
            archivos += sorted(base.rglob("*.py"))
    for doc in ("DIAGNOSTICO.md", "DEPENDENCIAS.md", "BITACORA.md"):
        p = RAIZ / doc
        if p.exists():
            archivos.append(p)
    for p in sorted(archivos):
        h.update(p.relative_to(RAIZ).as_posix().encode())
        h.update(p.read_bytes())
    return h.hexdigest()


def leer_estudiante() -> dict:
    p = RAIZ / "ESTUDIANTE.txt"
    datos = {"nombre": "", "carne": ""}
    if p.exists():
        for linea in p.read_text(encoding="utf-8").splitlines():
            if ":" in linea:
                k, v = linea.split(":", 1)
                k = k.strip().lower().replace("é", "e")
                if k in datos:
                    datos[k] = v.strip()
    return datos


def correr_etapa(n: int) -> tuple[int, int]:
    """Devuelve (pruebas en verde, pruebas por resolver) de la etapa."""
    base = [sys.executable, "-m", "pytest", "-m", f"etapa{n}",
            "-q", "--no-header", "-p", "no:cacheprovider"]

    recolecta = subprocess.run(base + ["--collect-only"], cwd=RAIZ,
                               capture_output=True, text=True)
    lineas = recolecta.stdout.splitlines()
    total = sum(1 for l in lineas if "::" in l)          # formato detallado
    if total == 0:                                        # formato «archivo: N»
        total = sum(int(m.group(1)) for m in
                    (re.search(r":\s*(\d+)\s*$", l) for l in lineas) if m)

    corrida = subprocess.run(base + ["--tb=no"], cwd=RAIZ,
                             capture_output=True, text=True)
    salida = corrida.stdout + corrida.stderr
    fallaron = sum(1 for l in salida.splitlines()
                   if l.startswith(("FAILED", "ERROR")))
    return max(0, total - fallaron), fallaron


def ultimo_sello() -> str:
    if not REGISTRO.exists():
        return "genesis"
    lineas = [l for l in REGISTRO.read_text(encoding="utf-8").splitlines() if l.strip()]
    return json.loads(lineas[-1])["sello"] if lineas else "genesis"


def sellar(registro: dict, anterior: str) -> str:
    cuerpo = json.dumps(registro, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256((anterior + cuerpo).encode()).hexdigest()


def main() -> int:
    etapas = ([int(sys.argv[1])] if len(sys.argv) > 1 else list(ETAPAS))
    estudiante = leer_estudiante()

    print()
    print("  MARCADOR DE LA PRÁCTICA · Principios de diseño")
    print(f"  {estudiante['nombre'] or '(sin nombre en ESTUDIANTE.txt)'}"
          f"   carné {estudiante['carne'] or '—'}")
    print("  " + "─" * 60)

    resultados, total_p, total_f = {}, 0, 0
    for n in etapas:
        p, f = correr_etapa(n)
        resultados[f"etapa{n}"] = [p, f]
        total_p, total_f = total_p + p, total_f + f
        if f == 0 and p > 0:
            marca, color = "verde", VERDE
        elif p == 0 and f == 0:
            marca, color = "sin pruebas", GRIS
        else:
            marca, color = f"{f} por resolver", ROJO
        barra = "█" * p + "░" * f
        print(f"  {color}Etapa {n}{FIN}  {ETAPAS[n]:<44} "
              f"{color}{barra:<14}{FIN} {color}{marca}{FIN}")

    print("  " + "─" * 60)
    print(f"  {total_p} pruebas en verde · {total_f} por resolver")

    EVIDENCIA.mkdir(exist_ok=True)
    registro = {
        "n": sum(1 for _ in REGISTRO.read_text(encoding="utf-8").splitlines()
                 if _.strip()) + 1 if REGISTRO.exists() else 1,
        "cuando": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "estudiante": estudiante["nombre"],
        "carne": estudiante["carne"],
        "huella": huella_del_codigo(),
        "resultados": resultados,
    }
    anterior = ultimo_sello()
    registro["anterior"] = anterior
    registro["sello"] = sellar({k: v for k, v in registro.items()
                                if k != "sello"}, anterior)
    with REGISTRO.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(registro, ensure_ascii=False) + "\n")

    print(f"  corrida #{registro['n']} registrada")
    print(f"  SELLO: {registro['sello'][:16]}")
    print("  Cópielo en la entrada de BITACORA.md de la etapa que acaba "
          "de cerrar.")
    print()
    return 0 if total_f == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
