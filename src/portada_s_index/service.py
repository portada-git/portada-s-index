"""
Servicio principal de desambiguación.

Corresponde al participante `similarityService` del diagrama de secuencia.
Orquesta el flujo completo:

  getCitations → getVoices → instanceConfigurator → instanceAlgorithm
  → setConfig → preprocess → saveData(cache) → process → classify

Es el único punto de entrada recomendado para el usuario externo.
"""

from __future__ import annotations

import logging
from pathlib import Path

from portada_s_index.algorithms import build as build_algorithm
from portada_s_index.algorithms.base import Algorithm, PreprocessedData
from portada_s_index.cache import ModelCache
from portada_s_index.cleaning import PortadaCleaningLayer, Configurator
from portada_s_index.config import AlgorithmConfig, PipelineConfig
from portada_s_index.data.citation import CitationRow
from portada_s_index.data.voice_list import VoiceList, Voice
from portada_s_index.normalize import normalize
from portada_s_index.scoring import AlgorithmScore

logger = logging.getLogger(__name__)


class SimilarityService:
    """
    Orquestador principal. Implementa el flujo del diagrama de secuencia.

    Uso básico:
        service = SimilarityService.from_file("config.json")
        results = service.evaluate(terms_json, voice_list)

    results es una lista de dicts lista para json.dumps().
    """

    def __init__(self, config: PipelineConfig) -> None:
        self._config = config
        self._cleaning = PortadaCleaningLayer()

    @classmethod
    def from_file(cls, path: str | Path) -> "SimilarityService":
        """Crea el servicio cargando la configuración desde un archivo JSON."""
        return cls(PipelineConfig.from_file(path))

    @classmethod
    def from_dict(cls, data: dict) -> "SimilarityService":
        """Crea el servicio desde un dict ya parseado."""
        return cls(PipelineConfig.from_dict(data))

    # ------------------------------------------------------------------
    # Punto de entrada principal
    # ------------------------------------------------------------------

    def evaluate(
        self,
        terms: list[dict] | list[str],
        voice_list: VoiceList,
    ) -> list[dict]:
        """
        Evalúa una lista de términos contra una lista de voces conocidas.

        Implementa el flujo completo del diagrama de secuencia.

        Args:
            terms      : Lista de dicts {"term": ..., "frequency": ...}
                         o lista de strings.
            voice_list : Lista de voces provista por el usuario.

        Returns:
            Lista de dicts (TermResult.to_dict()) lista para json.dumps().
        """

        # 1.1.1: getCitations — extrae y normaliza los términos
        logger.debug("Extrayendo citas...")
        citations = self._cleaning.extract_citations(terms)

        # 1.1.2: getVoices — obtiene las voces conocidas
        logger.debug("Obteniendo voces para entity_type=%s", voice_list.entity_type)
        voices = self._cleaning.get_known_entity_voices(
            entity_type=voice_list.entity_type,
            voice_list=voice_list,
        )

        term_ids = [c.id for c in citations]
        voice_norms = [v.normalized for v in voices]

        # Mejores matches por algoritmo: algo_name → term → (voice, score)
        # Esta estructura evita materializar matrices completas término×voz.
        best_matches_by_algorithm: dict[str, dict[str, tuple[str, float]]] = {}

        execution_configs = self._config.execution_algorithms

        for algo_config in execution_configs:

            # 1.1.3: instanceConfigurator — un Configurator por algoritmo
            configurator = self._cleaning.instance_configurator(
                algorithm_type=algo_config.name,
                config=algo_config,
            )
            logger.debug("Configurador creado: %s", configurator)

            # 1.1.4: instanceAlgorithm — instancia el algoritmo
            algorithm = build_algorithm(algo_config)
            logger.debug("Algoritmo instanciado: %s", algorithm)

            # 1.1.5: setConfig — aplica configuración al algoritmo
            algorithm.set_config(configurator.params)

            # 1.1.6: preprocess — prepara datos (con guarda de tipo)
            logger.debug("Preprocesando datos para %s...", algo_config.name)
            preprocessed = algorithm.preprocess(term_ids, voice_norms)

            # 1.1.7: saveData — guarda datos preprocesados en cache
            # Para embeddings el cache de disco ya se maneja en preprocess().
            # Aquí guardamos la referencia en memoria para posibles reusos.
            cache_key = f"preprocessed_{algo_config.name}_{voice_list.entity_type}"
            ModelCache.get_model(cache_key, lambda p=preprocessed: p)

            # 1.1.8 / 1.1.9: best_matches — calcula solo la mejor voz por término.
            logger.debug("Procesando mejores similitudes para %s...", algo_config.name)
            best_matches_by_algorithm[algo_config.name] = algorithm.best_matches(preprocessed)

        # Construir resultados crudos para que el frontend clasifique dinámicamente.
        logger.debug("Construyendo resultados crudos para %d términos...", len(citations))
        results = []
        for citation in citations:
            result = self._build_raw_citation_result(
                citation=citation,
                best_matches_by_algorithm=best_matches_by_algorithm,
                voice_list=voice_list,
                execution_configs=execution_configs,
            )
            results.append(result)

        return results

    # ------------------------------------------------------------------
    # Lógica interna de resultados crudos por término
    # ------------------------------------------------------------------

    def _build_raw_citation_result(
        self,
        citation: CitationRow,
        best_matches_by_algorithm: dict[str, dict[str, tuple[str, float]]],
        voice_list: VoiceList,
        execution_configs: list[AlgorithmConfig] | None = None,
    ) -> dict:
        """Construye los scores por algoritmo sin emitir clasificación final."""

        term_id = citation.id

        # Verificar match exacto
        exact_match = voice_list.is_exact(term_id)

        # Construir scores por algoritmo
        algo_scores: list[AlgorithmScore] = []
        for algo_config in execution_configs or self._config.execution_algorithms:
            best_matches = best_matches_by_algorithm.get(algo_config.name)
            if best_matches is None:
                continue

            best = best_matches.get(term_id)
            if best is None:
                continue

            best_voice, score = best
            best_entity = voice_list.entity_of(best_voice)
            threshold = algo_config.threshold
            piso, techo = algo_config.gray_zone

            algo_scores.append(AlgorithmScore(
                algorithm=algo_config.name,
                best_voice=best_voice,
                best_entity=best_entity,
                score=score,
                threshold=threshold,
                voted=score >= threshold,
                in_gray_zone=(piso <= score < threshold),
            ))

        return {
            "term": citation.citation,
            "frequency": citation.frequency,
            "normalized": term_id,
            "exact_match": exact_match,
            "entity_type": voice_list.entity_type,
            "allowed_algorithms": self._config.allowed_names_for_entity(voice_list.entity_type),
            "algorithm_scores": [score.to_dict() for score in algo_scores],
        }

    # ------------------------------------------------------------------
    # Utilidades
    # ------------------------------------------------------------------

    @property
    def config(self) -> PipelineConfig:
        return self._config

    @property
    def active_algorithms(self) -> list[str]:
        return self._config.execution_algorithm_names
