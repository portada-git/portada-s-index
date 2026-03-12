"""
Cache de modelos de embeddings y arrays numpy.

Dos niveles:
- Memoria : modelos cargados viven en el proceso Python actual (singleton).
- Disco   : embeddings precalculados de voces se persisten como .npy
            en ~/.portada_s_index/cache/

La clave de disco incluye un hash del contenido, así si los datos
o el modelo cambian, el cache se invalida automáticamente.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Callable

import numpy as np

logger = logging.getLogger(__name__)

_CACHE_DIR = Path.home() / ".portada_s_index" / "cache"


class ModelCache:
    """
    Singleton. Gestiona modelos pesados entre llamadas.

    Nivel 1 — Memoria:
        La primera llamada a get_model() carga el modelo via loader().
        Las siguientes devuelven la instancia ya en memoria.

    Nivel 2 — Disco:
        get_embeddings() busca el array en disco antes de calcular.
        Si no existe, llama a compute() y guarda el resultado.
        Los archivos se nombran por hash del contenido para
        invalidación automática.
    """

    _memory: dict[str, Any] = {}

    # ------------------------------------------------------------------
    # Cache de modelos (memoria)
    # ------------------------------------------------------------------

    @classmethod
    def get_model(cls, key: str, loader: Callable[[], Any]) -> Any:
        """
        Devuelve el modelo identificado por key.
        Si no está en memoria, llama a loader() una sola vez y lo guarda.

        Args:
            key    : Identificador único del modelo (ej: "fasttext_/path/model.bin")
            loader : Callable sin argumentos que construye y devuelve el modelo.
        """
        if key not in cls._memory:
            logger.debug("Cargando modelo: %s", key)
            cls._memory[key] = loader()
            logger.debug("Modelo cargado: %s", key)
        return cls._memory[key]

    @classmethod
    def clear_model(cls, key: str | None = None) -> None:
        """
        Elimina un modelo de memoria.
        Si key es None, limpia toda la memoria.
        """
        if key is None:
            cls._memory.clear()
            logger.debug("Cache de modelos limpiado completamente")
        elif key in cls._memory:
            del cls._memory[key]
            logger.debug("Modelo eliminado de cache: %s", key)

    # ------------------------------------------------------------------
    # Cache de embeddings (disco)
    # ------------------------------------------------------------------

    @classmethod
    def get_embeddings(
        cls,
        cache_key: str,
        compute: Callable[[], np.ndarray],
    ) -> np.ndarray:
        """
        Devuelve embeddings desde disco si existen, si no los calcula y guarda.

        Args:
            cache_key : Clave única (incluye hash de contenido + nombre de modelo).
            compute   : Callable que calcula y devuelve el array numpy.
        """
        path = cls._embedding_path(cache_key)

        if path.exists():
            logger.debug("Embeddings desde disco: %s", cache_key)
            return np.load(str(path))

        logger.debug("Calculando embeddings: %s", cache_key)
        vecs = compute()

        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(str(path), vecs)
        logger.debug("Embeddings guardados en disco: %s", path)

        return vecs

    @classmethod
    def clear_embeddings(cls, cache_key: str | None = None) -> None:
        """
        Elimina archivos de embeddings en disco.
        Si cache_key es None, elimina todos.
        """
        if cache_key is None:
            for f in _CACHE_DIR.glob("*.npy"):
                f.unlink()
                logger.debug("Eliminado: %s", f)
        else:
            path = cls._embedding_path(cache_key)
            if path.exists():
                path.unlink()
                logger.debug("Eliminado: %s", path)

    @classmethod
    def _embedding_path(cls, cache_key: str) -> Path:
        return _CACHE_DIR / f"{cache_key}.npy"

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @classmethod
    def models_in_memory(cls) -> list[str]:
        """Lista de claves de modelos actualmente en memoria."""
        return list(cls._memory.keys())

    @classmethod
    def embeddings_on_disk(cls) -> list[str]:
        """Lista de claves de embeddings guardados en disco."""
        if not _CACHE_DIR.exists():
            return []
        return [f.stem for f in _CACHE_DIR.glob("*.npy")]