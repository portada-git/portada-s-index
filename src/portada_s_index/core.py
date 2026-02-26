"""
Core module implementing the class-based structure for PortAda S-Index.
"""

import pickle
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, Dict, Optional, Any, Tuple
import json

from .similarity import (
    SimilarityAlgorithm,
    SimilarityConfig,
    calculate_similarity,
    classify_name,
    TermClassification,
    SimilarityResult,
    normalize_text
)
from .strategy import AlgorithmBuilder
from .utils import (
    generate_summary_report, 
    load_voices_from_file, 
    load_name_from_csv
)


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
    Provides stages: Configure, Load, Fit (Preprocess/Cache), and Run.
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
        self._prepared_voices: Dict[SimilarityAlgorithm, List[Dict[str, Any]]] = {}
        self._is_fitted: bool = False

    def load_known_entities(self, entities: List[KnownEntity]):
        """Load a list of known entities."""
        self.known_entities = entities
        self._voice_to_entity = {}
        for entity in self.known_entities:
            for voice in entity.voices:
                voice_norm = normalize_text(voice) if self.config.normalize else voice
                self._voice_to_entity[voice_norm] = entity.name
        self._is_fitted = False

    def load_known_entities_from_file(self, file_path: str | Path):
        """Load known entities from a hierarchical text file."""
        voices, voice_to_entity = load_voices_from_file(file_path)
        
        # Simplified: just set the internal mapping
        self._voice_to_entity = voice_to_entity
        
        # We store the unique voices as dummy entities if needed, 
        # but the important part is _voice_to_entity and returning voices from it.
        self.known_entities = [] # Reset to empty to trigger the mapping branch in _get_voices_list
        self._is_fitted = False

    def load_citations(self, citations: List[EntityCitation]):
        """Load a list of entity citations."""
        self.citations = citations

    def load_citations_from_csv(self, file_path: str | Path):
        """Load citations from a CSV file."""
        names, frequencies = load_name_from_csv(file_path)
        self.citations = [
            EntityCitation(id=str(i), cited_name=name, attributes={"frequency": frequencies.get(name, 1)})
            for i, name in enumerate(names)
        ]

    def set_entity_type(self, entity_type: str):
        """Set the entity type being processed."""
        self.entity_type = entity_type

    def _get_voices_list(self) -> List[str]:
        """Extract a flat list of voices from known entities or mapping."""
        if not self.known_entities and self._voice_to_entity:
             # If loaded from file mapping and no entities objects
             return list(self._voice_to_entity.keys())

        if not self.known_entities:
            # Fallback to citations (unknown entities scenario)
            return [citation.cited_name for citation in self.citations]
        
        # Use entities objects if available
        voices_set = set()
        for entity in self.known_entities:
            for voice in entity.voices:
                voices_set.add(voice)
        return list(voices_set)

    def fit(self, cache_path: Optional[str | Path] = None, force: bool = False):
        """
        Stage: Preprocessing.
        Pre-calculates (trains) the indexes/vectors for all loaded voices and algorithms.
        Optionally saves/loads from cache_path.
        """
        if cache_path:
            cache_path = Path(cache_path)
            if cache_path.exists() and not force:
                try:
                    with open(cache_path, "rb") as f:
                        cache_data = pickle.load(f)
                        if isinstance(cache_data, dict) and "_prepared_voices" in cache_data:
                            self._prepared_voices = cache_data["_prepared_voices"]
                            self._is_fitted = True
                            return
                except Exception:
                    pass # Fallback to re-calculate

        voices = self._get_voices_list()
        self._prepared_voices = {}

        for algo in self.config.algorithms:
            strategy = AlgorithmBuilder.build(algo.value)
            prepared_list = []
            for i, voice in enumerate(voices):
                voice_normalized = normalize_text(voice) if self.config.normalize else voice
                d = {"id": str(i), "voice": voice_normalized}
                prepared_list.append(strategy.prepare_data(d))
            self._prepared_voices[algo] = prepared_list

        self._is_fitted = True

        if cache_path:
            cache_path.parent.mkdir(parents=True, exist_ok=True)
            with open(cache_path, "wb") as f:
                pickle.dump({"_prepared_voices": self._prepared_voices}, f)

    def run(self) -> SimilarityMatrix:
        """
        Stage: Execution.
        Generates the Similarity Matrix by computing similarities for each pair of items.
        Uses pre-calculated data if fit() was called.
        """
        if not self._is_fitted:
            self.fit()

        names = [c.cited_name for c in self.citations]
        voices = self._get_voices_list()
        
        # Determine frequencies
        freq: Dict[str, int] = {}
        for c in self.citations:
            n = c.cited_name
            f = c.attributes.get("frequency", 1)
            freq[n] = freq.get(n, 0) + f
            
        unique_names = list(freq.keys())
        
        classifications = classify_name(
            name=unique_names,
            voices=voices,
            frequencies=freq,
            config=self.config,
            voice_to_entity=self._voice_to_entity,
            prepared_voices=self._prepared_voices
        )
        
        self._similarity_matrix = SimilarityMatrix(classifications)
        return self._similarity_matrix

    def generate_similarity_matrix(self) -> SimilarityMatrix:
        """Alias for run() for backward compatibility."""
        return self.run()

    def get_statistical_report(self) -> Dict[str, Any]:
        """
        Produces a statistical report based on the generated similarity matrix.
        """
        if not self._similarity_matrix:
            raise ValueError("You must run() the analysis first.")
            
        classifications = self._similarity_matrix.get_raw_data()
        
        # Recalculate total occurrences for report
        total_occurrences = sum(c.frequency for c in classifications)
        
        unique_citations = len(classifications)
        voices = self._get_voices_list()
        
        summary = generate_summary_report(classifications, total_occurrences, self.config)
        
        report = {
            "entity_type": self.entity_type,
            "total_citations": total_occurrences,
            "unique_citations": unique_citations,
            "total_voices": len(voices),
            "configuration": self.config.to_dict(),
            "results": summary
        }
        return report

    def get_result_matrix(self) -> List[Dict[str, Any]]:
        """
        Returns a result matrix where each entry contains the term, 
        the target voice, and the scores for all applied algorithms.
        """
        if not self._similarity_matrix:
            raise ValueError("You must run() the analysis first.")
            
        results = []
        for classification in self._similarity_matrix.get_raw_data():
            item = {
                "term": classification.term,
                "best_voice": classification.voice_consensus,
                "entity": classification.entity_consensus,
                "classification": classification.classification.value,
                "frequency": classification.frequency,
                "scores": {
                    algo_name: res["similarity"]
                    for algo_name, res in classification.to_dict()["results"].items()
                }
            }
            results.append(item)
        return sorted(results, key=lambda x: x["frequency"], reverse=True)
