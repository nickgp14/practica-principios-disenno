"""EVIDENCIA DE AUTORÍA  —  se revisa junto con todo lo demás.

Esta batería no evalúa su diseño: evalúa que el diseño lo hizo usted, y
que lo hizo entendiendo, no copiando un resultado final.

Lo que se pide, y por qué:

  ESTUDIANTE.txt        Nombre y carné. Trivial, pero sin esto nada se
                        puede atribuir.

  EVIDENCIA/registro.jsonl
                        Lo genera solo el marcador, cada vez que lo corre.
                        Guarda la fecha, una huella de su código en ese
                        momento y un sello encadenado con la corrida
                        anterior. Un rediseño real deja una traza: varias
                        corridas, con el código cambiando entre ellas y las
                        pruebas pasando de rojo a verde. Un archivo pegado
                        de otra parte deja una sola corrida, ya en verde.

  BITACORA.md           Una entrada por etapa con cuatro campos:
                          **Predicción:**  qué cree que va a pasar, ANTES
                                           de correr el experimento.
                          **Observación:** lo que efectivamente pasó, con
                                           la salida pegada.
                          **Explicación:** por qué, citando SU archivo y SU
                                           línea (formato archivo.py:42).
                          **Sello:**       el que imprimió el marcador al
                                           cerrar esa etapa.

  La predicción es la parte que enseña. Equivocarse en la predicción y
  entender por qué vale más que acertar: escríbala aunque crea que está
  mal, no la corrija después.
"""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
from datetime import datetime

import pytest

from pruebas.apoyo import RAIZ, existe_documento

REGISTRO = RAIZ / "EVIDENCIA" / "registro.jsonl"
CAMPOS = ("predicción", "observación", "explicación", "sello")
CITA = re.compile(r"[\w/]+\.py:\d+")


# ------------------------------------------------------------ identidad
def test_el_estudiante_se_identifica():
    p = existe_documento("ESTUDIANTE.txt")
    if p is None:
        pytest.fail("Falta ESTUDIANTE.txt con «Nombre:» y «Carne:».")
    texto = p.read_text(encoding="utf-8").lower()
    for campo in ("nombre", "carne"):
        linea = [l for l in texto.splitlines() if l.strip().startswith(campo)]
        assert linea and linea[0].split(":", 1)[1].strip(), (
            f"ESTUDIANTE.txt no trae «{campo}»."
        )


# ------------------------------------------------------------- registro
def _corridas() -> list[dict]:
    if not REGISTRO.exists():
        pytest.fail(
            "No existe EVIDENCIA/registro.jsonl.\n"
            "   Se genera solo: corra  python herramientas/marcador.py\n"
            "   al cerrar cada etapa. No lo escriba a mano."
        )
    return [json.loads(l) for l in
            REGISTRO.read_text(encoding="utf-8").splitlines() if l.strip()]


def test_hay_traza_de_varias_corridas():
    c = _corridas()
    assert len(c) >= 7, (
        f"El registro tiene {len(c)} corridas. Se esperan al menos 7: una "
        f"por etapa. Correr el marcador es parte del método, no un trámite "
        f"del final."
    )


def test_el_codigo_cambio_entre_corridas():
    huellas = {c["huella"] for c in _corridas()}
    assert len(huellas) >= 5, (
        f"Solo hay {len(huellas)} versiones distintas del código en todo el "
        f"registro. Un rediseño por etapas deja al menos cinco."
    )


def test_el_trabajo_no_ocurrio_todo_en_un_instante():
    c = _corridas()
    t0 = datetime.fromisoformat(c[0]["cuando"])
    t1 = datetime.fromisoformat(c[-1]["cuando"])
    minutos = (t1 - t0).total_seconds() / 60
    assert minutos >= 45, (
        f"Entre la primera y la última corrida pasaron {minutos:.0f} minutos. "
        f"Esta práctica no se piensa en menos de eso."
    )


def test_se_ve_la_progresion_de_rojo_a_verde():
    c = _corridas()
    def fallos(r):
        return sum(v[1] for v in r["resultados"].values())
    assert fallos(c[0]) >= 8, (
        "La primera corrida ya venía casi en verde. El registro debe "
        "empezar donde empieza la práctica: con el código de partida."
    )
    assert fallos(c[-1]) <= fallos(c[0]), "El avance no puede ir hacia atrás."


def test_el_registro_no_fue_manipulado():
    c = _corridas()
    anterior = "genesis"
    for r in c:
        cuerpo = {k: v for k, v in r.items() if k != "sello"}
        esperado = hashlib.sha256(
            (anterior + json.dumps(cuerpo, sort_keys=True,
                                   ensure_ascii=False)).encode()).hexdigest()
        assert r["sello"] == esperado, (
            f"La corrida #{r['n']} tiene un sello que no corresponde. "
            f"El registro fue editado a mano; bórrelo y rehaga la práctica "
            f"corriendo el marcador de verdad."
        )
        anterior = r["sello"]


