# ARCHIVO: src/portada_s_index/__init__.py
"""
portada_s_index — Librería de desambiguación de términos históricos.

API pública mínima:

    from portada_s_index import SimilarityService
    from portada_s_index.data import VoiceList

    voice_list = VoiceList.from_txt("ship_type", "listas/lista_barcos.txt")
    service = SimilarityService.from_file("config_ship_type.json")
    results = service.evaluate(terms_json, voice_list)
"""

from portada_s_index.service import SimilarityService
from portada_s_index.config import PipelineConfig, AlgorithmConfig, ConsensusConfig
from portada_s_index.data.voice_list import VoiceList
from portada_s_index.data.citation import parse_citations
from portada_s_index.scoring import TermResult, AlgorithmScore, Classification
from portada_s_index.cache import ModelCache

__all__ = [
    # Punto de entrada principal
    "SimilarityService",
    # Configuración
    "PipelineConfig",
    "AlgorithmConfig",
    "ConsensusConfig",
    # Datos
    "VoiceList",
    "parse_citations",
    # Resultados
    "TermResult",
    "AlgorithmScore",
    "Classification",
    # Cache
    "ModelCache",
]

__version__ = "0.1.0"