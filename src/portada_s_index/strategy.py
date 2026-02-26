"""
Strategy and Builder patterns for interchangeable similarity algorithms.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Tuple
from .algorithms import (
    levenshtein_ratio,
    levenshtein_ratio_ocr,
    jaro_winkler_similarity,
    ngram_similarity,
    cosine_similarity,
)
from .embeddings import CharHashingEmbedding

class SimilarityAlgorithmStrategy(ABC):
    """
    Base Strategy interface for all similarity algorithms.
    """
    
    @property
    @abstractmethod
    def name(self) -> str:
        """Returns the algorithm's unique name."""
        pass

    def prepare_data(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """
        Prepares the data for calculation.
        For non-embedding algorithms, this simply returns the input dictionary.
        Subclasses requiring embeddings should override this and add a 
        <name>_vector field.
        """
        return d

    @abstractmethod
    def calculate(self, d_prepared_1: Dict[str, Any], d_prepared_2: Dict[str, Any]) -> List[Tuple[Any, Any, float]]:
        """
        Calculates similarity between two prepared dictionaries.
        
        Args:
            d_prepared_1: A dictionary containing at least 'id' and 'citation'. 
                          For embedding algorithms, it must contain <name>_vector.
            d_prepared_2: A dictionary containing at least 'id' and 'voice'.
                          For embedding algorithms, it must contain <name>_vector.
                          
        Returns:
            A list containing a tuple (id1, id2, similarity_index).
            Designed as a list to allow potential one-to-many comparisons
            if adapted in the future, as strictly defined by requirements.
        """
        pass


class LevenshteinRatioStrategy(SimilarityAlgorithmStrategy):
    @property
    def name(self) -> str:
        return "levenshtein_ratio"

    def calculate(self, d_prepared_1: Dict[str, Any], d_prepared_2: Dict[str, Any]) -> List[Tuple[Any, Any, float]]:
        id1 = d_prepared_1.get("id")
        id2 = d_prepared_2.get("id")
        citation = d_prepared_1.get("citation", "")
        voice = d_prepared_2.get("voice", "")
        
        score = levenshtein_ratio(citation, voice)
        return [(id1, id2, score)]


class LevenshteinOcrStrategy(SimilarityAlgorithmStrategy):
    def __init__(self, confusion_cost: float = 0.4):
        self.confusion_cost = confusion_cost

    @property
    def name(self) -> str:
        return "levenshtein_ocr"

    def calculate(self, d_prepared_1: Dict[str, Any], d_prepared_2: Dict[str, Any]) -> List[Tuple[Any, Any, float]]:
        id1 = d_prepared_1.get("id")
        id2 = d_prepared_2.get("id")
        citation = d_prepared_1.get("citation", "")
        voice = d_prepared_2.get("voice", "")
        
        score = levenshtein_ratio_ocr(citation, voice, self.confusion_cost)
        return [(id1, id2, score)]


class JaroWinklerStrategy(SimilarityAlgorithmStrategy):
    def __init__(self, prefix_weight: float = 0.1):
        self.prefix_weight = prefix_weight

    @property
    def name(self) -> str:
        return "jaro_winkler"

    def calculate(self, d_prepared_1: Dict[str, Any], d_prepared_2: Dict[str, Any]) -> List[Tuple[Any, Any, float]]:
        id1 = d_prepared_1.get("id")
        id2 = d_prepared_2.get("id")
        citation = d_prepared_1.get("citation", "")
        voice = d_prepared_2.get("voice", "")
        
        score = jaro_winkler_similarity(citation, voice, self.prefix_weight)
        return [(id1, id2, score)]


class NgramStrategy(SimilarityAlgorithmStrategy):
    def __init__(self, n: int = 2):
        self.n = n

    @property
    def name(self) -> str:
        return f"ngram_{self.n}"

    def calculate(self, d_prepared_1: Dict[str, Any], d_prepared_2: Dict[str, Any]) -> List[Tuple[Any, Any, float]]:
        id1 = d_prepared_1.get("id")
        id2 = d_prepared_2.get("id")
        citation = d_prepared_1.get("citation", "")
        voice = d_prepared_2.get("voice", "")
        
        score = ngram_similarity(citation, voice, self.n)
        return [(id1, id2, score)]



class Text2VecStrategy(SimilarityAlgorithmStrategy):
    """
    Algorithm based on text embeddings.
    Adds a vector field to the data using a real Character Hashing implementation.
    """
    def __init__(self, dimensions: int = 128, n_gram: int = 3):
        self.embedding_model = CharHashingEmbedding(dimensions=dimensions, n_gram=n_gram)

    @property
    def name(self) -> str:
        return "text2vec"

    def prepare_data(self, d: Dict[str, Any]) -> Dict[str, Any]:
        """
        Adds the embedding vector to the dictionary using a real calculation.
        """
        text = d.get("citation") or d.get("voice") or ""
        vector_field = f"{self.name}_vector"
        
        # Only compute if not already present
        if vector_field not in d:
            d = d.copy()
            d[vector_field] = self.embedding_model.get_vector(text)
        
        return d

    def calculate(self, d_prepared_1: Dict[str, Any], d_prepared_2: Dict[str, Any]) -> List[Tuple[Any, Any, float]]:
        id1 = d_prepared_1.get("id")
        id2 = d_prepared_2.get("id")
        
        vector_field = f"{self.name}_vector"
        v1 = d_prepared_1.get(vector_field)
        v2 = d_prepared_2.get(vector_field)
        
        if v1 is None or v2 is None:
            # Fallback if vectors are missing (should not happen with prepare_data)
            return [(id1, id2, 0.0)]
        
        score = cosine_similarity(v1, v2)
        return [(id1, id2, score)]

class AlgorithmBuilder:
    """
    Builder pattern implementation for constructing algorithm strategies.
    """
    
    _registry = {
        "levenshtein_ratio": LevenshteinRatioStrategy,
        "levenshtein_ocr": LevenshteinOcrStrategy,
        "jaro_winkler": JaroWinklerStrategy,
        "ngram_2": lambda **kwargs: NgramStrategy(n=2, **kwargs),
        "ngram_3": lambda **kwargs: NgramStrategy(n=3, **kwargs),
        "text2vec": Text2VecStrategy,
    }

    @classmethod
    def register(cls, name: str, strategy_class):
        """Registers a new strategy class."""
        cls._registry[name] = strategy_class

    @classmethod
    def build(cls, algorithm_name: str, **kwargs) -> SimilarityAlgorithmStrategy:
        """
        Instantiates an algorithm strategy by name.
        """
        if algorithm_name not in cls._registry:
            raise ValueError(f"Unknown algorithm name: {algorithm_name}")
            
        strategy_constructor = cls._registry[algorithm_name]
        return strategy_constructor(**kwargs)