# -------------------------------------------------------------- bitácora
def _entradas() -> dict[int, str]:
    p = existe_documento("BITACORA.md")
    if p is None:
        pytest.fail("Falta BITACORA.md. Use la plantilla de la raíz.")
    texto = p.read_text(encoding="utf-8")
    partes = re.split(r"^##\s*Etapa\s*(\d)", texto, flags=re.M)
    return {int(partes[i]): partes[i + 1] for i in range(1, len(partes), 2)}


def _texto_propio(cuerpo: str) -> str:
    """El texto que escribió el estudiante: sin etiquetas, sin la salida
    pegada del experimento y sin las líneas de la plantilla."""
    sin_bloques = re.sub(r"```.*?```", " ", cuerpo, flags=re.S)
    sin_etiquetas = re.sub(r"\*\*[^*]*\*\*:?", " ", sin_bloques)
    sin_sellos = re.sub(r"`?[0-9a-f]{16,64}`?", " ", sin_etiquetas)
    lineas = [l for l in sin_sellos.splitlines()
              if l.strip() and not l.strip().startswith(("#", ">", "|"))]
    return " ".join(" ".join(lineas).split())


def test_hay_una_entrada_de_bitacora_por_cada_etapa():
    faltan = [n for n in range(7) if n not in _entradas()]
    assert not faltan, "Faltan entradas de bitácora para las etapas: " + str(faltan)


@pytest.mark.parametrize("n", range(7))
def test_cada_entrada_trae_los_cuatro_campos_llenos(n):
    cuerpo = _entradas().get(n, "")
    bajo = cuerpo.lower()
    for campo in CAMPOS:
        assert campo in bajo, f"La etapa {n} no tiene el campo «{campo}»."
    propio = _texto_propio(cuerpo)
    assert len(propio) > 200, (
        f"La entrada de la etapa {n} tiene {len(propio)} caracteres de texto "
        f"propio y se esperan más de 200. Se piden sus palabras, no un "
        f"resumen de una línea."
    )


@pytest.mark.parametrize("n", range(7))
def test_la_explicacion_cita_su_propio_codigo(n):
    cuerpo = _entradas().get(n, "")
    assert CITA.search(cuerpo), (
        f"La etapa {n} no cita ningún archivo con número de línea "
        f"(por ejemplo servicio.py:24). Una explicación sin evidencia vale "
        f"cero: es la misma regla del informe del proyecto."
    )


@pytest.mark.parametrize("n", range(7))
def test_la_prediccion_y_la_observacion_no_son_el_mismo_texto(n):
    cuerpo = _entradas().get(n, "")
    def campo(nombre):
        m = re.search(rf"\*\*{nombre}[^*]*\*\*:?(.*?)(?=\*\*|\Z)",
                      cuerpo, flags=re.S | re.I)
        return " ".join(m.group(1).split()).lower() if m else ""
    pred, obs = campo("predicci"), campo("observaci")
    assert pred and obs, f"La etapa {n} tiene predicción u observación vacía."
    assert pred != obs, (
        f"En la etapa {n} la predicción y la observación son idénticas. "
        f"La predicción se escribe antes de correr nada; si coincidieron "
        f"palabra por palabra, no hubo predicción."
    )


@pytest.mark.parametrize("n", range(7))
def test_el_sello_de_la_entrada_existe_en_el_registro(n):
    cuerpo = _entradas().get(n, "")
    m = re.search(r"\*\*sello[^*]*\*\*:?\s*`?([0-9a-f]{16,64})`?",
                  cuerpo, flags=re.I)
    assert m, (
        f"La etapa {n} no trae el sello que imprime el marcador. "
        f"Córralo al cerrar la etapa y pegue el valor."
    )
    sellos = [c["sello"] for c in _corridas()]
    assert any(s.startswith(m.group(1)) for s in sellos), (
        f"El sello de la etapa {n} no corresponde a ninguna corrida "
        f"registrada."
    )


# ------------------------------------------------------------------ git
def test_el_historial_de_git_acompana_el_trabajo():
    if not (RAIZ / ".git").exists():
        pytest.skip("El proyecto no está en git; se evalúa solo el registro.")
    r = subprocess.run(["git", "log", "--oneline"], cwd=RAIZ,
                       capture_output=True, text=True)
    commits = [l for l in r.stdout.splitlines() if l.strip()]
    assert len(commits) >= 7, (
        f"Hay {len(commits)} commits. Se espera al menos uno por etapa, "
        f"con un mensaje que diga qué principio aplicó y por qué."
    )
