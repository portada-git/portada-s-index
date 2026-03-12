"""
Clase base abstracta para todos los algoritmos de similitud.

Define el contrato que cada implementación debe cumplir.
El pipeline no necesita saber si está llamando a Levenshtein
o a un modelo de embeddings: los trata igual a través de esta interfaz.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, ClassVar


# ---------------------------------------------------------------------------
# Errores
# ---------------------------------------------------------------------------

class AlgorithmNotAvailableError(ImportError):
    """
    Se solicita un algoritmo cuya dependencia opcional no está instalada.
    El mensaje incluye instrucciones de instalación.
    """


class PreprocessingMismatchError(RuntimeError):
    """
    Se llamó a process() sin haber llamado primero a preprocess()
    para este tipo de algoritmo, o los datos preprocesados pertenecen
    a otro algoritmo.
    """


# ---------------------------------------------------------------------------
# Datos preprocesados
# ---------------------------------------------------------------------------

@dataclass
class PreprocessedData:
    """
    Marca que los datos ya fueron transformados para un algoritmo concreto.

    La guarda del diagrama de secuencia (paso 1.1.6) se implementa
    verificando que algorithm_name coincide con el algoritmo que va a procesar.
    """
    algorithm_name: str
    terms: list[str]            # Términos normalizados/transformados
    voices: list[str]           # Voces normalizadas/transformadas
    extras: dict[str, Any] = field(default_factory=dict)
    # extras: embeddings precalculados, índices, etc.


# ---------------------------------------------------------------------------
# Clase base
# ---------------------------------------------------------------------------

class Algorithm(ABC):
    """
    Interfaz común para todos los algoritmos de similitud.

    Corresponde a la interfaz SimilarityAlgorithm del diagrama de clases.
    """

    #: Nombre del algoritmo. Coincide con la clave en el JSON de config.
    name: ClassVar[str]

    def __init__(self, params: dict[str, Any]) -> None:
        self.params = params

    # ------------------------------------------------------------------
    # Métodos del diagrama de clases
    # ------------------------------------------------------------------

    def set_config(self, params: dict[str, Any]) -> None:
        """
        Actualiza parámetros del algoritmo en tiempo de ejecución.
        Corresponde a setConfig(configurator) del diagrama de clases.
        """
        self.params = params

    def preprocess(self, terms: list[str], voices: list[str]) -> PreprocessedData:
        """
        Prepara datos para este algoritmo.

        La implementación por defecto devuelve los datos tal cual —
        algoritmos léxicos no necesitan preprocesamiento especial.
        Los algoritmos de embeddings sobreescriben este método para
        calcular vectores y guardarlos en extras.

        Corresponde a preProcessData() del diagrama de clases.
        """
        return PreprocessedData(
            algorithm_name=self.name,
            terms=terms,
            voices=voices,
        )

    def process(self, data: PreprocessedData) -> "SimilarityMatrix":  # noqa: F821
        """
        Calcula la matriz de similitud completa.

        Solo puede llamarse si preprocess() fue ejecutado previamente
        para este algoritmo (guarda del diagrama de secuencia).

        Corresponde a process(data_citations, data_voices) del diagrama.
        """
        from portada_s_index.matrix import SimilarityMatrix, Similarity

        self._assert_preprocessed(data)

        entries = []
        for term in data.terms:
            scores = self.batch(term, data.voices)
            for voice, score in zip(data.voices, scores):
                entries.append(
                    Similarity(
                        citation_id=term,
                        voice_id=voice,
                        algorithm_name=self.name,
                        similarity_value=round(score, 6),
                    )
                )
        return SimilarityMatrix(algorithm_name=self.name, entries=entries)

    # ------------------------------------------------------------------
    # Métodos de cálculo
    # ------------------------------------------------------------------

    @abstractmethod
    def similarity(self, a: str, b: str) -> float:
        """
        Score 0-1 entre dos strings individuales ya normalizados.
        Método principal que cada algoritmo debe implementar.
        """

    def batch(self, query: str, candidates: list[str]) -> list[float]:
        """
        Calcula similitud de query contra todos los candidatos.

        Implementación por defecto: loop sobre similarity().
        Los algoritmos de embeddings sobreescriben esto para vectorizar
        en lote, lo que es órdenes de magnitud más eficiente.
        """
        return [self.similarity(query, c) for c in candidates]

    # ------------------------------------------------------------------
    # Utilidades internas
    # ------------------------------------------------------------------

    def _assert_preprocessed(self, data: PreprocessedData) -> None:
        """
        Guarda del diagrama de secuencia (paso 1.1.6).
        Verifica que los datos fueron preprocesados para este algoritmo.
        """
        if data.algorithm_name != self.name:
            raise PreprocessingMismatchError(
                f"Los datos fueron preprocesados para '{data.algorithm_name}', "
                f"pero se está intentando procesar con '{self.name}'. "
                f"Llama a preprocess() antes de process()."
            )

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(params={self.params})"