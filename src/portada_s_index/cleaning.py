"""
Capa de acceso y preprocesamiento de datos.

Corresponde al participante `portadaCleaningLayer` del diagrama de secuencia.
Sabe extraer datos de la fuente y construir objetos del dominio.
No conoce algoritmos ni lógica de scoring.
"""

from __future__ import annotations

from portada_s_index.config import AlgorithmConfig, PipelineConfig
from portada_s_index.data.citation import CitationRow, parse_citations
from portada_s_index.data.voice_list import VoiceList, Voice
from portada_s_index.normalize import normalize


class Configurator:
    """
    Configuración específica para un tipo de algoritmo.

    Instanciada por PortadaCleaningLayer.instance_configurator().
    Transporta los parámetros del algoritmo al momento de setConfig().
    Corresponde al objeto `configurator` del diagrama de secuencia.
    """

    def __init__(self, algorithm_type: str, config: AlgorithmConfig) -> None:
        self.algorithm_type = algorithm_type
        self.threshold = config.threshold
        self.gray_zone = config.gray_zone
        self.params = config.params

    def __repr__(self) -> str:
        return f"Configurator(type={self.algorithm_type!r}, threshold={self.threshold})"


class PortadaCleaningLayer:
    """
    Capa de acceso a datos.

    Responsabilidades:
    - Convertir JSON de términos → CitationRows (extractX del diagrama)
    - Obtener voces conocidas por tipo de entidad (get_known_entity_voices)
    - Instanciar Configurators por tipo de algoritmo (instanceConfigurator)

    No contiene lógica de similitud ni de clasificación.
    """

    # ------------------------------------------------------------------
    # Extracción de citas (paso 1.1.1.1 del diagrama de secuencia)
    # ------------------------------------------------------------------

    def extract_citations(self, source: list[dict] | list[str]) -> list[CitationRow]:
        """
        Convierte JSON de entrada en CitationRows normalizados.

        Corresponde a extractX del diagrama de secuencia.
        El id de cada CitationRow es el término ya normalizado.

        Args:
            source: Lista de dicts {"term": ..., "frequency": ...}
                    o lista de strings.
        """
        rows = parse_citations(source)
        # Normalizar el id para que coincida con las voces
        for row in rows:
            row.id = normalize(row.citation)
        return rows

    # ------------------------------------------------------------------
    # Obtención de voces (paso 1.1.2.1 del diagrama de secuencia)
    # ------------------------------------------------------------------

    def get_known_entity_voices(
        self,
        entity_type: str,
        voice_list: VoiceList,
    ) -> list[Voice]:
        """
        Devuelve las voces conocidas para el tipo de entidad.

        Corresponde a get_known_entity_voices(type) del diagrama de secuencia.
        El filtro por min_apariciones se aplica opcionalmente aquí.

        Args:
            entity_type : Tipo de entidad (ej: "ship_type", "flag")
            voice_list  : Lista de voces provista por el usuario
        """
        if voice_list.entity_type != entity_type:
            raise ValueError(
                f"La VoiceList es de tipo '{voice_list.entity_type}', "
                f"se esperaba '{entity_type}'."
            )
        return voice_list.all_voices

    # ------------------------------------------------------------------
    # Instanciación de configurador (paso 1.1.3 del diagrama de secuencia)
    # ------------------------------------------------------------------

    def instance_configurator(
        self,
        algorithm_type: str,
        config: AlgorithmConfig,
    ) -> Configurator:
        """
        Crea el Configurator para un tipo de algoritmo específico.

        Corresponde a instanceConfigurator(algorithmType) del diagrama.
        Un Configurator por algoritmo, no uno global.

        Args:
            algorithm_type : Nombre del algoritmo (ej: "levenshtein_ocr")
            config         : AlgorithmConfig con threshold, gray_zone y params
        """
        return Configurator(algorithm_type=algorithm_type, config=config)