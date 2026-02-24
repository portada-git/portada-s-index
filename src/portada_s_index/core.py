"""
Core module implementing the class-based structure for PortAda S-Index.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
import json

from .similarity import (
    SimilarityAlgorithm,
    SimilarityConfig,
    calculate_similarity,
    classify_name,
    TermClassification,
    SimilarityResult
)
from .utils import generate_summary_report


@dataclass
class EntityCitation:
    id: str
    cited_name: str
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class KnownEntity:
    name: str
    voices: List[str]
    attributes: Dict[str, Any] = field(default_factory=dict)

class SimilarityMatrix:
    """
    Represents the 3D similarity matrix (NxMxA) calculated for the citations and voices.
    """
    def __init__(self, matrix_data: List[TermClassification]):
        self.data = matrix_data
    
    def get_raw_data(self) -> List[TermClassification]:
        return self.data
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "matrix": [item.to_dict() for item in self.data]
        }


class PortAdaSIndex:
    """
    Main class for the PortAda S-Index library.
    Manages similarity index calculations between citations and recognized voices.
    """
    
    def __init__(self, config: Optional[SimilarityConfig] = None):
        """
        Initializes the PortAdaSIndex library with a configuration.
        """
        self.config = config or SimilarityConfig()
        self.known_entities: List[KnownEntity] = []
        self.citations: List[EntityCitation] = []
        self.entity_type: str = "Unknown"
        self._voice_to_entity: Dict[str, str] = {}
        self._similarity_matrix: Optional[SimilarityMatrix] = None

    def load_known_entities(self, entities: List[KnownEntity]):
        """Load a list of known entities."""
        self.known_entities = entities
        self._voice_to_entity = {}
        for entity in self.known_entities:
            for voice in entity.voices:
                self._voice_to_entity[voice] = entity.name

    def load_citations(self, citations: List[EntityCitation]):
        """Load a list of entity citations."""
        self.citations = citations

    def set_entity_type(self, entity_type: str):
        """Set the entity type being processed."""
        self.entity_type = entity_type

    def _get_voices_list(self) -> List[str]:
        """Extract a flat list of voices from known entities."""
        if not self.known_entities:
            # When working with unknown entities, the comparison is made between citations
            return [citation.cited_name for citation in self.citations]
        
        voices_set = set()
        for entity in self.known_entities:
            for voice in entity.voices:
                voices_set.add(voice)
        return list(voices_set)

    def generate_similarity_matrix(self) -> SimilarityMatrix:
        """
        Generates the Similarity Matrix by computing similarities for each pair of items.
        Returns the parsed matrix mapping.
        """
        names = [c.cited_name for c in self.citations]
        voices = self._get_voices_list()
        
        # Determine frequencies
        freq: Dict[str, int] = {}
        for n in names:
            freq[n] = freq.get(n, 0) + 1
            
        # Get unique names for the calculation to avoid redundant processing
        unique_names = list(freq.keys())
        
        classifications = classify_name(
            name=unique_names,
            voices=voices,
            frequencies=freq,
            config=self.config,
            voice_to_entity=self._voice_to_entity
        )
        
        self._similarity_matrix = SimilarityMatrix(classifications)
        return self._similarity_matrix

    def get_statistical_report(self) -> Dict[str, Any]:
        """
        Produces a statistical report based on the generated similarity matrix.
        """
        if not self._similarity_matrix:
            raise ValueError("You must generate the similarity matrix first.")
            
        classifications = self._similarity_matrix.get_raw_data()
        
        total_citations = len(self.citations)
        names = [c.cited_name for c in self.citations]
        unique_citations = len(set(names))
        voices = self._get_voices_list()
        
        # We reuse the existing summary report tool
        summary = generate_summary_report(classifications, total_citations, self.config)
        
        report = {
            "entity_type": self.entity_type,
            "total_citations": total_citations,
            "unique_citations": unique_citations,
            "total_voices": len(voices),
            "configuration": self.config.to_dict(),
            "results": summary
        }
        return report

    def get_result_matrix(self) -> Any:
        """
        Returns the result matrix.
        """
        pass
