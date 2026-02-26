"""
Embedding implementations for PortAda S-Index.
Provides a vector representations of text without external dependencies.
"""

import math
import hashlib
from abc import ABC, abstractmethod
from typing import List

class BaseEmbedding(ABC):
    """
    Base class for embedding calculations.
    """
    @abstractmethod
    def get_vector(self, text: str) -> List[float]:
        pass

class CharHashingEmbedding(BaseEmbedding):
    """
    A 'real' implementation of a text vectorizer using the Hashing Trick
    on character n-grams. This is a standard NLP technique for fuzzy
    string matching that doesn't require pre-trained models or external deps.
    """
    def __init__(self, dimensions: int = 128, n_gram: int = 3):
        self.dimensions = dimensions
        self.n_gram = n_gram

    def get_vector(self, text: str) -> List[float]:
        if not text:
            return [0.0] * self.dimensions
        
        vec = [0.0] * self.dimensions
        
        # Slide window for n-grams
        if len(text) < self.n_gram:
            # Fallback to whole text if shorter than n_gram
            ngrams = [text]
        else:
            ngrams = [text[i:i+self.n_gram] for i in range(len(text) - self.n_gram + 1)]
            
        for ngram in ngrams:
            # Deterministic hashing using MD5 (available in stdlib)
            h_hex = hashlib.md5(ngram.encode('utf-8')).hexdigest()
            h_int = int(h_hex, 16)
            vec[h_int % self.dimensions] += 1.0
            
        # L2 Normalization to ensure cosine similarity works correctly
        norm = math.sqrt(sum(x*x for x in vec))
        if norm > 0:
            vec = [x / norm for x in vec]
            
        return vec
