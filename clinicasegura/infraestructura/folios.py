"""Generador de folios usando uuid, en vez de random incrustado como el legado."""
import uuid


class GeneradorFolioUUID:
    def siguiente(self) -> str:
        return str(uuid.uuid4())