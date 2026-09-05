"""
ClínicaSegura · módulo de recetas electrónicas — CÓDIGO DE PARTIDA
=================================================================

ADVERTENCIA: este archivo funciona. No tiene errores de sintaxis y, en un
día bueno, hace lo que el negocio pide. Es, aun así, un mal diseño.

Su trabajo en esta práctica NO es corregir errores: es rediseñarlo aplicando
los once principios de Lethbridge (cap. 9) sin cambiar el comportamiento
observable.

Léalo entero antes de tocar nada. Cuente cuántos de los once principios
puede ver violados aquí. Ese conteo es la etapa 0.

NO BORRE ESTE ARCHIVO. Al terminar debe seguir existiendo como referencia
de "cómo estaba antes"; simplemente ya nadie lo importará.
"""

import json
import os
import random
import sqlite3
import urllib.request
from datetime import datetime, timedelta

# --------------------------------------------------------------------------
# Estado global mutable: cualquiera lo lee, cualquiera lo escribe, nadie sabe
# quién lo dejó así. Acoplamiento común de manual.
# --------------------------------------------------------------------------
CONFIG = {
    "farmauno_url": "https://api.farmauno.cr/v3/rx",
    "saludtotal_url": "https://ws.saludtotal.cr/api/recetas",
    "cruzverde_url": "https://soap.cruzverde.cr/Recetas.asmx",
    "vigencia_dias": 30,
    "tarifa_diaria": 250,
    "timeout": 1.5,
}

CACHE_PACIENTES = {}
ULTIMO_ERROR = None
CONTADOR_EMITIDAS = 0


class ServicioRecetas:
    """Una clase que hace absolutamente todo: valida, calcula, habla HTTP,
    escribe en la base de datos, genera folios y registra bitácora."""

    def __init__(self):
        # La dependencia se construye adentro: no hay forma de sustituirla.
        self.db = sqlite3.connect(os.path.join("/tmp", "clinicasegura.db"))
        self.db.execute(
            "CREATE TABLE IF NOT EXISTS bitacora "
            "(folio TEXT, evento TEXT, cuando TEXT)"
        )

    # ---------------------------------------------------------------- API
    def emitir(self, datos, cadena):
        """datos es un diccionario que viene tal cual del formulario web."""
        global CONTADOR_EMITIDAS, ULTIMO_ERROR

        # Aserción sobre datos que vienen de afuera: desaparece con python -O.
        assert datos["dias"] > 0, "los dias deben ser positivos"
        assert float(datos["dosis_mg"]) > 0

        # Reloj incrustado: imposible probar la vigencia sin esperar.
        vence = datetime.now() + timedelta(days=CONFIG["vigencia_dias"])

        # Azar incrustado: imposible predecir el folio en una prueba.
        folio = str(random.randint(100000, 999999))

        # Regla de negocio mezclada con efecto de borde y con lectura global.
        recargo = 0
        if datos.get("riesgo_alto"):
            recargo = CONFIG["tarifa_diaria"] * datos["dias"] * 2
        else:
            recargo = CONFIG["tarifa_diaria"] * datos["dias"]

        # Condicional por tipo: cada cadena nueva obliga a editar esta función.
        if cadena == "farmauno":
            respuesta = self._post(
                CONFIG["farmauno_url"],
                {"rx": datos, "vence": vence.isoformat(), "folio": folio},
            )
        elif cadena == "saludtotal":
            respuesta = self._post(
                CONFIG["saludtotal_url"],
                {"receta": datos, "expira": vence.strftime("%d/%m/%Y")},
            )
        elif cadena == "cruzverde":
            respuesta = self._post(
                CONFIG["cruzverde_url"],
                {"Envelope": {"Receta": datos, "Folio": folio}},
            )
        else:
            return None  # el error viaja callado hasta el reporte gerencial

        try:
            self.db.execute(
                "INSERT INTO bitacora VALUES (?, ?, ?)",
                (folio, "emitida", datetime.now().isoformat()),
            )
            self.db.commit()
        except Exception:
            pass  # la única política prohibida del curso

        CONTADOR_EMITIDAS += 1
        CACHE_PACIENTES[datos["cedula"]] = datos

        # Devuelve un diccionario sin contrato: el llamador adivina las llaves.
        return {
            "folio": folio,
            "vence": vence.isoformat(),
            "recargo": recargo,
            "http": respuesta,
            "cadena": cadena,
        }

    # ------------------------------------------------------------ interno
    def _post(self, url, cuerpo):
        intentos = 0
        while True:  # reintento sin límite ni espera creciente
            try:
                peticion = urllib.request.Request(
                    url,
                    data=json.dumps(cuerpo).encode("utf-8"),
                    headers={"Content-Type": "application/json"},
                )
                with urllib.request.urlopen(
                    peticion, timeout=CONFIG["timeout"]
                ) as r:
                    return r.status
            except Exception:
                intentos += 1
                if intentos > 1000000:
                    return -1  # devolver menos uno en vez de lanzar

    def buscar_paciente(self, cedula):
        """Devuelve el JSON crudo del proveedor. El dominio entero termina
        conociendo la forma del JSON de un tercero."""
        if cedula in CACHE_PACIENTES:
            return CACHE_PACIENTES[cedula]
        url = "https://api.exp.cr/v2/pac?ced=" + cedula
        with urllib.request.urlopen(url, timeout=CONFIG["timeout"]) as r:
            return json.loads(r.read())

    def reporte(self, paciente):
        """Acoplamiento de estampado: recibe el paciente completo para usar
        exactamente dos campos."""
        return "%s (%s)" % (
            paciente["data"]["attributes"]["full_name"],
            paciente["data"]["attributes"]["risk_lvl"],
        )

    def validar_cedula(self, c):
        """Reimplementa a mano algo que ya resuelve la biblioteca estándar."""
        partes = c.split("-")
        if len(partes) != 3:
            return False
        if len(partes[0]) != 1:
            return False
        if len(partes[1]) != 4 or len(partes[2]) != 4:
            return False
        for p in partes:
            for ch in p:
                if ch < "0" or ch > "9":
                    return False
        return True

    def exportar(self, ruta="C:\\ClinicaSegura\\export\\recetas.txt"):
        """Ruta literal de un solo sistema operativo, codificación implícita."""
        f = open(ruta, "w")
        f.write(str(CACHE_PACIENTES))
        f.close()
