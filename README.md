# Práctica asíncrona · Principios de diseño

**IC-6821 Diseño de Software** · Escuela de Computación · TEC

Va a rediseñar el módulo de recetas electrónicas de ClínicaSegura aplicando
los **once principios** de Lethbridge (cap. 9). El código de partida
funciona: no tiene errores. Tiene mal diseño, que es otra cosa.

Trabaje solo, a su ritmo. Cuente entre 3 y 4 horas repartidas en al menos
dos sesiones distintas: parte del método es volver al problema con la
cabeza descansada.

---

## Puesta en marcha

```bash
python -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install -r requirements.txt

git init && git add -A && git commit -m "estado inicial"

python herramientas/marcador.py
```

Esa última línea le muestra el tablero. Al empezar está casi todo en rojo:
**es lo esperado**. Llene primero `ESTUDIANTE.txt`.

---

## Cómo se trabaja cada etapa

Las siete etapas tienen siempre la misma forma, y el orden importa:

| Paso | Qué hace | Dónde queda |
|------|----------|-------------|
| 1 | Lee el concepto y el experimento al inicio del archivo de pruebas de la etapa | `pruebas/test_etapaN_*.py` |
| 2 | **Escribe su predicción** antes de correr nada | `BITACORA.md` |
| 3 | Corre el experimento y pega la salida | `BITACORA.md` |
| 4 | Rediseña hasta que la etapa quede en verde | `clinicasegura/` |
| 5 | Explica por qué, citando **su** archivo y **su** línea | `BITACORA.md` |
| 6 | `python herramientas/marcador.py N` y pega el sello | `BITACORA.md` |
| 7 | `git commit` diciendo qué principio aplicó y por qué | historial |

El paso 2 es el que enseña. Equivocarse en la predicción y entender
después por qué vale más que acertar: escríbala aunque crea que está mal,
y **no la corrija después**.

---

## Las siete etapas

| Etapa | Principios | Tema |
|-------|-----------|------|
| 0 | los once, leyendo | Diagnóstico del código de partida |
| 1 | 1, 2 | Dividir y conquistar · cohesión |
| 2 | 3 | Reducir el acoplamiento |
| 3 | 4, 5, 6 | Abstracción y reuso |
| 4 | 7, 8, 9 | Flexibilidad, obsolescencia y portabilidad |
| 5 | 10 | Testabilidad |
| 6 | 11 | Diseño defensivo |

Cada archivo de pruebas empieza con el concepto, el experimento y el
contrato exacto de lo que debe existir. **Léalo antes de programar**: las
pruebas no son un examen sorpresa, son la especificación.

```bash
python herramientas/marcador.py       # tablero completo
python herramientas/marcador.py 3     # solo la etapa 3
pytest -m etapa3                      # el detalle de por qué falla
```

Cuando una prueba falla, el mensaje le dice qué falta y por qué importa.
Léalo completo antes de tocar el código.

---

## Qué se entrega

Un `.zip` (o el enlace al repositorio) con **todo el proyecto**, incluido
el historial de git:

- `clinicasegura/` rediseñado, con `legado.py` intacto como referencia
- `mis_pruebas/` con al menos tres pruebas suyas
- `DIAGNOSTICO.md`, `DEPENDENCIAS.md`, `BITACORA.md` llenos
- `EVIDENCIA/registro.jsonl` — **no lo edite**: lo genera el marcador

## Sobre la evidencia

El marcador deja constancia de cada corrida: la fecha, una huella de su
código en ese momento y un sello encadenado con la corrida anterior. Eso
produce la traza de cómo su rediseño fue avanzando de rojo a verde.

No es vigilancia: es la misma idea de observabilidad que va a aplicar en
la etapa 5. Un trabajo hecho deja rastro; uno copiado aparece completo y
verde en una sola corrida. Las pruebas de `test_evidencia_de_autoria.py`
verifican esa traza y forman parte de la nota.

Si borra el registro por accidente, avísele a la profesora antes de
entregar. Rehacerlo a mano no funciona: los sellos no cuadran y la prueba
lo detecta.

---

## Reglas

- **No modifique** `pruebas/`, `herramientas/` ni `EVIDENCIA/`.
- **No borre** `clinicasegura/legado.py`.
- Puede consultar documentación, la presentación del curso y a sus
  compañeros. Lo que entrega debe ser suyo y debe poder explicarlo:
  la bitácora es donde lo demuestra.
- Puede usar asistentes de IA para consultar conceptos. Si le propone
  código, entiéndalo antes de pegarlo: la bitácora pregunta por **su**
  archivo y **su** línea, y en la defensa se le va a preguntar por
  decisiones concretas de ese código.
